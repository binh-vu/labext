import os
from pathlib import Path
from string import Template

import ipywidgets.widgets as widgets
import ujson
from IPython.core.display import Javascript
from ipycallback import SlowTunnelWidget
from pandas import DataFrame

from labext.helpers import read_file
from labext.widget import WidgetWrapper
import labext.modules as M


class DataTable(WidgetWrapper):
    def __init__(self, df: DataFrame, table_class: str='display', **kwargs):
        """Show the

        Parameters
        ----------
        df: DataFrame
            the data frame that we want to display
        table_class: str
            html classes for formatting the table's style: https://datatables.net/manual/styling/classes
        kwargs
            see the [examples](https://datatables.net/examples/index) and the [options](https://datatables.net/manual/options)
            the options will be passed directly to the client
        """
        self.df = df
        self.table_class = table_class
        self.options = kwargs

        self.tunnel = SlowTunnelWidget()
        self.tunnel.on_receive(self.on_receive_updates)
        self.el = widgets.HTML(value="")
        self.el_class_id = f"DataTable_{self.el.model_id}"
        self.el.add_class(self.el_class_id)

        jscode = read_file(Path(os.path.abspath(__file__)).parent / "DataTable.js")
        jscode += Template("""
            require(['$JQueryId'], function (jquery) {
                $CallUntilTrue(function () {
                    if (window.IPyCallback === undefined || window.IPyCallback.get("$tunnelId") === undefined) {
                        return false;
                    }
                    
                    let el = jquery(".$containerClassId > div.widget-html-content");
                    if (el.length === 0) {
                        return false;
                    }
                    
                    if (window.$container.DataTable === undefined) {
                        window.$container.DataTable = new Map();
                    }
                    
                    let model = new LabExtDataTable(
                        jquery, el, 
                        window.IPyCallback.get("$tunnelId"),
                        $columns,
                        "$table_class",
                        $options
                    );
                    model.render();
                    window.$container.DataTable.set("$modelId", model);

                    return true;
                }, 100);
            });
        """.strip()).substitute(JQueryId=M.JQuery.id(), CallUntilTrue=M.LabExt.call_until_true,
                                container=M.LabExt.container,
                                containerClassId=self.el_class_id,
                                modelId=self.el.model_id,
                                tunnelId=self.tunnel.model_id,
                                columns=ujson.dumps(self.df.columns.tolist()),
                                table_class=self.table_class,
                                options=ujson.dumps(self.options))

        self.el_auxiliaries = [self.tunnel, Javascript(jscode)]

    @property
    def widget(self):
        return self.el

    def get_auxiliary_components(self, *args) -> list:
        return self.el_auxiliaries

    def on_receive_updates(self, version: int, msg: str):
        msg = ujson.loads(msg)
        if msg['type'] == 'query':
            msg = msg['msg']
            resp = {
                "recordsTotal": len(self.df.index),
                "recordsFiltered": len(self.df.index),
                "data":  self.df[msg['start']:msg['start']+msg['length']].values.tolist()
            }
            self.tunnel.send_msg_with_version(version, ujson.dumps(resp))