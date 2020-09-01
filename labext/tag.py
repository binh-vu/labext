import re
from typing import *


class Tag:
    camel_reg = re.compile('.+?(?:(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z0-9])|$)')

    def __init__(self, tag: str, children: Union[str, 'Tag', List[Union[str, 'Tag']]]):
        self.tag = tag
        if not isinstance(children, list):
            children = [children]
        self.children = children
        self._styles = {}
        self._attrs = {}
        self._data = {}

    @staticmethod
    def span(children: Union[str, 'Tag', List[Union[str, 'Tag']]]=None):
        return Tag('span', children or [])

    @staticmethod
    def pre(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("pre", children or [])

    @staticmethod
    def code(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("code", children or [])

    @staticmethod
    def a(children: Union[str, 'Tag', List[Union[str, 'Tag']]]=None):
        return Tag("a", children or [])

    @staticmethod
    def ul(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("ul", children or [])

    @staticmethod
    def ol(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("ol", children or [])

    @staticmethod
    def li(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("li", children or [])

    @staticmethod
    def div(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("div", children or [])

    @staticmethod
    def p(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("p", children or [])

    @staticmethod
    def table(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("table", children or [])

    @staticmethod
    def thead(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("thead", children or [])

    @staticmethod
    def tbody(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("tbody", children or [])

    @staticmethod
    def tr(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("tr", children or [])

    @staticmethod
    def th(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("th", children or [])

    @staticmethod
    def td(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("td", children or [])

    @staticmethod
    def button(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("button", children or [])

    @staticmethod
    def label(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("label", children or [])

    @staticmethod
    def input(children: Union[str, 'Tag', List[Union[str, 'Tag']]] = None):
        return Tag("input", children or [])

    def clear_css(self):
        self._styles = {}
        return self

    def clear_attr(self):
        self._attrs = {}
        return self

    def clear_data(self):
        self._data = {}
        return self

    def css(self, **kwargs):
        for prop, value in kwargs.items():
            result = []
            for match in self.camel_reg.finditer(prop):
                result.append(match.group(0))
            prop = "-".join(result).lower()
            if value is None:
                if prop in self._styles:
                    self._styles.pop(prop)
            else:
                self._styles[prop] = value
        return self

    def attr(self, **kwargs):
        for prop, value in kwargs.items():
            if prop == "htmlClass":
                prop = 'class'
            elif prop == 'htmlFor':
                prop = 'for'
            else:
                result = []
                for match in self.camel_reg.finditer(prop):
                    result.append(match.group(0))
                prop = "-".join(result).lower()
            if value is None:
                if prop in self._attrs:
                    self._attrs.pop(prop)
            else:
                self._attrs[prop] = value
        return self

    def data(self, **kwargs):
        for prop, value in kwargs.items():
            result = []
            for match in self.camel_reg.finditer(prop):
                result.append(match.group(0))
            prop = "-".join(result).lower()

            if value is None:
                if prop in self._data:
                    self._data.pop(prop)
            else:
                self._data[prop] = value
        return self

    def add_child(self, x: Union[list, Union[str, 'Tag']]):
        if isinstance(x, list):
            self.children += x
        else:
            self.children.append(x)

    def get_attr(self, key, default=None):
        return self._attrs.get(key, default)

    def value(self):
        return str(self)

    def __str__(self):
        style = ''
        if len(self._styles) > 0:
            style = ";".join(f'{k}: {v}' for k, v in self._styles.items())
            style = f'style="{style}"'
        attrs = ''
        if len(self._attrs) > 0:
            attrs = " ".join([f'{k}="{v}"' for k, v in self._attrs.items()])
        data = ''
        if len(self._data) > 0:
            lst = []
            for k, v in self._data.items():
                v = v.replace('"', '&quot;')
                lst.append(f'data-{k}="{v}"')
            data = " ".join(lst)

        content = "".join([str(x) for x in self.children])
        return f"<{self.tag} {style} {attrs} {data}>{content}</{self.tag}>"

    def __repr__(self):
        return str(self)