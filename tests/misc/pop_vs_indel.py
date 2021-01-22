from tests.time import repeat

setup = 'd = {i: f"{i}" for i in range(100)}'
rep = 10 ** 5
key = 50
result = repeat(f'v = d.pop(key)', setup, repeat_=rep, number=1, globals_=dict(key=key))
print('Pop known key:               ', result)  # 100 ns

result = repeat(f'v = d.pop(key, 0)', setup, repeat_=rep, number=1, globals_=dict(key=key))
print('Pop known key with default:  ', result)  # 100 ns

result = repeat(f'v = d.pop(-1, 0)', setup, repeat_=rep, number=1, globals_=dict(key=key))
print('Pop unknown key with default:', result)  # 100 ns

result = repeat(
    (
        f'if key in d:\n'
        f'    v = d[key]\n'
        f'    del d[key]'
    ), setup, repeat_=rep, number=1, globals_=dict(key=key))
print('Delete key if in dict:       ', result)  # 200 ns, sometimes 100 ns with literal key

result = repeat(
    (
        f'if key in d:\n'
        f'    v = d.pop(key)'
    ), setup, repeat_=rep, number=1, globals_=dict(key=key))
print('Pop key if in dict:          ', result)  # 200 ns

result = repeat(
    (
        f'v = d.pop(key, no)\n'
        f'if v is not no: pass'
    ), setup, repeat_=rep, number=1, globals_=dict(no=object(), key=key))
print('Pop key and then check:      ', result)  # 100 ns
