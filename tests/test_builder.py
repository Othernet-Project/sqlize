import sqlize as mod

MOD = mod.__name__


def test_non_str_seq():
    assert mod.is_seq('a') is False
    assert mod.is_seq([]) is True
    assert mod.is_seq(tuple()) is True
    assert mod.is_seq((i for i in range(1))) is True
    assert mod.is_seq({}) is True
    assert mod.is_seq(True) is False


def test_sqlarray():
    assert mod.sqlarray(2) == '(?, ?)'


def test_sqlarray_zero():
    assert mod.sqlarray(0) == ''


def test_sqlarray_list():
    assert mod.sqlarray(['foo', 'bar', 'baz']) == '(?, ?, ?)'


def test_sqlin():
    assert mod.sqlin('foo', 4) == 'foo IN (?, ?, ?, ?)'


def test_sqlin_zero():
    assert mod.sqlin('foo', 0) == ''


def test_from():
    sql = mod.From('foo')
    assert str(sql) == 'FROM foo'


def test_from_table_list():
    sql = mod.From('foo', 'bar')
    assert str(sql) == 'FROM foo , bar'


def test_from_append():
    sql = mod.From('foo')
    sql.append('bar')
    assert str(sql) == 'FROM foo , bar'


def test_from_append_chain():
    sql = mod.From('foo')
    sql.append('bar').append('baz')
    assert str(sql) == 'FROM foo , bar , baz'


def test_from_joins():
    sql = mod.From('foo', 'bar', join=mod.From.INNER)
    assert str(sql) == 'FROM foo INNER JOIN bar'


def test_form_add_join():
    sql = mod.From('foo')
    sql.join('bar')
    assert str(sql) == 'FROM foo JOIN bar'


def test_from_add_join_kind():
    sql = mod.From('foo')
    sql.join('bar', mod.From.OUTER)
    assert str(sql) == 'FROM foo OUTER JOIN bar'


def test_from_add_join_natural():
    sql = mod.From('foo')
    sql.join('bar', natural=True)
    assert str(sql) == 'FROM foo NATURAL JOIN bar'


def test_from_add_join_natural_kind():
    sql = mod.From('foo')
    sql.join('bar', mod.From.CROSS, natural=True)
    assert str(sql) == 'FROM foo NATURAL CROSS JOIN bar'


def test_from_add_join_on():
    sql = mod.From('foo')
    sql.join('bar', on='foo.test = bar.footest')
    assert str(sql) == 'FROM foo JOIN bar ON foo.test = bar.footest'


def test_from_add_join_on_with_subquery():
    sql = mod.From('foo')
    subsql = mod.Select('bar')
    sql.join(subsql, on='foo.test = bar.footest')
    assert str(sql) == 'FROM foo JOIN (SELECT bar) ON foo.test = bar.footest'


def test_from_add_join_using():
    sql = mod.From('foo')
    sql.join('bar', using='test_id')
    assert str(sql) == 'FROM foo JOIN bar USING (test_id)'


def test_from_add_join_using_with_subquery():
    sql = mod.From('foo')
    subsql = mod.Select('bar')
    sql.join(subsql, using='test_id')
    assert str(sql) == 'FROM foo JOIN (SELECT bar) USING (test_id)'


def test_from_add_join_using_multiple():
    sql = mod.From('foo')
    sql.join('bar', using=['test_id', 'something'])
    assert str(sql) == 'FROM foo JOIN bar USING (test_id, something)'


def test_from_add_join_on_and_using():
    sql = mod.From('foo')
    sql.join('bar', on='foo.bar_id = bar.id', using='bar_id')
    assert str(sql) == 'FROM foo JOIN bar ON foo.bar_id = bar.id'


def test_empty_from():
    sql = mod.From()
    assert str(sql) == ''


def test_from_bool():
    sql = mod.From()
    assert not sql
    sql = mod.From('foo')
    assert sql


def test_where():
    sql = mod.Where('foo = ?', 'bar = ?')
    assert str(sql) == 'WHERE foo = ? AND bar = ?'


def test_where_or():
    sql = mod.Where('foo = ?', 'bar = ?', use_or=True)
    assert str(sql) == 'WHERE foo = ? OR bar = ?'


def test_where_and_method():
    sql = mod.Where('foo = ?')
    sql.and_('bar = ?')
    assert str(sql) == 'WHERE foo = ? AND bar = ?'


def test_where_and_operator():
    sql = mod.Where('foo = ?')
    sql &= 'bar = ?'
    assert str(sql) == 'WHERE foo = ? AND bar = ?'


def test_where_and_with_first_condition():
    sql = mod.Where()
    sql &= 'foo = ?'
    assert str(sql) == 'WHERE foo = ?'


def test_where_with_empty_str():
    sql = mod.Where('')
    assert str(sql) == ''


def test_and_alias():
    sql = mod.Where('foo = ?')
    sql += 'bar = ?'
    assert str(sql) == 'WHERE foo = ? AND bar = ?'


def test_where_or_method():
    sql = mod.Where('foo = ?')
    sql.or_('bar = ?')
    assert str(sql) == 'WHERE foo = ? OR bar = ?'


def test_where_or_operator():
    sql = mod.Where('foo = ?')
    sql |= 'bar = ?'
    assert str(sql) == 'WHERE foo = ? OR bar = ?'


def test_where_or_with_first_condition():
    sql = mod.Where()
    sql |= 'foo = ?'
    assert str(sql) == 'WHERE foo = ?'


def test_empty_where():
    sql = mod.Where()
    assert str(sql) == ''


def test_where_bool():
    sql = mod.Where()
    assert not sql
    sql = mod.Where('foo = ?')
    assert sql


def test_group_by():
    sql = mod.Group('foo')
    assert str(sql) == 'GROUP BY foo'


def test_group_by_multi():
    sql = mod.Group('foo', 'bar')
    assert str(sql) == 'GROUP BY foo, bar'


def test_group_by_having():
    sql = mod.Group('foo', having='bar > 12')
    assert str(sql) == 'GROUP BY foo HAVING bar > 12'


def test_group_by_empty():
    sql = mod.Group()
    assert str(sql) == ''


def test_group_by_bool():
    sql = mod.Group()
    assert not sql
    sql = mod.Group('foo')
    assert sql


def test_order():
    sql = mod.Order('foo')
    assert str(sql) == 'ORDER BY foo ASC'


def test_order_asc_alias():
    sql = mod.Order('+foo')
    assert str(sql) == 'ORDER BY foo ASC'


def test_order_desc():
    sql = mod.Order('-foo')
    assert str(sql) == 'ORDER BY foo DESC'


def test_order_multi():
    sql = mod.Order('foo', '-bar')
    assert str(sql) == 'ORDER BY foo ASC, bar DESC'


def test_order_add_asc():
    sql = mod.Order('foo')
    sql.asc('bar')
    assert str(sql) == 'ORDER BY foo ASC, bar ASC'


def test_order_add_desc():
    sql = mod.Order('foo')
    sql.desc('bar')
    assert str(sql) == 'ORDER BY foo ASC, bar DESC'


def test_order_asc_operator():
    sql = mod.Order('foo')
    sql += 'bar'
    assert str(sql) == 'ORDER BY foo ASC, bar ASC'


def test_order_desc_operator():
    sql = mod.Order('foo')
    sql -= 'bar'
    assert str(sql) == 'ORDER BY foo ASC, bar DESC'


def test_order_empty():
    sql = mod.Order()
    assert str(sql) == ''


def test_order_bool():
    sql = mod.Order()
    assert not sql
    sql = mod.Order('foo')
    assert sql


def test_limit():
    sql = mod.Limit(1)
    assert str(sql) == 'LIMIT 1'


def test_limit_offset():
    sql = mod.Limit(1, 2)
    assert str(sql) == 'LIMIT 1 OFFSET 2'


def test_offset_only():
    sql = mod.Limit(offset=2)
    assert str(sql) == ''


def test_empty_limit():
    sql = mod.Limit()
    assert str(sql) == ''


def test_limit_bool():
    sql = mod.Limit()
    assert not sql
    sql = mod.Limit(1)
    assert sql
    sql = mod.Limit(offset=2)
    assert not sql


def test_select():
    sql = mod.Select()
    assert str(sql) == 'SELECT *;'


def test_select_as_subquery():
    sql = mod.Select()
    assert sql.as_subquery() == '(SELECT *)'


def test_select_as_subquery_alias():
    sql = mod.Select()
    assert sql.as_subquery(alias='foo') == '(SELECT *) AS foo'


def test_select_what_iter():
    sql = mod.Select(['foo', 'bar'])
    assert str(sql) == 'SELECT foo, bar;'


def test_select_subquery():
    subsql = mod.Select('foo')
    sql = mod.Select(['bar', subsql])
    assert str(sql) == 'SELECT bar, (SELECT foo);'


def test_select_sbuquery_alias():
    subsql = mod.Select('foo', alias='baz')
    sql = mod.Select(['bar', subsql])
    assert str(sql) == 'SELECT bar, (SELECT foo) AS baz;'


def test_select_sbuquery_alias_property():
    subsql = mod.Select('foo')
    subsql.alias = 'baz'
    sql = mod.Select(['bar', subsql])
    assert str(sql) == 'SELECT bar, (SELECT foo) AS baz;'


def test_select_from():
    sql = mod.Select('*', 'foo')
    assert str(sql) == 'SELECT * FROM foo;'


def test_select_from_multiple():
    sql = mod.Select('*', ['foo', 'bar'])
    assert str(sql) == 'SELECT * FROM foo , bar;'


def test_select_from_subquery():
    subsql = mod.Select('foo')
    sql = mod.Select('*', ['bar', subsql])
    assert str(sql) == 'SELECT * FROM bar , (SELECT foo);'


def test_select_from_with_cls():
    sql = mod.Select('*', mod.From('foo', 'bar', join='CROSS'))
    assert str(sql) == 'SELECT * FROM foo CROSS JOIN bar;'


def test_select_tables_attrib():
    sql = mod.Select(sets='foo')
    sql.sets.join('bar', mod.From.CROSS)
    assert str(sql) == 'SELECT * FROM foo CROSS JOIN bar;'


def test_select_tables_attrib_submodule():
    subsql = mod.Select('bar')
    sql = mod.Select(sets='foo')
    sql.sets.join(subsql)
    assert str(sql) == 'SELECT * FROM foo JOIN (SELECT bar);'


def test_select_where():
    sql = mod.Select('*', where='a = b')
    assert str(sql) == 'SELECT * WHERE a = b;'


def test_select_where_multiple():
    sql = mod.Select('*', where=['a = b', 'c = d'])
    assert str(sql) == 'SELECT * WHERE a = b AND c = d;'


def test_select_where_cls():
    sql = mod.Select('*', where=mod.Where('a = b', 'c = d', use_or=True))
    assert str(sql) == 'SELECT * WHERE a = b OR c = d;'


def test_select_where_attrib():
    sql = mod.Select(where='a = b')
    sql.where |= 'c = d'
    assert str(sql) == 'SELECT * WHERE a = b OR c = d;'


def test_select_group_by():
    sql = mod.Select('COUNT(*) AS count', group='foo')
    assert str(sql) == 'SELECT COUNT(*) AS count GROUP BY foo;'


def test_select_group_by_multiple():
    sql = mod.Select('COUNT(*) AS count', group=['foo', 'bar'])
    assert str(sql) == 'SELECT COUNT(*) AS count GROUP BY foo, bar;'


def test_select_group_by_cls():
    sql = mod.Select('COUNT(*) AS count', group=mod.Group('foo'))
    assert str(sql) == 'SELECT COUNT(*) AS count GROUP BY foo;'


def test_select_group_attr():
    sql = mod.Select('COUNT(*) AS count', group='foo')
    sql.group.having = 'bar > 12'
    assert str(sql) == 'SELECT COUNT(*) AS count GROUP BY foo HAVING bar > 12;'


def test_select_order():
    sql = mod.Select(order='foo')
    assert str(sql) == 'SELECT * ORDER BY foo ASC;'


def test_select_order_multiple():
    sql = mod.Select(order=['foo', '-bar'])
    assert str(sql) == 'SELECT * ORDER BY foo ASC, bar DESC;'


def test_select_order_cls():
    sql = mod.Select(order=mod.Order('foo'))
    assert str(sql) == 'SELECT * ORDER BY foo ASC;'


def test_select_order_attr():
    sql = mod.Select(order='foo')
    sql.order.desc('bar')
    assert str(sql) == 'SELECT * ORDER BY foo ASC, bar DESC;'


def test_select_limit():
    sql = mod.Select(limit=1)
    assert str(sql) == 'SELECT * LIMIT 1;'


def test_select_limit_offset():
    sql = mod.Select(limit=1, offset=20)
    assert str(sql) == 'SELECT * LIMIT 1 OFFSET 20;'


def test_select_offset_without_limit():
    sql = mod.Select(offset=20)
    assert str(sql) == 'SELECT *;'


def test_select_limit_attr():
    sql = mod.Select()
    sql.limit = 1
    assert str(sql) == 'SELECT * LIMIT 1;'


def test_select_offset_attr():
    sql = mod.Select(limit=1)
    sql.offset = 20
    assert str(sql) == 'SELECT * LIMIT 1 OFFSET 20;'


def test_update():
    sql = mod.Update('foo', foo='?', bar='?')
    assert str(sql) in [
        'UPDATE foo SET foo = ?, bar = ?;',
        'UPDATE foo SET bar = ?, foo = ?;'
    ]


def test_update_where():
    sql = mod.Update('foo', foo='?', where='bar = ?')
    assert str(sql) == 'UPDATE foo SET foo = ? WHERE bar = ?;'


def test_update_where_multi():
    sql = mod.Update('foo', foo='?', where=['bar = ?', 'baz = ?'])
    assert str(sql) == 'UPDATE foo SET foo = ? WHERE bar = ? AND baz = ?;'


def test_update_where_attr():
    sql = mod.Update('foo', foo='?', where='bar = ?')
    sql.where += 'baz = ?'
    assert str(sql) == 'UPDATE foo SET foo = ? WHERE bar = ? AND baz = ?;'


def test_delete():
    sql = mod.Delete('foo')
    assert str(sql) == 'DELETE FROM foo;'


def test_delete_where():
    sql = mod.Delete('foo', where='foo = ?')
    assert str(sql) == 'DELETE FROM foo WHERE foo = ?;'


def test_delete_where_multi():
    sql = mod.Delete('foo', where=['foo = ?', 'bar = ?'])
    assert str(sql) == 'DELETE FROM foo WHERE foo = ? AND bar = ?;'


def test_delete_where_attrib():
    sql = mod.Delete('foo', where='foo = ?')
    sql.where += 'bar = ?'
    assert str(sql) == 'DELETE FROM foo WHERE foo = ? AND bar = ?;'


def test_delete_empty_where():
    sql = mod.Delete('foo', where='')
    assert str(sql) == 'DELETE FROM foo;'


def test_insert():
    sql = mod.Insert('foo', vals=mod.sqlarray(3))
    assert str(sql) == 'INSERT INTO foo VALUES (?, ?, ?);'


def test_insert_list():
    sql = mod.Insert('foo', vals=[':foo', ':bar', ':baz'])
    assert str(sql) == 'INSERT INTO foo VALUES (:foo, :bar, :baz);'


def test_insert_naked_vals():
    sql = mod.Insert('foo', vals=':foo, :bar, :baz')
    assert str(sql) == 'INSERT INTO foo VALUES (:foo, :bar, :baz);'


def test_insert_with_cols():
    sql = mod.Insert('foo', cols=['foo', 'bar'], vals=':foo, :bar')
    assert str(sql) == 'INSERT INTO foo (foo, bar) VALUES (:foo, :bar);'


def test_inset_without_vals():
    sql = mod.Insert('foo', cols=['foo', 'bar'])
    assert str(sql) == 'INSERT INTO foo (foo, bar) VALUES (:foo, :bar);'


def test_insert_withot_vals_and_cols():
    try:
        mod.Insert('foo')
        assert False, 'Expected to raise'
    except ValueError:
        pass


def test_replace():
    sql = mod.Replace('foo', ':foo, :bar')
    assert str(sql) == 'REPLACE INTO foo VALUES (:foo, :bar);'
