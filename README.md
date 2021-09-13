# dotdict

A python library which provides an extension to the `dict` with an ability to access dictionary values in an attribute-like fashion:
```python
>>> D = dotdict({'foo': {'bar': {'spam': 69}}})
>>> D.foo.bar.spam
69
```

## Installation

Install the package
```
pip install https://github.com/dmtlvn/dotdict/archive/refs/heads/main.zip
```

To run tests run:
```
pip install -r requirements.txt
```

## Usage

The goal of the `dotdict` is to add a bit of convenient syntactic sugar while keeping all the standard interfaces intact. It is therefore is meant to be compatible with the standard `dict` in as many scenarios as possible. The main use cases for the added functionality are dictionaries with fixed schemas, access to which is not determined at runtime. 

`dotdict` supports all the construction methods the normal `dict` does: mappings, iterables, generators, keywords etc. Conversion back to `dict` is done using method `dotdict.to_dict()`. All nested `dict` instances (**but not its subclasses**) are recursively converted to a `dotdict`, which enables chaining the dot to access nested dictionaries. Recursion also enters default `list` and `tuple` containers, but again **not their subclasses**. Subclasses of `dict`, `list` and `tuple` are stored as is, so all user-defined classes behave as expected:

```python
>>> D = dotdict({
...   'foo': 4.20, 
...   'bar': {'spam': 'egg'}, 
...   'baz': ['big', 'black', {'crocs': 69}]
... })
>>> D.bar
dotdict({'spam': 'egg'})
>>> D.bar.spam
'egg'
>>> D.baz[2].crocs
69

>>> D = dotdict({'foo': 4.20, 'bar': OrderedDict(spam = 420, egg = 'nice')})
>>> type(D.bar)
collections.OrderedDict

>>> class FancyTuple(tuple):
...   __fancy_meter__ = 9000
>>> D = dotdict({'foo': 4.20, 'bar': FancyTuple((69, {"spam": "egg"}))})
>>> type(D.bar)
FancyTuple
>>> type(D.bar[1])
dict
```

The `dotdict` is mutable in the same way as a standard dictionary. The difference is that all `dict` instances in the assigned value are converted to `dotdict` recursively through other `dict`, `list` and `tuple` items, but **not through their subclasses**:
```python
>>> D = dotdict({'foo': 69, 'bar': {'spam': 4.20, "egg": ["big", "black", "crocs"]}})
>>> D.foo = 'nice'
>>> D.foo
'nice'
>>> D.foo = {'baz': 'nice'}
>>> type(D.foo)
dotdict
>>> D.bar.egg[2] = "crow"
>>> D.bar.egg
["big", "black", "crow"]
>>> del D.bar.egg
>>> D.bar
{'spam': 4.2}
```

The standard index operator is kept intact and is still present to allow access to non-string keys. It also keeps the ability to provide keys at runtime, as usual:
```python
>>> D = dotdict({'foo': 'bar', 420: 69})
>>> D.420  # duh
SyntaxError: invalid syntax
>>> D['foo'], D[420]
('bar', 69)
```

Attribute-style and index-style access can be mixed for nested dictionaries:
```python
>>> D = dotdict({'foo': 69, 'bar': {'spam': 4.20}})
>>> D['bar'].spam
4.2
>>> D.bar['spam']
4.2
```

`dotdict` throws the same KeyError exceptions the normal `dict` does regardless the way of key access. Also, `hasattr` check works as expected: 
```python
>>> D = dotdict({'foo': 69, 'bar': {'spam': 4.20}})
>>> D.spam
KeyError: 'spam'
>>> D.spam.egg = 'nice'   # does not support recursive assignment
KeyError: 'spam'
>>> del D.spam
KeyError: 'spam'

>>> hasattr(D, 'foo')
False
```

The common problem in many similar implementations is handling of standard method names. `dotdict` resolves such cases in favor of the standard `dict` behavior. It can store these keywords but they can be accessed only with the index operator. The new syntax can make such cases a bit confusing, however, because it can't be used at runtime, it won't break anything: 
```python
>>> D = attrdict(keys = 69)
>>> D['keys']
69
>>> D.keys
<function dotdict.keys>
>>> D.keys = 4.20
AttributeError: 'dict' object attribute 'keys' is read-only
>>> del D.keys
AttributeError: 'dict' object attribute 'keys' is read-only
```

Comparison to `dict` instances still works as expected:
```python
>>> A = {'foo': 69, 'bar': {'spam': 4.20}}
>>> B = dotdict(A)
>>> A == B
True
```

Additional option allows for a recursive update of nested dictionaries. A standard non-recursive update is performed by default:
```python
>>> D = dotdict({'foo': 69, 'bar': {'spam': 'egg', 'baz': 4.20}})
>>> D.update({'foo': 'nice', 'bar': {'baz': 420}}, recursive = True)
>>> D
dotdict({'foo': 'nice', 'bar': {'spam': 'egg', 'baz': 420}})

>>> D = dotdict({'foo': 69, 'bar': {'spam': 'egg', 'baz': 4.20}})
>>> D.update({'foo': 'nice', 'bar': {'baz': 420}})
>>> D
dotdict({'foo': 'nice', 'bar': {'baz': 420}})
```

`dotdict` is fully compatible with pickle, and partially compatible json and PyYAML libs. In the case of pickle, the `dotdict` object is saved as is. In the case of JSON and YAML, it is naturally serialized and deserialized as a normal `dict`. This keeps readability of serialized representations, but can break your code in some cases
```python
>>> D = dotdict({'foo': 69, 'bar': {'spam': 4.20}})
>>> D = pickle.loads(pickle.dumps(D))
>>> D.bar.spam
4.2

>>> json.dumps(D)
'{"foo": 69, "bar": {"spam": 4.20}}}'
>>> E = json.loads(json.dumps(D))
>>> E.foo
AttributeError: 'dict' object has no attribute 'foo'

>>> print(yaml.dump(D))
bar:
  spam: 4.2
foo: 69 
>>> E = yaml.load(yaml.dump(b))
>>> E.foo
AttributeError: 'dict' object has no attribute 'foo'
```
