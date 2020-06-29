from typing import Callable

import ipywidgets.widgets as widgets
from ipyevents import Event

from labext.widget import WidgetWrapper


class Icon(WidgetWrapper):

    def __init__(self, fontawesome_icon: str):
        """Clickable icon

        Parameters
        ----------
        fontawesome_icon: str
            icon string from the fontawesome https://fontawesome.com. For example, "fab fa-500px"
        """
        self.el_icon = widgets.HTML(value=f'<i class="{fontawesome_icon}"></i>')
        self.on_click_callback = lambda: 1
        self.event_listener = Event(source=self.el_icon, watched_events=['click'])
        self.event_listener.on_dom_event(self.fire_on_click_event)

    @property
    def widget(self):
        return self.el_icon

    def on_click(self, callback: Callable[[], None]):
        self.on_click_callback = callback

    def fire_on_click_event(self, event: dict):
        if event['type'] == 'click':
            self.on_click_callback()
