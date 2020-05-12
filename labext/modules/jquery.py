from typing import List, Type, Dict

from labext.module import Module


class JQuery(Module):

    @classmethod
    def id(cls) -> str:
        return 'jquery'

    @classmethod
    def css(cls) -> List[str]:
        return []

    @classmethod
    def js(cls) -> Dict[str, str]:
        return {cls.id(): '//code.jquery.com/jquery-3.3.1.min'}

    @classmethod
    def dependencies(cls) -> List[Type['Module']]:
        return []
