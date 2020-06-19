from typing import List

import ipywidgets.widgets as widgets
from IPython.core.display import display, Javascript

from labext.modules import JQuery, Selectize, MiscFunc
from labext.widget import WidgetWrapper


class Selection(WidgetWrapper):

    def __init__(self, *args, **kwargs):
        self._widget = widgets.Select(*args, **kwargs)
        self.unique_class_id = f"IJ_selection_{self._widget.model_id}"
        self._widget.add_class(self.unique_class_id)

    @property
    def widget(self):
        return self._widget

    @staticmethod
    def required_modules():
        return [JQuery, Selectize, MiscFunc]

    def sync(self, fix_overflow: bool = True):
        jscode = f"""
require(["{JQuery.id()}", "{Selectize.id()}"], function ($, _) {{
    {MiscFunc.call_until_return_true}(function () {{
        // get the selection container
        var $el = $(".{self.unique_class_id}");
        if ($('select', $el).length == 0) {{
            return false;
        }}

        // make it looks beautiful
        $('select', $el).selectize();
        $('.selectize-control', $el).width('100%');
        
        if ({"true" if fix_overflow else "false"}) {{
            var $p = $el.parent();
            for (var i = 0; i < 64; i++) {{
                $p.css('overflow', 'inherit');
                if ($p.hasClass('jp-OutputArea') && $p.hasClass('jp-Cell-outputArea')) {{
                    break;
                }}
                $p = $p.parent();
            }}
        }}

        return true;
    }}, 100);
}}
"""
        display(Javascript(jscode))


class RecordedSelection:
    """
    Key is the key that we want to select the value
    Value is the value that we are going to select
    """

    def __init__(self, recorded_data: dict, key: str, options: List[str], label):
        self.recorded_data = recorded_data
        self.options = options
        self.key = key
        self.widget = Selection(
            options=[(x, i) for i, x in enumerate(options)],
            value=self.recorded_data.get(self.key, 0),
            description=label,
            disabled=False,
        )
        self.widget.widget.observe(self.update, names='value')

    def update(self, change):
        self.recorded_data[self.key] = change['new']

    def set_key(self, key):
        self.key = key
        return self

    def sync_value(self):
        self.widget.value = self.recorded_data.get(self.key, 0)
        return self
