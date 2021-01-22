from tests.time import repeat

t = tuple(i for i in range(2))

vars = ', '.join(f'a{i}' for i in t)
print(repeat(f'{vars} = t', globals_=dict(t=t)))

print(repeat('\n'.join(f'a{i} = t[{i}]' for i in t), globals_=dict(t=t)))
