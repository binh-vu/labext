import json
from labext.modules.lab_ext import LabExt
from string import Template
from typing import List, Dict, Tuple, Callable, Any, Optional, Type

from IPython.core.display import display, Javascript
from ipycallback.slow_tunnel import SlowTunnelWidget

from labext.module import Module


class Tippy(Module):
    """
    By default, this module allows reload tippy content directly embedded in the attributes of elements

    Example:
        >>> Tippy.register()

        >>> display(HTML('<button data-tippy-content="<b>Hello</b> what are you doing" data-tippy-allowHTML="true">Text</button>'))

        >>> Tippy.render()
    """
    # Properties that can be set: https://atomiks.github.io/tippyjs/v6/all-props/#interactive
    tunnel = SlowTunnelWidget(tunnel_id="labext.tippy")

    @classmethod
    def id(cls) -> str:
        return "tippy"

    @classmethod
    def css(cls) -> List[str]:
        return ["https://unpkg.com/tippy.js@6.2.3/dist/tippy.css", "https://unpkg.com/tippy.js@6.2.3/themes/light.css"]

    @classmethod
    def js(cls) -> Dict[str, str]:
        return {"@popperjs/core": 'https://unpkg.com/@popperjs/core@2/dist/umd/popper.min',
                cls.id(): "https://unpkg.com/tippy.js@6/dist/tippy-bundle.umd.min"}

    @classmethod
    def dependencies(cls) -> List[Type['Module']]:
        return [LabExt]

    @classmethod
    def register(cls, use_local: bool = True, suppress_display: bool = False):
        result = super().register(use_local, suppress_display)
        jscode = Javascript(Template("""
        require(["@popperjs/core", "tippy"], function (popper, tippy) {
            $CallUntilTrue(function () {
                if (window.IPyCallback === undefined || window.IPyCallback.get("$tunnelId") === undefined) {
                    return false;
                }

                window.IPyCallback.get("$tunnelId").on_receive((version, payload) => {
                    let msg = JSON.parse(payload);
                    if (msg.params.appendTo !== undefined) {
                        msg.params.appendTo = document.querySelector(msg.params.appendTo);  
                    }
                    if (msg.params.debug !== undefined) {
                        window.tippy = tippy;
                        console.log("Tippy args:", `$${msg.selector} [data-tippy-content]`, msg.params);
                    }
                    if (msg.params.delayms !== undefined) {
                        setTimeout(() => {
                            tippy(`$${msg.selector} [data-tippy-content]`, msg.params);
                        }, msg.params.delayms);
                    } else {
                        tippy(`$${msg.selector} [data-tippy-content]`, msg.params);
                    }
                });
                return true;
            }, 100);
        });
                """).substitute(tunnelId=cls.tunnel.tunnel_id, CallUntilTrue=LabExt.call_until_true))
        display(cls.tunnel, jscode)
        return result

    @classmethod
    def render(cls, css_selector: str = "", params: dict = None):
        cls.tunnel.send_msg(json.dumps({
            "selector": css_selector,
            "params": params or {}
        }))
