from typing import List, Dict, Tuple, Callable, Any, Optional

from typing import List, Callable, Type

import ipywidgets.widgets as widgets

from labext.modules import Module
from labext.widget import WidgetWrapper
from labext.widgets.button import Button

class Icon(WidgetWrapper):
    def __init__(self, fontawesome_icon: str):
        """Clickable icon

        Parameters
        ----------
        fontawesome_icon: str
            icon string from the fontawesome https://fontawesome.com. For example, "fab fa-500px"
        """
        self.el_icon = widgets.HTML(value=f'<i class="{fontawesome_icon}"></i>')
        