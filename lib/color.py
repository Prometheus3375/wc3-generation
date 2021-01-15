import re
from typing import final

from common import sorted_ext


def _hsv2rgb_helper(n: int, h: int, a: int, v: int, /) -> int:
    k = (n + h / 60.) % 6
    return round((v - a * max(0., min(k, 4. - k, 1.))) * 255. / 100. / 100.)


def _hsl2rgb_helper(n: int, h: int, a: int, l: int, /) -> int:
    k = (n + h / 30.) % 12
    return round((l - a * max(-1., min(k - 3., 9. - k, 1.))) * 255. / 100. / 100.)


@final
class Color:
    __slots__ = '_argb',

    def __init__(self, /, red: int, green: int, blue: int, alpha: int = 255):
        if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255 and 0 <= alpha <= 255):
            raise ValueError(f'values of color components must be integers in range [0, 255], '
                             f'got {alpha=}, {red=}, {green=}, {blue=}')
        self._argb = (alpha << 24) + (red << 16) + (green << 8) + blue

    @property
    def alpha(self, /):
        return self._argb >> 24

    @property
    def red(self, /):
        return self._argb >> 16 & 255

    @property
    def green(self, /):
        return self._argb >> 8 & 255

    @property
    def blue(self, /):
        return self._argb & 255

    def __str__(self, /):
        return f'{self.alpha:02x}{self.red:02x}{self.green:02x}{self.blue:02x}'

    def __repr__(self, /):
        return f'{self.__class__.__name__}(alpha={self.alpha}, red={self.red}, green={self.green}, blue={self.blue})'

    def __eq__(self, other, /):
        if isinstance(other, self.__class__):
            return self._argb == other._argb

        return NotImplemented

    def __ne__(self, other, /):
        if isinstance(other, self.__class__):
            return self._argb != other._argb

        return NotImplemented

    def __hash__(self, /):
        return self._argb

    def apply(self, string: str, /) -> str:
        return f'|c{self}{string}|r'

    __call__ = apply

    @property
    def alpha_p(self, /):
        return self.alpha * 100 / 255

    @property
    def red_p(self, /):
        return self.red * 100 / 255

    @property
    def green_p(self, /):
        return self.green * 100 / 255

    @property
    def blue_p(self, /):
        return self.blue * 100 / 255

    def to_tuple(self, /):
        return self.red, self.green, self.blue, self.alpha

    __getnewargs__ = to_tuple

    def to_dict(self, /):
        return {'alpha': self.alpha, 'red': self.red, 'green': self.green, 'blue': self.blue}

    @classmethod
    def from_hex(cls, hex_: str, alpha: int = 255, /):
        if len(str) == 8:
            alpha = int(hex_[:2], 16)
            hex_ = hex_[2:]
        elif len(str) != 6:
            raise ValueError(f'length of hex string must be 6 or 8, got {len(str)}')

        return cls(int(hex_[:2], 16), int(hex_[2:4], 16), int(hex_[4:], 16), alpha)

    @property
    def hex(self, /):
        return f'{self.alpha:02x}{self.red:02x}{self.green:02x}{self.blue:02x}'

    @classmethod
    def from_hsv(cls, hue: int, saturation: int, value: int, alpha: int = 255):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB_alternative
        a = saturation * value
        value *= 100
        return cls(
            _hsv2rgb_helper(5, hue, a, value),
            _hsv2rgb_helper(3, hue, a, value),
            _hsv2rgb_helper(1, hue, a, value),
            alpha
        )

    # noinspection DuplicatedCode
    @property
    def hsv(self, /):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        comp = self.red_p, self.green_p, self.blue_p
        sort, idx = sorted_ext(comp)
        min_, _, max_ = sort
        max_idx = idx[2]
        v = max_
        c = max_ - min_
        s = 0. if v == 0. else c * 100. / v
        h = 0. if c == 0. else 60. * (max_idx * 2. + (comp[(max_idx + 1) % 3] - comp[(max_idx + 2) % 3]) / c)
        return round(h), round(s), round(v), self.alpha

    @classmethod
    def from_hsl(cls, hue: int, saturation: int, lightness: int, alpha: int = 255):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB_alternative
        a = saturation * min(lightness, 100 - lightness)
        lightness *= 100
        return cls(
            _hsl2rgb_helper(0, hue, a, lightness),
            _hsl2rgb_helper(8, hue, a, lightness),
            _hsl2rgb_helper(4, hue, a, lightness),
            alpha
        )

    # noinspection DuplicatedCode
    @property
    def hsl(self, /):
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        comp = self.red_p, self.green_p, self.blue_p
        sort, idx = sorted_ext(comp)
        min_, _, max_ = sort
        max_idx = idx[2]
        l = (max_ + min_) / 2.
        c = max_ - min_
        s = 0. if l == 0. or l == 100. else (max_ - l) * 100. / min(l, 100. - l)
        h = 0. if c == 0. else 60. * (max_idx * 2. + (comp[(max_idx + 1) % 3] - comp[(max_idx + 2) % 3]) / c)
        return round(h), round(s), round(l), self.alpha


# TODO move all tests to tests
# c = Color.from_hsv(119, 75, 100)
# c = Color.from_hsl(119, 100, 63)
# print(f'{c!r}')
# print(f'{c.hsv}')
# print(f'{c.hsl}')
#
# c = Color.from_hsv(20, 75, 100)
# c = Color.from_hsl(20, 100, 63)
# print(f'{c!r}')
# print(f'{c.hsv}')
# print(f'{c.hsl}')
#
# c = Color.from_hsv(212, 94, 100)
# c = Color.from_hsl(212, 100, 53)
# print(f'{c!r}')
# print(f'{c.hsv}')
# print(f'{c.hsl}')
#
# c = Color.from_hsv(300, 50, 100)
# c = Color.from_hsl(300, 100, 75)
# print(f'{c!r}')
# print(f'{c.hsv}')
# print(f'{c.hsl}')
#
# c = Color.from_hsv(60, 50, 100)
# c = Color.from_hsl(60, 100, 75)
# print(f'{c!r}')
# print(f'{c.hsv}')
# print(f'{c.hsl}')
#
# c = Color.from_hsv(180, 50, 100)
# c = Color.from_hsl(180, 100, 75)
# print(f'{c!r}')
# print(f'{c.hsv}')
# print(f'{c.hsl}')

# from sys import getsizeof as sizeof
# c = Color(124, 25, 0, 10)
# print(repr(c))
# print(sizeof(c))
# print(sizeof(c._argb))

DecolorizePattern = re.compile(r'\|c[a-f0-9]{8}.*?\|r', re.DOTALL)
ColorPattern = re.compile(r'\|c[a-f0-9]{8}')


def _decolorize_repl(match: re.Match) -> str:
    return match.group()[10:-2]


def decolorize(string: str) -> str:
    return DecolorizePattern.sub(_decolorize_repl, string)


# print(decolorize(
#     '''
# Created by |cff80ccffvk.com/prometheus3375|r.
# Contact me via Telegram: |cff80ccff@Prometheus3375|r.
#
# Special thanks:
# |cffff3333youtube.com/2kxaoc|r
# |cffccccccxgm.guru/p/wc3|r
#     '''
# ))
#
# print(decolorize(
#     '''
# Cost: |cffe2b007200|r Gold
# Income Gain: |cff76a5af+40|r
# Build Limit: |cff00ccff∞|r
#
# Attack
# Damage: |cff9933cc20|r Magical
# Cooldown: |cff00ccff2|r s
# Range: |cff00ccff3|r
# Max. Targets: |cff00ccff1|r
# Targets Allowed: All
# Explodes Targets: Yes
#     '''
# ))
#
# print(decolorize(
#     '''
# Switches from |cffcc80ccTower Mode|r back to the previous one.
#
# |cff00ff80Passive|r
# Every |cff00ccff6|r seconds gives to the selected tower |cff00ccff20%|r of the experience required to reaching its next level.
#
# |cffffcc80If the selected tower becomes sold or unable to be upgraded, the mode automatically switches to the previous one.
#
# The active effect of this ability applies to all selected Fountains of Experience with Tower Mode.|r
#     '''
# ))
