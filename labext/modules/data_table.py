import os
from pathlib import Path
from typing import List, Dict, Type

import requests

from labext.module import Module
from labext.modules.jquery import JQuery


class DataTable(Module):
    args = {
        "index": True,
        "escape": True,
        "border": 0,
        "justify": "left",
        "classes": ['table', 'table-striped', 'table-bordered']
    }

    @classmethod
    def set_args(cls, **kwargs):
        cls.args.update(**kwargs)

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
    def register(cls):
        super().register()

        import pandas as pd
        def _repr_datatable_(self):
            """Return DataTable representation of pandas DataFrame."""
            # create table DOM
            # script = f'$(element).html(`{self.to_html(**cls.args)}`);\n'
            # execute jQuery to turn table into DataTable
            script = f"""
require(["{cls.id()}", "{JQuery.id()}"], function(dataTables, jquery) {{
    jquery(element).html(`{self.to_html(**cls.args)}`);
    jquery(document).ready( () => {{
        // Turn existing table into datatable
        jquery(element).find("table.dataframe").DataTable({{
            "lengthMenu": [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]]
        }});
    }})
}});"""
            return script

        pd.DataFrame._repr_javascript_ = _repr_datatable_

    @classmethod
    def download(cls):
        localdir = super().download()
        (Path(localdir) / "images").mkdir(exist_ok=True)

        for static_file in ["sort_asc.png", "sort_both.png"]:
            with open(os.path.join(localdir, "images", static_file), "wb") as f:
                f.write(requests.get(f"https://cdn.datatables.net/1.10.19/images/{static_file}").content)
