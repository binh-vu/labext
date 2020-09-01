from typing import Callable
from uuid import uuid4

from labext.modules import LabExt
from labext.tag import Tag
from labext.widget import WidgetWrapper
import ipywidgets as widgets


class Checkbox(WidgetWrapper):

    def __init__(self, value: bool=False, metadata: dict = None):
        self.el_id = "checkbox-" + str(uuid4())
        self.checkbox = Tag.input().attr(
            type="checkbox",
            onchange=f"window.IPyCallback.get('{LabExt.tunnel.tunnel_id}').send_msg(JSON.stringify({{ receiver: '{self.el_id}', content: {{ value: event.target.checked }} }}));")
        self.value = value
        if value:
            self.checkbox.attr(checked="1")

        self.el = widgets.HTML(self.checkbox.value())
        self.metadata = metadata or {}
        self.on_change_callback = None

        LabExt.add_listener(self.el_id, self.on_js_event)

    @property
    def widget(self):
        return self.el

    def refresh(self):
        self.el.value = self.checkbox.value()

    def check(self):
        self.checkbox.attr(checked="1")
        self.el.value = self.checkbox.value()
        self.value = True

    def uncheck(self):
        self.checkbox.attr(checked=None)
        self.el.value = self.checkbox.value()
        self.value = False

    def on_change(self, callback: Callable[['Checkbox'], None]):
        """Register for on click event"""
        self.on_change_callback = callback
        return self

    def on_js_event(self, _version: int, event: dict):
        """Handle the event that the JS fire"""
        self.value = event['value']
        self.on_change_callback(self)