from common.metaclasses import EmptySlotsByDefaults


class Meta1(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict, *, arg1: str = 'arg1', **kwargs):
        print(arg1)
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class Meta2(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict, *, arg2: str = 'arg2', **kwargs):
        print(arg2)
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class Meta3(Meta1, Meta2):
    pass


class Class(metaclass=Meta3, arg1='1', arg2='2'):
    pass


class MyClass(metaclass=EmptySlotsByDefaults):
    pass
