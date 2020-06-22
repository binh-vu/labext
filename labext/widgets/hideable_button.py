from typing import List, Callable, Type

import ipywidgets.widgets as widgets

from labext.modules import Module
from labext.widget import WidgetWrapper
from labext.widgets.button import Button


class HideableButton(WidgetWrapper):
    def __init__(self, label: str, fn: Callable[[], None], show_event: str='click', default_visible: bool = False):
        """Hide and show the content

        Parameters
        ----------
        label: str
            label of the button
        fn: Callable[[], None]
            function that renders the content
        show_event: 'click' | 'hover'
            how the content will be shown
        default_visible: bool
            should the content show at first
        """
        self.el_btn = Button(description=label, disabled=False, button_style='')
        self.el_container = widgets.Output()

        if show_event == 'hover':
            self.el_btn.on_mouseenter(self._show)
            self.el_btn.on_mouseleave(self._hide)
        else:
            assert show_event == 'click'
            self.el_btn.on_click(self._on_toggle_visibility)

        if not default_visible:
            self._hide(None)
        else:
            self._show(None)

        self.el_root = widgets.VBox([self.el_btn.widget, self.el_container])
        with self.el_container:
            fn()

    @property
    def widget(self):
        return self.el_root

    @staticmethod
    def required_modules() -> List[Type[Module]]:
        return []

    def _show(self, _btn):
        """Show the content"""
        self.el_container.layout.display = 'inherit'
        self.el_btn.widget.button_style = 'success'
        self.is_shown = True

    def _hide(self, _btn):
        """Hide the content"""
        self.el_container.layout.display = 'none'
        self.el_btn.widget.button_style = ''
        self.is_shown = False

    def _on_toggle_visibility(self, _btn):
        """Toggle the visibility of the content"""
        if self.is_shown:
            self._hide(_btn)
        else:
            self._show(_btn)

