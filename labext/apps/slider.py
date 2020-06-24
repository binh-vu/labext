from typing import Any, Callable

import ipywidgets.widgets as widgets
from IPython.core.display import display


def slider(fn: Callable[[int], Any], min=0, max=10, step=1) -> None:
    """Interactive slider. Useful for navigating a list of items/entities/tables

    Parameters
    ----------
    fn: Callable[[int], Any]
        a rendering function that render the item at a given position in the list
    min: int
        the start range of this slider
    max: int
        the stop range of this (inclusive)
    step: int
    """

    # define navigating buttons and slider
    prev_btn = widgets.Button(
        description='Previous',
        disabled=False,
        button_style='',
        icon='arrow-circle-left'  # (FontAwesome names without the `fa-` prefix)
    )
    next_btn = widgets.Button(
        description='Next',
        disabled=False,
        button_style='',
        icon='arrow-circle-right'  # (FontAwesome names without the `fa-` prefix)
    )
    next_btn.layout.margin = "0 0 0 8px"

    slider = widgets.IntSlider(value=min, min=min, max=max, step=step, continuous_update=False)
    slider.layout.margin = "0 0 0 8px"

    container = widgets.HBox([prev_btn, next_btn, slider])
    output = widgets.Output()

    display(container, output)

    def navigate(btn):
        with output:
            if btn == next_btn:
                slider.value += 1
            elif btn == prev_btn:
                slider.value -= 1

            next_btn.disabled = slider.value == slider.max
            prev_btn.disabled = slider.value == slider.min

    def on_change(change):
        with output:
            output.clear_output()
            next_btn.disabled = change['new'] == slider.max
            prev_btn.disabled = change['new'] == slider.min
            fn(change['new'])

    next_btn.on_click(navigate)
    prev_btn.on_click(navigate)
    slider.observe(on_change, names='value')

    with output:
        fn(slider.value)
