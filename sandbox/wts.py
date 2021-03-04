from misclib import exc2str

from wc3gen.wts import wtsFile


def extract_types_and_fields(path: str):
    file = wtsFile(path)
    types = set()
    fields = set()
    for s in file.storage:
        try:
            comment = s.comment.strip()
            if comment:
                colon = comment.index(':')
                types.add(comment[3:colon])
                closing_brace = comment.rindex(')', colon + 2, len(comment) - 2)
                opening_brace = comment.index('(', closing_brace + 3)
                fields.add(comment[closing_brace + 3:opening_brace - 1])
        except ValueError as e:
            print(f'Exception in string {s.id}')
            print(f'Comment: {s.comment}')

            print(exc2str(e))

    for t in sorted(types):
        print(f'{t} = \'{t}\'')

    print()

    for f in sorted(fields):
        print(f'{f} = \'{f}\'')


extract_types_and_fields('sandbox/strings.wts')
