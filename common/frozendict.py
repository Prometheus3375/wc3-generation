class frozendict(dict):
    __slots__ = ()

    clear = None
    pop = None
    popitem = None
    setdefault = None
    update = None

    __delitem__ = None
    __setitem__ = None
    __ior__ = None

    def __repr__(self, /) -> str:
        return f'{self.__class__.__name__}({dict.__repr__(self)})'

    def __hash__(self, /) -> int:
        return hash(frozenset(self.items()))  # frozenset to have the same hash for different order


# dict methods
#     clear, pop, popitem, setdefault, update
#     copy, fromkeys, get, items, keys, values
# dict special attributes
#     __class__, __class_getitem__, __delattr__, __dir__, __doc__, __format__, __getattribute__, __init_subclass__,
#     __new__, __reduce__, __reduce_ex__, __setattr__, __sizeof__, __subclasshook__
# dict attributes for overwrite
#   __contains__, __delitem__, __eq__, __ge__, __getitem__, __gt__, __hash__, __init__, __ior__, __iter__, __le__,
#   __len__, __lt__, __ne__, __or__, __repr__, __reversed__, __ror__, __setitem__, __str__
