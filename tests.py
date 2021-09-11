import unittest
import pickle
import json
from dotdict.dotdict import dotdict


class DotDictTestCase(unittest.TestCase):

    def setUp(self):
        self.dict_ex = dict(
            a = 1,
            b = 2,
            c = dict(
                d = 3,
                e = 4,
                f = dict(
                    g = 5,
                    h = 6
                )
            )
        )
        self.attrdict_ex = dotdict(self.dict_ex)
        self.keywords = {
            "clear", "copy", "fromkeys", "get", "items", "keys",
            "pop", "popitem", "setdefault", "update", "values", "to_dict"
        }

    def test_from_dict(self):
        d = dict(a = 1, b = dict(c = 2))
        a = dotdict(d)
        self.assertEqual(a.a, d['a'])
        self.assertEqual(a.b, d['b'])
        self.assertEqual(a.b.c, d['b']['c'])

    def test_nested_list(self):
        d = dict(a = 1, b = [2, dict(c = 3)])
        a = dotdict(d)
        self.assertEqual(a.b[1].c, 3)

    def test_nested_tuple(self):
        d = dict(a = 1, b = (2, dict(c = 3)))
        a = dotdict(d)
        self.assertEqual(a.b[1].c, 3)

    def test_subclasses_dict(self):
        class A(dict):
            pass
        d = dict(a = 1, b = A(c = 2))
        a = dotdict(d)
        self.assertRaises(AttributeError, lambda m: m.c, a.b)

    def test_subclasses_tuple(self):
        class A(tuple):
            pass
        d = dict(a = 1, b = A((2, {'c': 3})))
        a = dotdict(d)
        self.assertRaises(AttributeError, lambda m: m.c, a.b[1])

    def test_subclasses_list(self):
        class A(list):
            pass
        d = dict(a = 1, b = A((2, {'c': 3})))
        a = dotdict(d)
        self.assertRaises(AttributeError, lambda m: m.c, a.b[1])

    def test_to_dict_dict(self):
        d = dotdict(a = 1, b = dict(c = 2)).to_dict()
        self.assertRaises(AttributeError, lambda m: m.c, d['b'])

    def test_to_dict_list(self):
        d = dotdict(a = 1, b = [1, dict(c = 2)]).to_dict()
        self.assertRaises(AttributeError, lambda m: m.c, d['b'][1])

    def test_to_dict_tuple(self):
        d = dotdict(a = 1, b = (1, dict(c = 2))).to_dict()
        self.assertRaises(AttributeError, lambda m: m.c, d['b'][1])

    def test_isinstance(self):
        self.assertTrue(isinstance(self.attrdict_ex, dict))

    def test_hasattr(self):
        self.assertTrue(hasattr(self.attrdict_ex, 'a'))

    def test_hasattr_methods(self):
        for k in self.keywords:
            self.assertTrue(hasattr(self.attrdict_ex, k))

    def test_dict_comparison(self):
        self.assertEqual(self.attrdict_ex, self.dict_ex)

    def test_str(self):
        d = dotdict(a = 42, b = dict(c = 69))
        self.assertEqual(str(d), "attrdict({'a': 42, 'b': attrdict({'c': 69})})")

    def test_pickle(self):
        ref = dotdict(a = 42, b = dict(c = 69))
        pkl = pickle.dumps(ref)
        rec = pickle.loads(pkl)
        self.assertEqual(rec, ref)

    def test_json(self):
        ref = dotdict(a = 42, b = dict(c = 69))
        jsn = json.dumps(ref)
        rec = json.loads(jsn)
        self.assertEqual(rec, ref)

    def test_pyyaml(self):
        d = dotdict(a = 42, b = dict(c = 69))
        try:
            import yaml
            s = yaml.dump(d)
            self.assertEqual(s, 'a: 42\nb:\n  c: 69\n')
        except ImportError:
            pass

    # get-tests

    def test_getattr(self):
        self.assertEqual(self.attrdict_ex.a, 1)

    def test_getitem(self):
        self.assertEqual(self.attrdict_ex['a'], 1)

    def test_getattr_recursive(self):
        self.assertEqual(self.attrdict_ex.c.d, 3)

    def test_getitem_recursive(self):
        self.assertEqual(self.attrdict_ex['c']['d'], 3)

    def test_getattr_mixed(self):
        self.assertEqual(self.attrdict_ex.c['d'], 3)

    def test_getitem_mixed(self):
        self.assertEqual(self.attrdict_ex['c'].d, 3)

    def test_getattr_error(self):
        self.assertRaises(KeyError, lambda d: d.non_existent, self.attrdict_ex)

    def test_getitem_error(self):
        self.assertRaises(KeyError, lambda d: d['non_existent'], self.attrdict_ex)

    def test_getitem_protected(self):
        d = dotdict(a = 42, keys = 69)
        self.assertEqual(d['keys'], 69)

    def test_getattr_protected(self):
        d = dotdict(a = 42, keys = 69)
        self.assertTrue(callable(d.keys))

    # set-tests

    def test_setattr_existing(self):
        self.attrdict_ex.a = 42
        self.assertEqual(self.attrdict_ex.a, 42)

    def test_setattr_new(self):
        self.attrdict_ex.q = 69
        self.assertEqual(self.attrdict_ex.q, 69)

    def test_setattr_nested_dict(self):
        self.attrdict_ex.q = {'a': 1, 'b': {'c': 69}}
        self.assertEqual(self.attrdict_ex.q.b.c, 69)

    def test_setattr_nested_dict_subclass(self):
        class A(dict):
            pass
        self.attrdict_ex.q = A(a = 1)
        self.assertTrue(isinstance(self.attrdict_ex.q, A))
        self.assertRaises(AttributeError, lambda m: m.a, self.attrdict_ex.q)

    def test_setattr_nested_tuple_subclass(self):
        class A(tuple):
            pass
        self.attrdict_ex.q = A(({'a': 1},))
        self.assertTrue(isinstance(self.attrdict_ex.q, A))
        self.assertTrue(type(self.attrdict_ex.q[0]) is dict)
        self.assertRaises(AttributeError, lambda m: m.a, self.attrdict_ex.q[0])

    def test_setattr_nested_list_subclass(self):
        class A(tuple):
            pass
        self.attrdict_ex.q = A([{'a': 1}])
        self.assertTrue(isinstance(self.attrdict_ex.q, A))
        self.assertTrue(type(self.attrdict_ex.q[0]) is dict)
        self.assertRaises(AttributeError, lambda m: m.a, self.attrdict_ex.q[0])

    def test_setattr_nested_tuple(self):
        self.attrdict_ex.q = {'a': 1, 'b': ({'c': 69},)}
        self.assertEqual(self.attrdict_ex.q.b[0].c, 69)

    def test_setattr_nested_list(self):
        self.attrdict_ex.q = {'a': 1, 'b': [{'c': 69}]}
        self.assertEqual(self.attrdict_ex.q.b[0].c, 69)

    def test_setitem_existing(self):
        self.attrdict_ex['a'] = 42
        self.assertEqual(self.attrdict_ex['a'], 42)

    def test_setitem_new(self):
        self.attrdict_ex['q'] = 69
        self.assertEqual(self.attrdict_ex['q'], 69)

    def test_setattr_recursive_existing(self):
        self.attrdict_ex.c.f.g = 42
        self.assertEqual(self.attrdict_ex.c.f.g, 42)

    def test_setattr_recursive_new(self):
        self.attrdict_ex.c.f.q = 69
        self.assertEqual(self.attrdict_ex.c.f.q, 69)

    def test_setitem_recursive_existing(self):
        self.attrdict_ex['c']['f']['g'] = 42
        self.assertEqual(self.attrdict_ex['c']['f']['g'], 42)

    def test_setitem_recursive_new(self):
        self.attrdict_ex['c']['f']['q'] = 69
        self.assertEqual(self.attrdict_ex['c']['f']['q'], 69)

    def test_setattr_mixed_existing(self):
        self.attrdict_ex.c['f'].g = 42
        self.assertEqual(self.attrdict_ex.c['f'].g, 42)

    def test_setattr_mixed_new(self):
        self.attrdict_ex.c['f'].q = 69
        self.assertEqual(self.attrdict_ex.c['f'].q, 69)

    def test_setattr_unresolved(self):
        def test():
            self.attrdict_ex.c.non_existent.foo = 69
        self.assertRaises(KeyError, test)

    def test_setattr_protected(self):
        def test(key):
            self.attrdict_ex.__setattr__(key, 69)
        for k in self.keywords:
            self.assertRaises(AttributeError, test, k)

    # del-tests

    def test_delattr(self):
        del self.attrdict_ex.a
        self.assertFalse('a' in self.attrdict_ex)

    def test_delitem(self):
        del self.attrdict_ex['a']
        self.assertFalse('a' in self.attrdict_ex)

    def test_delattr_error(self):
        def test():
            del self.attrdict_ex.non_existent
        self.assertRaises(KeyError, test)

    def test_delitem_error(self):
        def test():
            del self.attrdict_ex['non_existent']
        self.assertRaises(KeyError, test)

    def test_delattr_protected(self):
        def test(d, key):
            d.__delattr__(key)
        d = dotdict(a = 42, keys = 69)
        for k in self.keywords:
            self.assertRaises(AttributeError, test, d, k)

    # update tests

    def test_update_dict(self):
        upd = dict(a = 42, c = dict(d = 69))
        ref = dict(a = 42, b = 2, c = dict(d = 69))
        self.attrdict_ex.update(upd)
        self.assertEqual(self.attrdict_ex, ref)

    def test_update_iterable(self):
        upd = [('a', 42), ('c', dict(d = 69))]
        ref = dict(a = 42, b = 2, c = dict(d = 69))
        self.attrdict_ex.update(upd)
        self.assertEqual(self.attrdict_ex, ref)

    def test_update_kwargs(self):
        upd = dict(a = 42, c = dict(d = 69))
        ref = dict(a = 42, b = 2, c = 69)
        self.attrdict_ex.update(upd, c = 69)
        self.assertEqual(self.attrdict_ex, ref)

    def test_update_error(self):
        self.assertRaises(TypeError, self.attrdict_ex.update, 42)
        self.assertRaises(TypeError, self.attrdict_ex.update, 42, 69)

    def test_update_iterable_error(self):
        self.assertRaises(TypeError, self.attrdict_ex.update, [42, 69])

    def test_update_dict_recursive(self):
        upd = dict(a = 42, c = dict(d = 69))
        ref = self.dict_ex
        ref['a'], ref['c']['d'] = 42, 69
        self.attrdict_ex.update(upd, recursive = True)
        self.assertEqual(self.attrdict_ex, ref)

    def test_update_iterable_recursive(self):
        upd = [('a', 42), ('c', dict(d = 69))]
        ref = self.dict_ex
        ref['a'], ref['c']['d'] = 42, 69
        self.attrdict_ex.update(upd, recursive = True)
        self.assertEqual(self.attrdict_ex, ref)

    def test_update_nested_iterable_recursive(self):
        upd = [('a', 42), ('c', [('d', 69)])]
        ref = dict(a = 42, b = 2, c = [('d', 69)])
        self.attrdict_ex.update(upd, recursive = True)
        self.assertEqual(self.attrdict_ex, ref)

    def test_update_kwargs_recursive(self):
        upd = dict(a = 42, c = dict(d = 69))
        ref = self.dict_ex
        ref['a'], ref['c'] = 42, 69
        self.attrdict_ex.update(upd, c = 69, recursive = True)
        self.assertEqual(self.attrdict_ex, ref)

    def test_update_kwargs_nested_recursive(self):
        upd = dict(a = 42, c = dict(d = 69))
        self.attrdict_ex.update(upd, c = dict(d = 420), recursive = True)
        ref = self.dict_ex
        ref['a'], ref['c']['d'] = 42, 420
        self.assertEqual(self.attrdict_ex, ref)

    def test_update_error_recursive(self):
        self.assertRaises(TypeError, self.attrdict_ex.update, 42, recursive = True)
        self.assertRaises(TypeError, self.attrdict_ex.update, 42, 69, recursive = True)

    def test_update_iterable_error_recursive(self):
        self.assertRaises(TypeError, self.attrdict_ex.update, [42, 69], recursive = True)


if __name__ == "__main__":
    unittest.main()
