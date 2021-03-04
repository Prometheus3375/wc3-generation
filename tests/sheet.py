from wc3gen.sheet.functions import column2index, index2column


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
