from abc import ABC, abstractmethod

import ipywidgets.widgets as widgets
from IPython.core.display import display
from ipyevents import Event


class Example(ABC):
    """An abstract class representing examples that will be annotated.
    """

    def render(self):
        """Rendering the example. Override this function to render the example in the way you want"""
        display(widgets.Label(value=str(self)))

    @property
    @abstractmethod
    def id(self) -> str:
        """Get id of this example"""
        pass


class Annotator(ABC):
    """Base annotator, provides basic functions to navigate examples and keyboard shortcuts
    """

    def __init__(self):
        # container for displaying example
        self.el_example_container = widgets.Output()

        # navigation buttons
        self.el_next_btn = widgets.Button(
            description='Next (n)',
            disabled=False,
            button_style='',
            icon='arrow-circle-right'  # (FontAwesome names without the `fa-` prefix)
        )
        self.el_prev_btn = widgets.Button(
            description='Previous (b)',
            disabled=False,
            button_style='',
            icon='arrow-circle-left'  # (FontAwesome names without the `fa-` prefix)
        )

        self.el_prev_btn.layout.margin = "0px 0 0 0"
        self.el_next_btn.layout.margin = "0px 0 0 8px"

        self.el_next_btn.on_click(self.on_navigate)
        self.el_prev_btn.on_click(self.on_navigate)

        # status box telling if keyboard shortcut is activated
        self.el_status_box = widgets.HTML(
            value='Keyboard Interaction: <span style="color: #d24829"><b>inactive</b></span> (mouse hover to activate)')
        self.el_status_box.layout.margin = "0 0 0 8px"

        # now define the DOM tree for the annotator
        # root is the top component
        self.el_root = widgets.Output()
        self.el_root.layout.border = '1px solid #d24829'
        self.el_root.layout.padding = '2px'
        self.el_root.layout.margin = "0 0 0 -2px"

        self.el_root_children = (
            widgets.HBox([self.el_prev_btn, self.el_next_btn, self.el_status_box]),
            self.el_example_container
        )

        # add keyboard listener
        self.event_listener = Event(source=self.el_root, watched_events=['keydown', 'mouseenter', 'mouseleave'])
        self.event_listener.on_dom_event(self.on_mouse_key_event)

    @abstractmethod
    def render_example(self):
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
        """Render this annotator. This method should only be called once"""
        with self.el_root:
            self.el_root.clear_output()
            display(*self.el_root_children)

        display(self.el_root)
        self.sync_navigator()
        self.render_example()

    def on_mouse_key_event(self, event: dict):
        """Handling keyboard and mouse events to support keyboard shortcut

        Parameters
        ----------
        event: dict
            the event fired from ipyevents
        """
        if event['type'] == 'mouseenter' or event['type'] == 'mouseleave':
            # update the status box to show that keyboard capturing is activated when mouse is over the annotator component
            is_monitorbox_active = event['type'] == 'mouseenter'
            if is_monitorbox_active:
                self.el_status_box.value = 'Keyboard Interaction: <span style="color: #79b549"><b>active</b></span> (mouse leave to deactivate)'
                self.el_root.layout.border = '1px solid #79b549'
            else:
                self.el_status_box.value = 'Keyboard Interaction: <span style="color: #d24829"><b>inactive</b></span> (mouse enter to activate)'
                self.el_root.layout.border = '1px solid #d24829'
        else:
            # handling keyboard event
            key = event['key']
            re_render = False
            if key == 'n':
                # move to next example
                if self.has_next():
                    re_render = True
                    self.next()
                    self.el_next_btn.disabled = not self.has_next()
                    self.el_prev_btn.disabled = not self.has_prev()
            elif key == 'b':
                # move to previous example
                if self.has_prev():
                    re_render = True
                    self.prev()
                    self.el_next_btn.disabled = not self.has_next()
                    self.el_prev_btn.disabled = not self.has_prev()
            else:
                self.receive_key(key, event['altKey'], event['ctrlKey'], event['shiftKey'], event['metaKey'])

            if re_render:
                self.render_example()

    def on_navigate(self, btn: widgets.Button):
        re_render = False
        if btn == self.el_next_btn:
            # move to next example
            if self.has_next():
                re_render = True
                self.next()
                self.sync_navigator()
        else:
            # move to previous example
            if self.has_prev():
                re_render = True
                self.prev()
                self.sync_navigator()

        if re_render:
            self.render_example()

    def sync_navigator(self):
        """Synchronize the navigating buttons with the current data
        """
        self.el_prev_btn.disabled = not self.has_prev()
        self.el_next_btn.disabled = not self.has_next()
