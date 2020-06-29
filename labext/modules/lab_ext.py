from typing import List, Dict, Type

from IPython.core.display import display, Javascript

from labext.module import Module
from string import Template


class LabExt(Module):
    """Module that provides basic functions and containers to widget wrappers in the `labext.widgets` packages.
    """

    container = "LabExtContainer1292931"
    call_until_true = "__CallUntilReturnTrue_BV12__"

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
        jscode = Template("""
// create a container so that widget wrappers can use to store some information
if (window.$container === undefined) {
    window.$container = {};
}

// define call until return true function
if (window.$CallUntilTrue === undefined) {
    function $CallUntilTrue(fn, timeout) {
        setTimeout(function () {
            if (!fn()) {
                $CallUntilTrue(fn, timeout);
            }
        }, timeout);
    }
    window.$CallUntilTrue = $CallUntilTrue
}
        """.strip()).substitute(
            container=cls.container,
            CallUntilTrue=cls.call_until_true)

        display(Javascript(jscode))
        Module.registered_modules[cls.id()] = True
