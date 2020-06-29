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

    def get_auxiliary_components(self, *args) -> list:
        return []
