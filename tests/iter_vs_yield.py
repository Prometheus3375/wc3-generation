from .time import repeat


def iterator(t: tuple):
    return iter(t)


def generator1(t: tuple):
    yield from t


def generator2(t: tuple):
    for v in t:
        yield v


tup = (1, 2, 3, 4, 5, 6, 7, 8, 9)
result = repeat('o = iterator(tup)', globals_=dict(iterator=iterator, tup=tup))
print(result)  # 117.5 ±   32.7 ns
result = repeat('o = iterator(tup)', globals_=dict(iterator=generator1, tup=tup))
print(result)  # 184.1 ±   30.3 ns
result = repeat('o = iterator(tup)', globals_=dict(iterator=generator2, tup=tup))
print(result)  # 181.4 ±    8.0 ns

result = repeat('for _ in o: pass', 'o = iterator(tup)', globals_=dict(iterator=iterator, tup=tup))
print(result)  # 18.7 ±    0.9 ns
result = repeat('for _ in o: pass', 'o = iterator(tup)', globals_=dict(iterator=generator1, tup=tup))
print(result)  # 20.4 ±    1.1 ns
result = repeat('for _ in o: pass', 'o = iterator(tup)', globals_=dict(iterator=generator2, tup=tup))
print(result)  # 20.9 ±    1.8 ns

result = repeat('for _ in iterator(tup): pass', globals_=dict(iterator=iterator, tup=tup))
print(result)  # 195.0 ±   15.5 ns
result = repeat('for _ in iterator(tup): pass', globals_=dict(iterator=generator1, tup=tup))
print(result)  # 488.7 ±   79.9 ns
result = repeat('for _ in iterator(tup): pass', globals_=dict(iterator=generator2, tup=tup))
print(result)  # 549.7 ±   87.1 ns
