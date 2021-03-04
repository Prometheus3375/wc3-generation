import re
from typing import final

from misclib.color import Color


@final
class WC3Color(Color):
    def apply(self, string: str, /) -> str:
        return f'|c{self.alpha:02x}{self.red:02x}{self.green:02x}{self.blue:02x}{string}|r'

    __call__ = apply


_DecolorizePattern = re.compile(r'\|c[a-f0-9]{8}.*?\|r', re.DOTALL)


def _decolorize_repl(match: re.Match, /) -> str:
    return match.group()[10:-2]


def decolorize(string: str, /) -> str:
    return _DecolorizePattern.sub(_decolorize_repl, string)


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
