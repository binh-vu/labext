import abc
from IPython.core.display import display, Javascript


class WidgetWrapper:

    @property
    @abc.abstractmethod
    def widget(self):
        pass

    @property
    @abc.abstractmethod
    def required_modules(self):
        pass

    def display(self):
        return display(self.widget)

    def js_modules(self):
        return ", ".join(f"'{m}'" for m in self.required_modules)