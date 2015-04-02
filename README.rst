======
sqlize
======

Sqlize is a SQL query builder for Python. It's main goals are:

- speed: because fast is good
- transparency: do not hide the true nature of SQL
- mutability: we should be able to mutate the query

This library is primarily developed for use with SQLite and no efforts have
been invested into testing or using with other database backends.

Installation
============

Sqlize can be installed using ``pip`` or ``easy_install`` as usual::

    pip install sqlize


Introduction (quick tutorial)
=============================

This section will provide a brief introduction to sqlize. The examples are all
doctested, so rest assured that they work as expected.

The basic concept is to instantiate an object representing some type of query,
optionally manipulate attributes on it to fine-tune the clauses, and finally
convert the query into SQL string by coercing it into string.

Note that the queries are meant to be used with placeholder values, and **no
quoting is performed by sqlize**. The generated SQL strings are intended to be
used with ``sqlite3.Cursor.execute()``, and similar methods.

A basic select looks like this::

    >>> import sqlize as sql
    >>> q = sql.Select('*', sets='foo')

Note that we call tables 'sets' to avoid the clash with Python's ``from``
keyword.

To convert the query to SQL, we simply coerce it into a ``str``::

    >>> str(q)
    'SELECT * FROM foo;'

You can select multiple things::

    >>> str(sql.Select(['foo', 'bar'], sets='foo'))
    'SELECT foo, bar FROM foo;'

You can also select from mutliple tables::

    >>> str(sql.Select('*', sets=['foo', 'bar']))
    'SELECT * FROM foo , bar;'


If you want to restrict your select, all common clauses are available::

    >>> str(sql.Select('*', ['foo', 'bar'], where='a = ?', group='foo',
    ...                order='-bar', limit=10, offset=20))
    'SELECT * FROM foo , bar WHERE a = ? GROUP BY foo ORDER BY bar DESC LIMIT 10 OFFSET 20;'


So far it looks like a rather complicated way of writing SQL. The real power,
though, comes from the fact that every aspect of the query object can be
tweaked.

    >>> q = sql.Select()
    >>> str(q)
    'SELECT *;'
    >>> q.what = 'foo'
    >>> q.sets = 'this'
    >>> q.sets.join('other', sql.INNER)
    <sqlize.builder.From object at ...>
    >>> q.where = 'bar = ?'
    >>> q.limit = 2
    >>> str(q)
    'SELECT foo FROM this INNER JOIN other WHERE bar = ? LIMIT 2;'

Now let's take a look at individual clauses. 

The ``where`` attribute is represented by a ``sqlize.builder.Where`` object,
which supports a few handy operators for adding conditions::

    >>> q = sql.Select()
    >>> q.where = 'foo = ?'
    >>> q.where &= 'bar = ?'
    >>> q.where |= 'foo = bar'
    >>> str(q)
    'SELECT * WHERE foo = ? AND bar = ? OR foo = bar;'

The ``&=`` and ``|=`` have method aliases. Main advantage is that methods are
chainable. The above example can be rewritten as::

    >>> q = sql.Select()
    >>> q.where = 'foo = ?'
    >>> q.where.and_('bar = ?').or_('foo = bar')
    <sqlize.builder.Where object at ...>
    >>> str(q)
    'SELECT * WHERE foo = ? AND bar = ? OR foo = bar;'

Note the underscore. We can't use method names that look like built-in
operators.

The ``sets`` attribute is represented by a ``sqlize.builder.From`` object. It
has a few utility methods which you can use to add and join other tables::

    >>> q = sql.Select()
    >>> q.sets = 'foo'
    >>> q.sets.append('bar')
    <sqlize.builder.From object at ...>
    >>> str(q)
    'SELECT * FROM foo , bar;'

    >>> q = sql.Select()
    >>> q.sets = 'foo'
    >>> q.sets.join('bar', sql.NATURAL)
    <sqlize.builder.From object at ...>
    >>> str(q)
    'SELECT * FROM foo NATURAL JOIN bar;'

There is no direct support for aggregates. Instead, you write raw SQL.::

    >>> q = sql.Select('COUNT(*) as count', sets='foo', group='bar')
    >>> str(q)
    'SELECT COUNT(*) as count FROM foo GROUP BY bar;'

This is intentional. We wanted sqlize to be as true to SQL as possible, and not
get in your way.

Apart from selecting, sqlize supports inserts, updates, deletion, and
replacement.

Inserts look like this:

    >>> q = sql.Insert('foo', '?, ?, ?')
    >>> str(q)
    'INSERT INTO foo VALUES (?, ?, ?);'

You can also specify columns:

    >>> q = sql.Insert('foo', '?, ?, ?', ('foo', 'bar', 'baz'))
    >>> str(q)
    'INSERT INTO foo (foo, bar, baz) VALUES (?, ?, ?);'

If you omit the values, the query will contain named placeholders:

    >>> q = sql.Insert('foo', cols=('foo', 'bar', 'baz'))
    >>> str(q)
    'INSERT INTO foo (foo, bar, baz) VALUES (:foo, :bar, :baz);'

Replacing is exactly the same as inserting, but uses ``Replace`` class
instead::

    >>> q = sql.Replace('foo', '?, ?, ?')
    >>> str(q)
    'REPLACE INTO foo VALUES (?, ?, ?);'

The update query looks like this::

    >>> q = sql.Update('foo', 'bar = ?', baz='?')
    >>> str(q)
    'UPDATE foo SET baz = ? WHERE bar = ?;'

The second argument is the same as ``where`` in ``Select()``. It can be
modified after initialization::

    >>> q = sql.Update('foo', baz='?')
    >>> q.where &= 'foo = ?'
    >>> q.where |= 'bar = ?'
    >>> str(q)
    'UPDATE foo SET baz = ? WHERE foo = ? OR bar = ?;'

Any keyword arguments passed to ``Update()`` will be converted to ``SET``
clauses.

Deleting rows can be accomplished using the ``Delete()`` class.

    >>> q = sql.Delete('foo', 'bar = ?')
    >>> str(q)
    'DELETE FROM foo WHERE bar = ?;'

As with ``Update()``, the second argument is a ``where`` clause, and can be
manipulated.

More docs, please!
==================

Unfortunately, there are currently no docs apart from this introduction. I hope
that codebase is not too difficult to follow, though, so if you can't wait, you
can peek into the source files.

Comparison to other libraries
=============================

TODO

Reporting bugs
==============

TODO
