from .time import repeat


def iterator(t: tuple):
    return iter(t)


def generator(t: tuple):
    yield from t


result = repeat('o = iterator((1, 2, 3, 4, 5, 6, 7, 8, 9))', globals_=dict(iterator=iterator))
print(result)  # 127.1 ±   89.5 ns
result = repeat('o = iterator((1, 2, 3, 4, 5, 6, 7, 8, 9))', globals_=dict(iterator=generator))
print(result)  # 183.2 ±   40.6 ns

result = repeat('for _ in o: pass', 'o = iterator((1, 2, 3, 4, 5, 6, 7, 8, 9))', globals_=dict(iterator=iterator))
print(result)  # 19.2 ±    7.6 ns
result = repeat('for _ in o: pass', 'o = iterator((1, 2, 3, 4, 5, 6, 7, 8, 9))', globals_=dict(iterator=generator))
print(result)  # 22.6 ±   11.1 ns

result = repeat('for _ in iterator((1, 2, 3, 4, 5, 6, 7, 8, 9)): pass', globals_=dict(iterator=iterator))
print(result)  # 199.7 ±   39.3 ns
result = repeat('for _ in iterator((1, 2, 3, 4, 5, 6, 7, 8, 9)): pass', globals_=dict(iterator=generator))
print(result)  # 478.2 ±   70.7 ns
