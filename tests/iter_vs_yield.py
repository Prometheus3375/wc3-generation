from .time import repeat


def iterator(t: tuple):
    return iter(t)


def generator(t: tuple):
    yield from t


result = repeat('o = iterator((1, 2, 3, 4, 5, 6, 7, 8, 9))', globals_=dict(iterator=iterator))
print(result)  # 115.7 ±   26.4 ns
result = repeat('o = iterator((1, 2, 3, 4, 5, 6, 7, 8, 9))', globals_=dict(iterator=generator))
print(result)  # 177.5 ±   37.0 ns

result = repeat('for _ in o: pass', 'o = iterator((1, 2, 3, 4, 5, 6, 7, 8, 9))', globals_=dict(iterator=iterator))
print(result)  # 17.8 ±    0.9 ns
result = repeat('for _ in o: pass', 'o = iterator((1, 2, 3, 4, 5, 6, 7, 8, 9))', globals_=dict(iterator=generator))
print(result)  # 20.4 ±    5.4 ns
