from IPython.core.display import display
from ipywidgets import widgets


def display_row(*display_objects):
    outputs = [widgets.Output() for _ in display_objects]
    for output, display_object in zip(outputs, display_objects):
        with output:
            display(display_object)
    display(widgets.HBox(outputs))