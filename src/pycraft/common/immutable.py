# -*- coding: utf8 -*-

import operator


class ImmutableMeta(type):
    """immutable クラスを構築するためのメタクラス
    
    >>> class Vector(metaclass=ImmutableMeta):
    ...
    ...     properties = 'x y'
    ...     
    ...     @classmethod
    ...     def new(cls, x=0, y=0):
    ...         return x, y
    
    >>> v = Vector(1,-1)
    >>> v
    (1, -1)
    >>> v.x
    1
    >>> v.y
    -1
    >>> Vector()
    (0, 0)
    >>> Vector(y=2)
    (0, 2)
    """
    
    def __new__(cls, cls_name, bases, attrs):
        attrs['__slots__'] = []
        if 'properties' in attrs:
            properties = attrs['properties'].split()
            # property を追加
            for i, name in enumerate(properties):
                attrs[name] = property(operator.itemgetter(i))
            # __new__ を置き換え
            attrs['__new__'] = cls.new_method(attrs, properties)
        # tuple を継承していなければ、基底クラスに tuple を追加
        if not list(c for c in bases if issubclass(c, tuple)):
            bases = (tuple, ) + bases
        return type.__new__(cls, cls_name, tuple(bases), attrs)

    @staticmethod
    def new_method(attrs, properties):
        def gen(new_func):
            def __new__(cls, *args, **kwargs):
                args = new_func(cls, *args, **kwargs)
                if len(args) != len(properties):
                    raise TypeError(
                        '__new__() takes {0} arguments ({1} given)'.format(
                            len(properties), len(args)))
                return tuple.__new__(cls, args)
            return __new__
        if 'new' in attrs:
            return gen(lambda cls, *args, **kwargs: cls.new(*args, **kwargs))
        else:
            return gen(lambda cls, *args, **kwargs: tuple(args))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
