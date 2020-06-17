import ipywidgets.widgets as widgets
from IPython.core.display import display


def interactive_slider(fn, min=0, max=10, step=1):
    next_btn = widgets.Button(
        description='Next',
        disabled=False,
        button_style='',
        icon='arrow-circle-right'  # (FontAwesome names without the `fa-` prefix)
    )
    prev_btn = widgets.Button(
        description='Previous',
        disabled=False,
        button_style='',
        icon='arrow-circle-left'  # (FontAwesome names without the `fa-` prefix)
    )
    space = widgets.HTML(value="<span style='margin-left: 8px' />")
    slider = widgets.IntSlider(value=min, min=min, max=max, step=step, continuous_update=False)
    container = widgets.HBox([prev_btn, space, next_btn, space, slider])
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
        fn(0)