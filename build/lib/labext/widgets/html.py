from typing import Callable

import ipywidgets.widgets as widgets
from ipyevents import Event

from labext.widget import WidgetWrapper


class HTML(WidgetWrapper):

    def __init__(self, html: str):
        self.el = widgets.HTML(value=html)
        self.on_click_callback = lambda: 1
        self.event_listener = Event(source=self.el, watched_events=['click'])
        self.event_listener.on_dom_event(self.fire_on_click_event)

    @property
    def widget(self):
        return self.el

    def on_click(self, callback: Callable[[], None]):
        self.on_click_callback = callback

    def fire_on_click_event(self, event: dict):
        if event['type'] == 'click':
            self.on_click_callback()
