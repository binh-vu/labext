import logging
import os, csv
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional

from IPython.core.display import display
from ipyevents import Event
import ipywidgets.widgets as widgets


class Example(ABC):

    def render(self):
        """Rendering the example"""
        display(widgets.Label(value=str(self)))

    @property
    @abstractmethod
    def id(self) -> str:
        pass


class InteractiveLabeler(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def render_example(self, output_area: widgets.Output):
        """Render the current example"""
        pass

    @abstractmethod
    def has_next(self):
        """Has next example"""
        pass

    @abstractmethod
    def next(self):
        """Move to next example"""
        pass

    @abstractmethod
    def has_prev(self):
        """Has previous example"""
        pass

    @abstractmethod
    def prev(self):
        """Move to previous example"""
        pass

    @abstractmethod
    def receive_key(self, key, altKey: bool, ctrlKey: bool, shiftKey: bool, metaKey: bool):
        """Receive a pressed key from the keyboard"""
        pass

    def render(self):
        """Render the labeler"""
        # define the basic components
        output = widgets.Output()
        next_btn = widgets.Button(
            description='Next (n)',
            disabled=False,
            button_style='',
            icon='arrow-circle-right'  # (FontAwesome names without the `fa-` prefix)
        )
        prev_btn = widgets.Button(
            description='Previous (b)',
            disabled=False,
            button_style='',
            icon='arrow-circle-left'  # (FontAwesome names without the `fa-` prefix)
        )
        clear_btn = widgets.Button(
            description='Clear',
            disabled=False,
            button_style='',
            icon='eraser'
        )

        prev_btn.layout.margin = "3px 0 0 0"
        next_btn.layout.margin = "3px 0 0 8px"
        clear_btn.layout.margin = "3px 0 0 8px"

        prev_btn.disabled = not self.has_prev()
        next_btn.disabled = not self.has_next()

        self.prev_btn = prev_btn
        self.next_btn = next_btn
        self.clear_btn = clear_btn

        monitorbox = widgets.HTML(
            value='Keyboard Interaction: <span style="color: #d24829"><b>inactive</b></span> (mouse hover to activate)')
        monitorbox.layout.border = '1px solid #d24829'
        monitorbox.layout.padding = '2px 32px'
        monitorbox.layout.margin = "0 0 0 8px"

        # keyboard listener
        event_listener = Event(source=monitorbox, watched_events=['keydown', 'mouseenter', 'mouseleave'])

        def handle_keyboard_event(event):
            if event['type'] == 'mouseenter' or event['type'] == 'mouseleave':
                is_monitorbox_active = event['type'] == 'mouseenter'
                if is_monitorbox_active:
                    monitorbox.value = 'Keyboard Interaction: <span style="color: #79b549"><b>active</b></span> (mouse leave to deactivate)'
                    monitorbox.layout.border = '1px solid #79b549'
                else:
                    monitorbox.value = 'Keyboard Interaction: <span style="color: #d24829"><b>inactive</b></span> (mouse enter to activate)'
                    monitorbox.layout.border = '1px solid #d24829'
            else:
                # keydown event
                key = event['key']
                re_render = False
                if key == 'n':
                    # move to next example
                    if self.has_next():
                        re_render = True
                        self.next()
                        next_btn.disabled = not self.has_next()
                        prev_btn.disabled = not self.has_prev()
                elif key == 'b':
                    # move to previous example
                    if self.has_prev():
                        re_render = True
                        self.prev()
                        next_btn.disabled = not self.has_next()
                        prev_btn.disabled = not self.has_prev()
                else:
                    self.receive_key(key, event['altKey'], event['ctrlKey'], event['shiftKey'], event['metaKey'])

                if re_render:
                    self.render_example(output)

        def navigate(btn):
            re_render = False
            if btn == next_btn:
                # move to next example
                if self.has_next():
                    re_render = True
                    self.next()
                    prev_btn.disabled = not self.has_prev()
                    next_btn.disabled = not self.has_next()
            else:
                # move to previous example
                if self.has_prev():
                    re_render = True
                    self.prev()
                    prev_btn.disabled = not self.has_prev()
                    next_btn.disabled = not self.has_next()

            if re_render:
                self.render_example(output)

        # register the event
        event_listener.on_dom_event(handle_keyboard_event)
        next_btn.on_click(navigate)
        prev_btn.on_click(navigate)
        clear_btn.on_click(self.on_clear)
        # render the labeler
        container = widgets.HBox([prev_btn, next_btn, clear_btn, monitorbox])
        display(container, output)

        # render the example
        self.render_example(output)
        self.output_area = output

    def on_clear(self, btn):
        pass
