from tests.time import repeat


def iterator(t: tuple):
    return iter(t)


def generator1(t: tuple):
    yield from t


def generator2(t: tuple):
    for v in t:
        yield v


def genexp(t: tuple):
    return (v for v in t)


tup = (1, 2, 3, 4, 5, 6, 7, 8, 9)
rep = 1_000_000
number = 1  # to not exhaust iterator

result = repeat('o = iterator(tup)', repeat_=rep, number=number, globals_=dict(iterator=iterator, tup=tup))
print(result)  # 100 ns
result = repeat('o = iterator(tup)', repeat_=rep, number=number, globals_=dict(iterator=generator1, tup=tup))
print(result)  # 100 ns
result = repeat('o = iterator(tup)', repeat_=rep, number=number, globals_=dict(iterator=generator2, tup=tup))
print(result)  # 100 ns
result = repeat('o = iterator(tup)', repeat_=rep, number=number, globals_=dict(iterator=genexp, tup=tup))
print(result)  # 200 ns
print()

result = repeat('for _ in o: pass', 'o = iterator(tup)', repeat_=rep, number=number,
                globals_=dict(iterator=iterator, tup=tup))
print(result)  # 200 ns
result = repeat('for _ in o: pass', 'o = iterator(tup)', repeat_=rep, number=number,
                globals_=dict(iterator=generator1, tup=tup))
print(result)  # 500 ns
result = repeat('for _ in o: pass', 'o = iterator(tup)', repeat_=rep, number=number,
                globals_=dict(iterator=generator2, tup=tup))
print(result)  # 500 ns
result = repeat('for _ in o: pass', 'o = iterator(tup)', repeat_=rep, number=number,
                globals_=dict(iterator=genexp, tup=tup))
print(result)  # 500 ns
print()

result = repeat('for _ in iterator(tup): pass', repeat_=rep, number=number, globals_=dict(iterator=iterator, tup=tup))
print(result)  # 200 ns
result = repeat('for _ in iterator(tup): pass', repeat_=rep, number=number, globals_=dict(iterator=generator1, tup=tup))
print(result)  # 500 ns
result = repeat('for _ in iterator(tup): pass', repeat_=rep, number=number, globals_=dict(iterator=generator2, tup=tup))
print(result)  # 600 ns
result = repeat('for _ in iterator(tup): pass', repeat_=rep, number=number, globals_=dict(iterator=genexp, tup=tup))
print(result)  # 600 ns
print()
