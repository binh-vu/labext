import os, json
from pathlib import Path
from typing import List, Dict, Type

import requests
from IPython.core.display import display
from pandas import DataFrame

from labext.module import Module
from labext.modules.jquery import JQuery


class DataTable(Module):
    py_args = {
        "index": True,
        "escape": True,
        "border": 0,
        "justify": "left",
        "classes": ['table', 'table-striped', 'table-bordered'],
    }
    js_args = {}

    @classmethod
    def set_args(cls, **kwargs):
        cls.py_args.update(**kwargs)

    @classmethod
    def set_js_args(cls, **kwargs):
        cls.js_args.update(**kwargs)

    @classmethod
    def id(cls) -> str:
        return "data_table"

    @classmethod
    def css(cls) -> List[str]:
        return ["//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css"]

    @classmethod
    def js(cls) -> Dict[str, str]:
        return {cls.id(): "//cdn.datatables.net/1.10.19/js/jquery.dataTables.min"}

    @classmethod
    def dependencies(cls) -> List[Type['Module']]:
        return [JQuery]

    @classmethod
    def render(cls, df: DataFrame, *args, **kwargs):
        """Rendering a data frame"""
        from labext.widgets.data_table import DataTable
        dt = DataTable(df, *args, **kwargs)
        display(dt.widget, *dt.get_auxiliary_components())

    @classmethod
    def download(cls):
        localdir = super().download()
        (localdir / "images").mkdir(exist_ok=True)

        for static_file in ["sort_asc.png", "sort_desc.png", "sort_both.png"]:
            with open(str(localdir / "images" / static_file), "wb") as f:
                f.write(requests.get(f"https://cdn.datatables.net/1.10.19/images/{static_file}").content)
