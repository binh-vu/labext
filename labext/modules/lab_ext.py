from typing import List, Dict, Type, Callable

import ujson
from IPython.core.display import display, Javascript
from ipycallback import SlowTunnelWidget

from labext.module import Module
from string import Template


class LabExt(Module):
    """Module that provides basic functions and containers to widget wrappers in the `labext.widgets` packages.
    """
    version = "1.0"
    container = "LabExtContainer1292931"
    call_until_true = "__CallUntilReturnTrue_BV12__"
    # a global tunnel that one can use to dispatch event from JS to the server
    tunnel = SlowTunnelWidget(tunnel_id="LabExtTunnel1292931")
    tunnel_listeners = {}

    @classmethod
    def id(cls) -> str:
        return "misc_func"

    @classmethod
    def css(cls) -> List[str]:
        return []

    @classmethod
    def js(cls) -> Dict[str, str]:
        return {}
        # return {cls.id(): f"/custom/labext/{cls.id()}/js/misc_func.{cls.version}"}

    @classmethod
    def dependencies(cls) -> List[Type['Module']]:
        return []

    @classmethod
    def register(cls, use_local: bool = True, suppress_display: bool = False):
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
    
    // define a global tunnel
            """.strip()).substitute(
            container=cls.container,
            CallUntilTrue=cls.call_until_true)

        Module.registered_modules[cls.id()] = True
        display(cls.tunnel)

        if not suppress_display:
            display(Javascript(jscode))
            return
        return jscode

    @classmethod
    def on_receive_tunnel_msg(cls, version: int, msg: str):
        msg = ujson.loads(msg)
        cls.tunnel_listeners[msg['receiver']](version, msg['content'])

    @classmethod
    def add_listener(cls, id: str, cb: Callable[[int, any], None]):
        cls.tunnel_listeners[id] = cb


LabExt.tunnel.on_receive(LabExt.on_receive_tunnel_msg)