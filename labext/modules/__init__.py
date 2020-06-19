from .jquery import *
from .data_table import *
from .misc_func import *
from .selectize import *
from .tippy import *


def register(modules: List[Type[Module]]):
    for m in modules:
        m.register()