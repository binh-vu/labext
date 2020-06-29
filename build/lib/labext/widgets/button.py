from typing import Callable

import ipywidgets.widgets as widgets
from ipyevents import Event

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
