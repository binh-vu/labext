from typing import Any, Callable, Optional

import ipywidgets.widgets as widgets
from IPython.core.display import display


def slider(fn: Callable[[int], Any], min=0, max=10, step=1, id2index: Optional[Callable[[str], Optional[int]]]=None, clear_output: bool=True) -> None:
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
    id2index: function
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

    index_jumper = widgets.Text(
        value=str(min),
        description=f'Index [{slider.min}, {slider.max}]',
        disabled=False
    )
    id_jumper = widgets.Text(
        value='',
        description=f'Enter ID',
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
        index_jumper.value = str(index)

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

    def on_index_jumper_edit(change):
        index_jumper.value = "".join((c for c in change['new'] if c.isdigit()))

    def on_index_jumper_change(_sender):
        if index_jumper.value != "":
            update_index(int(index_jumper.value))

    def on_id_jumper_change(_sender):
        assert id2index is not None
        idx = id2index(id_jumper.value.strip())
        if idx is not None:
            update_index(idx)

    next_btn.on_click(navigate)
    prev_btn.on_click(navigate)
    slider.observe(on_slider_change, names='value')
    index_jumper.observe(on_index_jumper_edit, names='value')
    index_jumper.on_submit(on_index_jumper_change)
    id_jumper.on_submit(on_id_jumper_change)

    container = [prev_btn, next_btn, slider, index_jumper]
    if id2index is not None:
        container.append(id_jumper)

    display(widgets.HBox(container), output)

    with output:
        fn(slider.value)
