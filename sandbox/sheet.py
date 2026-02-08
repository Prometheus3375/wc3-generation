import gspread

from wc3gen.sheet import Row, Sheet

gc = gspread.service_account(filename='sandbox/wisptd-reader.json')
spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1LfpGAp6Z0qlFUxjVStFu5Z_0_Dj_U5Wck339fdPyUKk')


def split(value: str) -> list[str]:
    return value.split(', ')


def str2bool(value: str) -> bool:
    value = value.lower()
    if value == 'yes':
        return True
    if value == 'no':
        return False

    raise ValueError()


def percent(value: str) -> float:
    return float(value[:-1]) / 100


class Stats(Row):
    name: str = 'minion'
    plural: str
    gold_cost: int
    exp_cost: int
    supply_usage: int
    income: int
    limit: int
    amount: int

    abilities: list[str] = split

    lives_consume: int
    lives_gain: int

    class KilledStats(Row):
        __prefix__ = 'killed - '
        gold: int
        exp: int
        tower_exp: int
        income: int
        lives: int

    class LeakedStats(Row):
        __prefix__ = 'leaked - '
        gold: int
        exp: int

    killed: KilledStats
    leaked: LeakedStats

    war3_max_hp: float
    max_health: float
    regen: float
    health_upgrade: float
    ms_factor: float = percent
    ms_type: str
    phys_armor: int
    mag_armor: int

    class Flags(Row):
        class_: str
        decays: bool = str2bool
        special: bool = str2bool
        merc: bool = str2bool
        challenger: bool = str2bool

    flags: Flags

    class Rawcodes(Row):
        __postfix__ = ' rawcode'
        unit: str
        spawn: str
        info: str

    rawcode: Rawcodes

    estimated_cost: float


class MinionStats(Sheet[Stats]):
    spreadsheet = spreadsheet
    title = 'Minion Stats'
    transpose = True


def conv(value: str) -> int:
    return 0 if value == '' else int(value)


class MinionUpgrade(Row):
    name: str = 'upgrade'
    gold_cost: int = conv
    exp_cost: int = conv
    description: str
    minion_description: str
    button_raw: str
    icon_raw: str


class MinionUpgrades(Sheet[MinionUpgrade]):
    spreadsheet = spreadsheet
    title = 'Minion Upgrades'


# class MinionUpgradesRu(Sheet[MinionUpgrade]):
#     spreadsheet = spreadsheet
#     title = 'Minion Upgrades Ru'


minion_stats = MinionStats()
minion_upgrades = MinionUpgrades()
