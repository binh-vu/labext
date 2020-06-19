from typing import List, Dict, Type

from IPython.core.display import display, Javascript

from labext.module import Module


class MiscFunc(Module):

    call_until_return_true = "__CallUntilReturnTrue_BV12__"

    @classmethod
    def id(cls) -> str:
        return "misc_func"

    @classmethod
    def css(cls) -> List[str]:
        return []

    @classmethod
    def js(cls) -> Dict[str, str]:
        return {}

    @classmethod
    def dependencies(cls) -> List[Type['Module']]:
        return []

    @classmethod
    def register(cls, use_local: bool = True):
        jscode = f"""
if (window.{cls.call_until_return_true} === undefined) {{
    function {cls.call_until_return_true}(fn, timeout) {{
        setTimeout(function () {{
            if (!fn()) {{
                {cls.call_until_return_true}(fn, timeout);
            }}
        }}, timeout);
    }}
    window.{cls.call_until_return_true} = {cls.call_until_return_true}
}}"""
        display(Javascript(jscode))
        Module.registered_modules[cls.id()] = True

