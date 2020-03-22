from typing import List

from IPython.core.display import display, Javascript

JQuery = "jquery"
DataTable = "dataTable"
Selectize = "selectize"

IPywidgetLibs = {
    "remote": {
        DataTable: {
            "js": "//cdn.datatables.net/1.10.19/js/jquery.dataTables.min",
            "css": "//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css"
        },
        JQuery: {
            "js": '//code.jquery.com/jquery-3.3.1.min'
        },
        Selectize: {
            "js": '//selectize.github.io/selectize.js/js/selectize',
            "css": "//selectize.github.io/selectize.js/css/selectize.default.css"
        },
    },
    "local": {
        DataTable: {
            "js": "/static/components/ipywidgets_extra_libs/js/jquery.dataTables.min",
            "css": "/static/components/ipywidgets_extra_libs/js/jquery.dataTables.min"
        },
        JQuery: {
            "js": '/static/components/jquery/jquery.min'
        },
        Selectize: {
            "js": "/static/components/ipywidgets_extra_libs/js/selectize.min",
            "css": "//selectize.github.io/selectize.js/css/selectize.default.css"
        },
    }
}

REGISTERED_MODULES = set()


def register(modules: List[str], auto_use_local: bool=True):
    global IPywidgetLibs, REGISTERED_MODULES

    # not filtered the modules because we need to output the same code
    # modules = [m for m in modules if m not in REGISTERED_MODULES]
    if JQuery not in modules:
        modules.append(JQuery)
    REGISTERED_MODULES.update(modules)

    location = "remote"
    module_urls = [
        f"{m}: \"{IPywidgetLibs[location][m]['js']}\""
        for m in modules
    ]

    js = "require.config({ paths: {" + ",".join(module_urls) + " } });"

    request_css = []
    request_modules = []

    for m in modules:
        if 'css' in IPywidgetLibs[location][m]:
            request_css.append(f"""
if ($("head link#{m}-css-fds82j1").length == 0) {{
    $('head').append('<link rel="stylesheet" id="{m}-css-fds82j1" type="text/css" href="{IPywidgetLibs[location][m]['css']}" />');
}}
            """)
            request_modules.append(m)

    if len(request_css) > 0:
        request_css = '\n'.join(request_css)
        js += f"""
require([{', '.join(['"' + m + '"' for m in request_modules])}], function ({', '.join(request_modules)}) {{
    {request_css}
}});
        """

    js += """
function __CallUntilReturnTrue_BV12__(fn, timeout) {
    setTimeout(function () {
        if (!fn()) {
            __CallUntilReturnTrue_BV12__(fn, timeout);
        }
    }, timeout);
}
window.__CallUntilReturnTrue_BV12__ = __CallUntilReturnTrue_BV12__
    """
    display(Javascript(js))

    if DataTable in modules:
        import pandas as pd

        def _repr_datatable_(self):
            """Return DataTable representation of pandas DataFrame."""
            # classes for dataframe table (optional)
            classes = ['table', 'table-striped', 'table-bordered']

            # create table DOM
            script = (
                f'$(element).html(`{self.to_html(index=True, classes=classes, border=0, justify="left")}`);\n'
            )

            # execute jQuery to turn table into DataTable
            script += f"""
                require(["{DataTable}", "{JQuery}"], function(dataTables) {{
                    $(document).ready( () => {{
                        // Turn existing table into datatable
                        $(element).find("table.dataframe").DataTable();
                    }})
                }});
            """

            return script
        pd.DataFrame._repr_javascript_ = _repr_datatable_
