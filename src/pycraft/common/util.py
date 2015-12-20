# -*- coding: utf8 -*-

import collections
import itertools
import numbers


def max_int(byte, signed):
    """指定した条件における整数の最大値を返す
    
    >>> max_int(1, False)
    255
    >>> max_int(1, True)
    127
    >>> max_int(2, False)
    65535
    """
    return (1 << (byte*8 - (1 if signed else 0))) - 1


def divide_seq(s, n):
    """Sequence を固定長で分割する
    
    >>> divide_seq('abcdefg', 3)
    ['abc', 'def', 'g']
    >>> divide_seq(b'abcdefg', 4)
    [b'abcd', b'efg']
    """
    return [s[i:i+n] for i in range(0, len(s), n)]


def ndarray(*size):
    """多次元配列を返す
    
    >>> ndarray(2)
    [0, 0]
    >>> ndarray(2,3)
    [[0, 0, 0], [0, 0, 0]]
    """
    return [0] * size[0] if len(size) == 1 \
        else [ndarray(*size[1:]) for _ in range(size[0])]


def put_in_range(n, m):
    """n を 0 <= n < m の範囲の値にする
    
    >>> put_in_range(90, 360)
    90
    >>> put_in_range(-90, 360)
    270
    >>> put_in_range(360, 360)
    0
    >>> put_in_range(450, 360)
    90
    """
    while n < 0:
        n += m
    return n % m


def put_in_border(n, min_n, max_n):
    """境界内に値を収める
    
    >>> put_in_border(-46, -45, 45)
    -45
    >>> put_in_border(0, -45, 45)
    0
    >>> put_in_border(46, -45, 45)
    45
    """
    if n < min_n:
        return min_n
    if n > max_n:
        return max_n
    return n


def iter_count(iterable):
    """sequence オブジェクトを生成せずに繰り返し回数を返す"""
    n = 0
    for _ in iterable:
        n += 1
    return n


def product(*iterables):
    """itertools.product のラッパー関数
    
    itertools.product は汎用的であり速度低下が認められたため
    使用頻度の高い2,3次元を簡潔な実装で代用する。
    """
    if len(iterables) == 2:
        seqs = [[i for i in it] for it in iterables]
        for i in seqs[0]:
            for j in seqs[1]:
                yield i,j
    elif len(iterables) == 3:
        seqs = [[i for i in it] for it in iterables]
        for i in seqs[0]:
            for j in seqs[1]:
                for k in seqs[2]:
                    yield i,j,k
    else:
        for i in itertools.product(iterables):
            yield i

def names(ids):
    """ID の一覧(name -> id)から(id -> name)の一覧を生成する"""
    return dict(
        (v,k) for k,v in ids.__dict__.items() if not k.startswith('_'))


def summary(key, value):
    """属性値の概要を表す文字列にする"""
    if isinstance(value, collections.Mapping):
        return key + '.keys=' + str(value.keys())
    if isinstance(value, tuple) or isinstance(value, set):
        return key + '=' + str(value)
    if isinstance(value, collections.Sized):
        return 'len(' + key + ')=' + str(len(value))
    if isinstance(value, numbers.Number):
        return key + '=' + str(value)
    return key + ':' + value.__class__.__name__


if __name__ == '__main__':
    import doctest
    doctest.testmod()