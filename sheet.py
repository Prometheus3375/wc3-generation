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


def check_conversions(index: int, column: str):
    col = index2column(index)
    idx = column2index(column)

    assert col == column, f'Got {col}, must be {column}'
    assert idx == index, f'Got {idx}, must be {index}'


check_conversions(1, 'A')
check_conversions(2, 'B')
check_conversions(25, 'Y')
check_conversions(26, 'Z')
check_conversions(27, 'AA')
check_conversions(26 * 2, 'AZ')
check_conversions(26 * 2 + 1, 'BA')
check_conversions(26 * 3, 'BZ')
check_conversions(26 * 3 + 1, 'CA')
check_conversions(26 * 26, 'YZ')
check_conversions(26 * 26 + 1, 'ZA')
check_conversions(26 * 27, 'ZZ')
check_conversions(26 * 27 + 1, 'AAA')
check_conversions(26 * 28, 'AAZ')
check_conversions(26 * 53, 'AZZ')
check_conversions(26 * 53 + 1, 'BAA')
check_conversions(26 * 54, 'BAZ')
check_conversions(26 * 80, 'CAZ')
check_conversions(26 * (28 + 25 * 26), 'ZAZ')
check_conversions(26 * (28 + 25 * 26 + 25), 'ZZZ')
check_conversions(26 * (28 + 25 * 26 + 25) + 1, 'AAAA')
check_conversions(26 * (28 + 26 * 26), 'AAAZ')
