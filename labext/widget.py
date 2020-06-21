from abc import abstractmethod, ABC
from typing import List, Type

from IPython.core.display import display

from labext.module import Module


class WidgetWrapper(ABC):

    @property
    @abstractmethod
    def widget(self):
        pass

    @staticmethod
    def required_modules() -> List[Type[Module]]:
        return []

    def display(self):
        """Should use this method to display the widget instead of directly displaying self.widget"""
        for m in self.required_modules():
            m.register()
        return display(self.widget)
