from tests.time import repeat

print(repeat('a = (255 << 24) | (255 << 16) | (255 << 8) | 255'))
print(repeat('a = (255 << 24) + (255 << 16) + (255 << 8) + 255'))
