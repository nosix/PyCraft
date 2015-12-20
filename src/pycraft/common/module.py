# -*- coding: utf8 -*-

from inspect import isclass


def filter_classes(filter_func, key_func, *modules):
    """指定したモジュールに含まれるクラスの (key_func(cls), cls) ペアを返す
    
    filter_func(cls) が True のクラスのみ返す
    """
    return (
        (key_func(o), o) for m in modules \
            for o in m.__dict__.values() if isclass(o) and filter_func(o))
