from typing import List, Dict, Tuple, Callable, Any, Optional, Type

from labext.module import Module
from labext.modules.jquery import JQuery


class Selectize(Module):
    @classmethod
    def id(cls) -> str:
        return "selectize"

    @classmethod
    def css(cls) -> List[str]:
        return ["//selectize.github.io/selectize.js/css/selectize.default.css"]

    @classmethod
    def js(cls) -> Dict[str, str]:
        return {cls.id(): '//selectize.github.io/selectize.js/js/selectize'}

    @classmethod
    def dependencies(cls) -> List[Type['Module']]:
        return [JQuery]