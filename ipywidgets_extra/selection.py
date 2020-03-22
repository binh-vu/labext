from typing import List

from ipywidgets_extra.widget_wrapper import WidgetWrapper
import ipywidgets_extra.modules as M

import ipywidgets.widgets as widgets
from IPython.core.display import display, Javascript


class Selection(WidgetWrapper):

    def __init__(self, *args, **kwargs):
        self._widget = widgets.Select(*args, **kwargs)
        self.unique_class_id = f"IJ_selection_{self._widget.model_id}"
        self._widget.add_class(self.unique_class_id)

    @property
    def widget(self):
        return self._widget

    @property
    def required_modules(self):
        return [M.JQuery, M.Selectize]

    def sync(self, fix_overflow: bool=True):
        js = f"""
    // get the selection container
    var $el = $(".{self.unique_class_id}");
    if ($('select', $el).length == 0) {{
        return false;
    }}

    // make it looks beautiful
    $('select', $el).selectize();
    $('.selectize-control', $el).width('100%');
        """
        if fix_overflow:
            js += """
    var $p = $el.parent();
    for (var i = 0; i < 64; i++) {
        $p.css('overflow', 'inherit');
        if ($p.hasClass('jp-OutputArea') && $p.hasClass('jp-Cell-outputArea')) {
            break;
        }
        $p = $p.parent();
    }
            """
        js += """
    return true;
        """
        js = """
__CallUntilReturnTrue_BV12__(function () {
    require([""" + self.js_modules() + """], function () {
        """ + js + """
    });
}, 100);
        """
        display(Javascript(js))


class RecordedSelection:
    """
    Key is the key that we want to select the value
    Value is the value that we are going to select
    """
    def __init__(self, recorded_data: dict, key: str, options: List[str], label):
        self.recorded_data = recorded_data
        self.options = options
        self.key = key
        self.selection = Selection(
            options=[(x, i) for i, x in enumerate(options)],
            value=self.recorded_data.get(self.key, 0),
            description=label,
            disabled=False,
        )
        self.selection.widget.observe(self.update, names='value')

    def update(self, change):
        self.recorded_data[self.key] = change['new']

    def set_key(self, key):
        self.key = key
        return self

    def sync_value(self):
        self.selection.value = self.recorded_data.get(self.key, 0)
        return self
