from typing import Callable
from uuid import uuid4

import ipywidgets.widgets as widgets
import ujson
from ipycallback import SlowTunnelWidget
from ipyevents import Event

from labext.modules import LabExt
from labext.tag import Tag
from labext.widget import WidgetWrapper


class Button(WidgetWrapper):
    """An extended button widget that support mouse over event.
    """

    def __init__(self, **kwargs):
        """Same constructor as `ipywidgets.widgets.Button`"""
        self.el_btn = widgets.Button(**kwargs)
        self.el_btn.on_click(self.fire_on_click_event)
        self.on_click_callback = lambda x: x
        self.on_mouseenter_callback = lambda x: x
        self.on_mouseleave_callback = lambda x: x

        self.event_listener = Event(source=self.el_btn, watched_events=['mouseenter', 'mouseleave'])
        self.event_listener.on_dom_event(self.fire_mouse_event)

    @property
    def widget(self):
        return self.el_btn

    def on_click(self, callback: Callable[['Button'], None]):
        """Register for on click event"""
        self.on_click_callback = callback

    def on_mouseenter(self, callback: Callable[['Button'], None]):
        """Register for on mouse enter event"""
        self.on_mouseenter_callback = callback

    def on_mouseleave(self, callback: Callable[['Button'], None]):
        """Register for on mouse leave event"""
        self.on_mouseleave_callback = callback

    def fire_on_click_event(self, _btn: widgets.Button):
        """Fire the on_click event when users click the button"""
        self.on_click_callback(self)

    def fire_mouse_event(self, event: dict):
        """Show the content on mouse over"""
        if event['type'] == 'mouseenter':
            self.on_mouseenter_callback(self)
        else:
            self.on_mouseleave_callback(self)


class HTMLButton(WidgetWrapper):

    def __init__(self, btn: Tag, metadata: dict = None):
        self.btn_id = "btn-" + str(uuid4())
        self.btn_cls = btn.get_attr("class", "")
        btn.attr(htmlClass=self.btn_cls + f" {self.btn_id}",
                 onclick=f"window.IPyCallback.get('{LabExt.tunnel.tunnel_id}').send_msg(JSON.stringify({{ receiver: '{self.btn_id}', content: {{ type: 'click' }} }}));")

        self.btn = btn
        self.el_btn = widgets.HTML(btn.value())
        self.metadata = metadata or {}
        self.on_click_callback = None

        LabExt.add_listener(self.btn_id, self.on_js_event)

    @property
    def widget(self):
        return self.el_btn

    def refresh_button(self):
        self.el_btn.value = self.btn.value()

    def on_click(self, callback: Callable[['HTMLButton'], None]):
        """Register for on click event"""
        self.on_click_callback = callback
        return self

    def on_js_event(self, _version: int, event: dict):
        """Handle the event that the JS fire"""
        if event['type'] == 'click':
            self.on_click_callback(self)
