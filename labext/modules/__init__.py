from .jquery import *
from .data_table import *
from .lab_ext import *
from .selectize import *
from .tippy import *


def register(modules: List[Type[Module]]):
    jscodes = []
    for m in modules:
        jscode = m.register(suppress_display=True)
        jscodes.append(jscode)

    display(Javascript("\n".join(jscodes)))