from collections.abc import Mapping


class dotdict(dict):
    """
    dotdict(*args, **kwargs)
    A subclass of dict which adds attribute-style access to dict values
    along with usual index-style access:

    Example:
    D = attrdict(foo = 42, spam = {"egg": 69})
    D.foo
    >>> 42
    D.spam.egg
    >>> 69
    D['spam'].egg
    >>> 69

    Recursively converts all nested instances of `dict` into `dotdict` inside
    other dicts, lists and tuples and keeps this structure upon updates.
    """

    __protected_keywords__ = {
        "clear", "copy", "fromkeys", "get", "items", "keys",
        "pop", "popitem", "setdefault", "update", "values", "to_dict"
    }

    def __init__(self, *args, **kwargs):
        super().__init__()
        init_dict = dict(*args, **kwargs)
        self.clear()
        for k, v in init_dict.items():
            if type(v) is tuple:
                v = tuple(dotdict(i) if type(i) is dict else i for i in v)
            if type(v) is list:
                v = [dotdict(i) if type(i) is dict else i for i in v]
            if type(v) is dict:
                v = dotdict(v)
            self.__setitem__(k, v)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, k, v):
        if type(v) is tuple:
            v = tuple(dotdict(i) if type(i) is dict else i for i in v)
        if type(v) is list:
            v = [dotdict(i) if type(i) is dict else i for i in v]
        if type(v) is dict:
            v = dotdict(v)
        # value = attrdict(value) if type(value) is dict else value
        dict.__setitem__(self, k, v)

    def __getattr__(self, key):
        return dict.__getitem__(self, key)

    def __setattr__(self, key, value):
        if key not in self.__protected_keywords__:
            self.__setitem__(key, value)
        else:
            raise AttributeError(f"'dict' object attribute '{key}' is read-only")

    def __delattr__(self, key):
        if key not in self.__protected_keywords__:
            del self[key]
        else:
            raise AttributeError(f"'dict' object attribute '{key}' is read-only")

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, data):
        self.clear()
        for k, v in data.items():
            if type(v) is dict:
                v = dotdict(v)
            self.__setitem__(k, v)

    def __repr__(self):
        return f"{self.__class__.__name__}({dict.__repr__(self)})"

    def update(self, *args, recursive = False, **kwargs):
        """
        D.update([E,] recursive = False, **F). Updates values in D with values
        from E and F.
        If recursive is False (default), performs a standard dict.update(E, **F)
        If recursive is True, merges E and F recursively first, and then applies
        a recursive standard update for every nested Mapping value.
        """

        if not recursive:
            super().update(*args, **kwargs)
            return

        if len(args) > 1:
            raise TypeError(f"update expected at most 1 arguments, got {len(args)}")

        update_dict = dotdict(*args)
        if kwargs:
            update_dict.update(kwargs, recursive = True)

        for k, v in update_dict.items():
            if isinstance(v, Mapping):
                if k not in self or not isinstance(self[k], dotdict):
                    self[k] = dotdict()
                self[k].update(v, recursive = True)
            else:
                self[k] = v
        return

    def to_dict(self):
        """
        Converts every nested dotdict in other dicts, dotdicts, lists and tuples
        back to a standard dict
        """
        state = dict()
        for k, v in self.items():
            if type(v) is tuple:
                v = tuple(i.to_dict() if type(i) is dotdict else i for i in v)
            if type(v) is list:
                v = [i.to_dict() if type(i) is dotdict else i for i in v]
            if type(v) is dict:
                v = {k: i.to_dict() if type(i) is dotdict else i for k, i in v.items()}
            if type(v) is dotdict:
                v = v.to_dict()
            state[k] = v
        return state


try:
    import yaml
    yaml.add_representer(dotdict, yaml.representer.Representer.represent_dict)
except ImportError:
    pass
