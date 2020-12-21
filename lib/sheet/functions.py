_alphabet_offset = ord('A') - 1
_alphabet_len = ord('Z') - ord('A') + 1


def index2column(index: int) -> str:
    if index <= 0:
        raise ValueError(f'Column index must be positive, got {index}')

    name = []
    while index > _alphabet_len:
        rem = index % _alphabet_len
        index //= _alphabet_len
        if rem == 0:
            rem = _alphabet_len
            index -= 1
        name.append(chr(rem + _alphabet_offset))

    name.append(chr(index + _alphabet_offset))
    return ''.join(reversed(name))


def column2index(column: str) -> int:
    if len(column) == 0:
        raise ValueError(f'Column name must consist of upper latin letters, got empty string')

    for c in column:
        if not c.isupper():
            raise ValueError(f'Column name must consist of upper latin letters, got {column}')

    result = 0
    pw = 1
    for c in reversed(column):
        result += (ord(c) - _alphabet_offset) * pw
        pw *= _alphabet_len

    return result
