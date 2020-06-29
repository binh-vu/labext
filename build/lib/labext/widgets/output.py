from typing import Callable, List, Type

import ipywidgets.widgets as widgets
from IPython.core.display import display, Javascript
from ipyevents import Event

from labext.modules import JQuery, Module, LabExt
from labext.widget import WidgetWrapper


class DataTableOutput(WidgetWrapper):
    """An output widget wrapper for data table class. Use this if you want horizontal scrolling work"""

    def __init__(self, fix_width: bool = False):
        # we need fix width as some widgets such as selection need to set the overflow of the cell output area to be visible??
        # hence, the width of this output need to be fixed
        self.fix_width = fix_width
        self.el = widgets.Output()
        self.unique_class_id = f"DataTableOutput_{self.el.model_id}"
        self.el.add_class(self.unique_class_id)

    @property
    def widget(self):
        return self.el

    @staticmethod
    def required_modules() -> List[Type[Module]]:
        return [JQuery, LabExt]

    def get_auxiliary_components(self, *args) -> list:
        if self.fix_width:
            return [Javascript(f"""
require(['{JQuery.id()}'], function ($) {{
    {LabExt.call_until_true}(function () {{
        var $el = $(".{self.unique_class_id}");
        if ($el.length == 0) {{
            return false;
        }}
        
        // set the width to be full of the output size
        var width = $(".jp-Notebook-cell").width() - 80;
        $el.css('width', width);
        return true;
    }}, 100);
}});
            """.strip())]

        return [Javascript(f"""
require(['{JQuery.id()}'], function ($) {{
    {LabExt.call_until_true}(function () {{
        var $el = $(".{self.unique_class_id}");
        if ($el.length == 0) {{
            return false;
        }}

        $el.css('overflow', 'inherit');
        $el.parent().css('overflow', 'inherit');
        return true;
    }}, 100);
}});
            """.strip())]
