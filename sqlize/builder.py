"""
builder.py: Helpers for working with databases

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

try:
    basestring = basestring
except NameError:
    basestring = (str, bytes)


NATURAL = 'NATURAL'
INNER = 'INNER'
CROSS = 'CROSS'
OUTER = 'OUTER'
LEFT_OUTER = 'LEFT OUTER'
JOIN = 'JOIN'


def is_seq(obj):
    """ Returns True if object is not a string but is iterable """
    if not hasattr(obj, '__iter__'):
        return False
    if isinstance(obj, basestring):
        return False
    return True


def sqlarray(n):
    if not n:
        return ''
    if is_seq(n):
        n = len(n)
    return '({})'.format(', '.join('?' * n))


def sqlin(col, n):
    if not n:
        return ''
    return '{} IN {}'.format(col, sqlarray(n))


class SQL(object):
    sqlarray = sqlarray
    sqlin = sqlin

    def serialize(self):
        raise NotImplementedError('Must be implemented by expression')

    def __str__(self):
        return self.serialize()


class BaseClause(SQL):
    keyword = None

    def __init__(self, *parts, **kwargs):
        self.parts = list(parts)

    def __len__(self):
        return len(self.parts)

    def __nonzero__(self):
        return len(self.parts) > 0


class Clause(BaseClause):
    keyword = None
    default_connector = None
    null_connector = None

    def __init__(self, *parts, **kwargs):
        connector = kwargs.pop('connector', self.default_connector)
        self.parts = []
        parts = [p for p in parts if p]
        try:
            self.parts.append((None, parts[0]))
        except IndexError:
            return
        for p in parts[1:]:
            self.parts.append((connector, p))

    def serialize_part(self, connector, part):
        if connector:
            part = '{} {}'.format(connector, part)
        return part + ' '

    def serialize(self):
        if not self.parts:
            return ''
        sql = self.keyword + ' '
        for connector, part in self.parts:
            sql += self.serialize_part(connector, part)
        return sql.rstrip()

    def __bool__(self):
        return len(self.parts) > 0

    def __len__(self):
        return len(self.parts)


class From(Clause):
    keyword = 'FROM'
    default_connector = ','

    NATURAL = NATURAL
    INNER = INNER
    CROSS = CROSS
    OUTER = OUTER
    LEFT_OUTER = LEFT_OUTER
    JOIN = JOIN

    def __init__(self, *args, **kwargs):
        join = kwargs.pop('join', None)
        if join:
            kwargs['connector'] = '{} JOIN'.format(join)
        super(From, self).__init__(*args, **kwargs)

    def append(self, table):
        self.parts.append((self.default_connector, table))
        return self

    def join(self, table, kind=None, natural=False, on=None, using=[]):
        j = []
        if natural:
            j.append(self.NATURAL)
        if kind:
            j.append(kind)
        j.append(self.JOIN)
        if on:
            table += ' ON {}'.format(on)
        elif using:
            if is_seq(using):
                using = ', '.join(using)
            table += ' USING ({})'.format(using)
        self.parts.append((' '.join(j), table))
        return self

    def inner_join(self, table, natural=False):
        return self.join(table, self.INNER, natural)

    def outer_join(self, table, natural=False):
        return self.join(table, self.OUTER, natural)

    def natural_join(self, table):
        return self.join(table, None, True)


class Where(Clause):
    keyword = 'WHERE'
    default_connector = 'AND'

    AND = 'AND'
    OR = 'OR'

    def __init__(self, *args, **kwargs):
        if kwargs.pop('use_or', False):
            kwargs['connector'] = self.OR
        super(Where, self).__init__(*args, **kwargs)

    def and_(self, condition):
        if not self.parts:
            self.parts.append((None, condition))
        else:
            self.parts.append((self.AND, condition))
        return self

    def or_(self, condition):
        if not self.parts:
            self.parts.append((None, condition))
        else:
            self.parts.append((self.OR, condition))
        return self

    __iand__ = and_
    __iadd__ = and_
    __ior__ = or_


class Group(BaseClause):
    keyword = 'GROUP BY'

    def __init__(self, *parts, **kwargs):
        self.having = kwargs.pop('having', None)
        self.parts = parts

    def serialize(self):
        if not self.parts:
            return ''
        sql = self.keyword + ' '
        sql += ', '.join(self.parts)
        if self.having:
            sql += ' HAVING {}'.format(self.having)
        return sql


class Order(BaseClause):
    keyword = 'ORDER BY'

    def __init__(self, *parts):
        self.parts = list(parts)

    def asc(self, term):
        self.parts.append('+{}'.format(term))
        return self

    def desc(self, term):
        self.parts.append('-{}'.format(term))
        return self

    def __iadd__(self, term):
        return self.asc(term)

    def __isub__(self, term):
        return self.desc(term)

    def _convert_term(self, term):
        if term.startswith('-'):
            return '{} DESC'.format(term[1:])
        elif term.startswith('+'):
            return '{} ASC'.format(term[1:])
        return '{} ASC'.format(term)

    def serialize(self):
        if not self.parts:
            return ''
        sql = self.keyword + ' '
        sql += ', '.join((self._convert_term(t) for t in self.parts))
        return sql


class Limit(SQL):
    def __init__(self, limit=None, offset=None):
        self.limit = limit
        self.offset = offset

    def serialize(self):
        if not self.limit:
            return ''
        sql = 'LIMIT {}'.format(self.limit)
        if not self.offset:
            return sql
        sql += ' OFFSET {}'.format(self.offset)
        return sql

    def __len__(self):
        return int(self.limit) if self.limit else 0

    def __bool__(self):
        return len(self) > 0


class Statement(SQL):
    lists = []
    ints = []
    clauses = {}

    def __setattr__(self, attr, val):
        if attr in self.lists:
            return object.__setattr__(self, attr, self._get_list(val))
        if attr in self.ints:
            return object.__setattr__(self, attr, self._get_int(val))
        if attr in self.clauses:
            return object.__setattr__(
                self, attr, self._get_clause(val, self.clauses[attr]))
        object.__setattr__(self, attr, val)

    @staticmethod
    def _get_clause(val, sql_class):
        if hasattr(val, 'serialize'):
            return val
        if val is None:
            return sql_class()
        if hasattr(val, 'get'):
            return sql_class(**val)
        if is_seq(val):
            return sql_class(*val)
        return sql_class(val)

    @staticmethod
    def _get_list(val):
        if not val:
            return []
        if not is_seq(val):
            return [val]
        return list(val)

    @staticmethod
    def _get_int(val):
        if not val:
            return None
        return int(val)


class Select(Statement):
    lists = ('what',)
    ints = ('limit', 'offset')
    clauses = {
        'sets': From,
        'where': Where,
        'group': Group,
        'order': Order,
        'limit': int,
    }

    def __init__(self, what=['*'], sets=None, where=None, group=None,
                 order=None, limit=None, offset=None):
        self.what = what
        self.sets = sets
        self.where = where
        self.group = group
        self.order = order
        self.limit = limit
        self.offset = offset

    def serialize(self):
        sql = 'SELECT '
        sql += ', '.join(self._what)
        if self.sets:
            sql += ' {}'.format(self._from)
        if self.where:
            sql += ' {}'.format(self._where)
        if self.group:
            sql += ' {}'.format(self._group)
        if self.order:
            sql += ' {}'.format(self._order)
        if self.limit:
            sql += ' {}'.format(self._limit)
        return sql + ';'

    @property
    def _what(self):
        return self._get_list(self.what)

    @property
    def _from(self):
        return self._get_clause(self.sets, From)

    @property
    def _where(self):
        return self._get_clause(self.where, Where)

    @property
    def _group(self):
        return self._get_clause(self.group, Group)

    @property
    def _order(self):
        return self._get_clause(self.order, Order)

    @property
    def _limit(self):
        return Limit(self.limit, self.offset)


class Update(Statement):
    clauses = {'where': Where}

    def __init__(self, table, where=None, **kwargs):
        self.table = table
        self.set_args = kwargs
        self.where = where

    @property
    def _where(self):
        return self._get_clause(self.where, Where)

    def serialize(self):
        sql = 'UPDATE {} SET '.format(self.table)
        sql += ', '.join(('{} = {}'.format(col, p)
                          for col, p in self.set_args.items()))
        if self.where:
            sql += ' {}'.format(self._where)
        return sql + ';'


class Delete(Statement):
    clauses = {'where': Where}

    def __init__(self, table, where=None):
        self.table = table
        self.where = where

    def serialize(self):
        sql = 'DELETE FROM {}'.format(self.table)
        if self.where:
            sql += ' {}'.format(self._where)
        return sql + ';'

    @property
    def _where(self):
        return self._get_clause(self.where, Where)


class Insert(Statement):
    keyword = 'INSERT INTO'

    def __init__(self, table, vals=None, cols=None):
        self.table = table
        self.vals = vals
        self.cols = cols
        if not any([vals, cols]):
            raise ValueError('Either vals or cols must be specified')

    def serialize(self):
        sql = '{} {}'.format(self.keyword, self.table)
        if self.cols:
            sql += ' {}'.format(self._cols)
        sql += ' VALUES {}'.format(self._vals)
        return sql + ';'

    @property
    def _vals(self):
        if not self.vals:
            return self._get_sqlarray((':' + c for c in self.cols))
        return self._get_sqlarray(self.vals)

    @property
    def _cols(self):
        return self._get_sqlarray(self.cols)

    @staticmethod
    def _get_sqlarray(vals):
        if is_seq(vals):
            return '({})'.format(', '.join(vals))
        if vals.startswith('(') and vals.endswith(')'):
            return vals
        return '({})'.format(vals)


class Replace(Insert):
    keyword = 'REPLACE INTO'
