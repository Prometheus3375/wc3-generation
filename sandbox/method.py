class Class:
    def method(self, a: int, b: str, c: float) -> list:
        return [self, a, b, c]


def method(self, a: int, b: str, c: float) -> list:
    return [self, a, b, c]


assert dir(Class.method) == dir(method)

equal = []
for f in dir(method):
    cm = getattr(Class.method, f)
    m = getattr(method, f)
    if callable(cm):
        cm = getattr(type(Class.method), f)
        m = getattr(type(method), f)
    if not (cm is m or cm == m):
        print(f'{f}: class method - {cm}, method - {m}')
    elif not callable(cm):
        equal.append(f)

print(equal)
