from typing import Any, Callable

import ipywidgets.widgets as widgets
from IPython.core.display import display


def slider(fn: Callable[[int], Any], min=0, max=10, step=1, clear_output: bool=True) -> None:
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
    clear_output: bool
        clear the output before each function call
    """
    # an output container
    output = widgets.Output()

    # define navigating buttons, slider, and index jumper
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

    jumper = widgets.Text(
        value=str(min),
        description=f'Index [{slider.min}, {slider.max}]',
        disabled=False
    )

    # define functions to interactive update the index
    def update_index(index: int):
        if index < slider.min or index > slider.max:
            print(f"[ERROR] Invalid index for the slider. Get {index} while range is [{slider.min}, {slider.max}]")
            return
        next_btn.disabled = index == slider.max
        prev_btn.disabled = index == slider.min
        slider.value = index
        jumper.value = str(index)

    def navigate(btn):
        with output:
            if btn == next_btn:
                update_index(slider.value + 1)
            elif btn == prev_btn:
                update_index(slider.value - 1)

    def on_slider_change(change):
        with output:
            if clear_output:
                output.clear_output()
            update_index(change['new'])
            fn(change['new'])

    def on_jumper_edit(change):
        jumper.value = "".join((c for c in change['new'] if c.isdigit()))

    def on_jumper_change(_sender):
        if jumper.value != "":
            update_index(int(jumper.value))

    next_btn.on_click(navigate)
    prev_btn.on_click(navigate)
    slider.observe(on_slider_change, names='value')
    jumper.observe(on_jumper_edit, names='value')
    jumper.on_submit(on_jumper_change)

    container = widgets.HBox([prev_btn, next_btn, slider, jumper])
    display(container, output)

    with output:
        fn(slider.value)
