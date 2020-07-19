import os
from pathlib import Path
from string import Template
from typing import Type, List, TYPE_CHECKING, Optional
from uuid import uuid4

import ipywidgets.widgets as widgets
import ujson
from IPython.core.display import Javascript, display
from ipycallback import SlowTunnelWidget

if TYPE_CHECKING:
    # do this because pandas is optional
    from pandas import DataFrame

from labext.helpers import read_file
from labext.widget import WidgetWrapper
import labext.modules as M


class DataTable(WidgetWrapper):
    def __init__(self, df: 'DataFrame', table_class: str='display', table_id: Optional[str]=None, **kwargs):
        """Show the

        Parameters
        ----------
        df: DataFrame
            the data frame that we want to display
        table_class: str
            html classes for formatting the table's style: https://datatables.net/manual/styling/classes
        table_id: Optional[str]
            id of the table, manually giving the table an id helps reducing number of instances in the client
            as we store this data table in the client side to reduce the
        kwargs
            see the [examples](https://datatables.net/examples/index) and the [options](https://datatables.net/manual/options)
            the options will be passed directly to the client
        """
        self.df = df
        self.table_class = table_class
        self.table_id = table_id or str(uuid4())
        self.options = kwargs

        self.tunnel = SlowTunnelWidget(tunnel_id=self.table_id)
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
                    
                    // fix the issue of horizontal scrolling (the size goes beyond the border as jupyter set overflow
                    // to be visible)
                    // DOM structure (* is the one we need to modify)
                    // jp-Cell-outputArea
                    // jp-OutputArea-child
                    // jp-OutputArea-output *
                    // widgets-output *
                    // jp-OutputArea *
                    // jp-OutputArea-child
                    // jp-OutputArea-output *
                    let ptr = el;
                    while (!ptr.parent().hasClass("jp-Cell-outputArea")) {
                        ptr.css('overflow-x', 'scroll');
                        ptr = ptr.parent();
                    }

                    if (window.$container.DataTable === undefined) {
                        window.$container.DataTable = new Map();
                    }
                    
                    let tunnel = window.IPyCallback.get("$tunnelId");
                    let model = new LabExtDataTable(
                        jquery, el, tunnel,
                        $columns, "$table_class", $options
                    );
                    model.render();
                    window.$container.DataTable.set("$tableId", model);
                    return true;
                }, 100);
            });
        """.strip()).substitute(JQueryId=M.JQuery.id(), CallUntilTrue=M.LabExt.call_until_true,
                                container=M.LabExt.container,
                                containerClassId=self.el_class_id,
                                tableId=self.table_id,
                                tunnelId=self.tunnel.tunnel_id,
                                columns=ujson.dumps(self.df.columns.tolist()),
                                table_class=self.table_class,
                                options=ujson.dumps(self.options))

        self.el_auxiliaries = [self.tunnel, Javascript(jscode)]

    @property
    def widget(self):
        return self.el

    @staticmethod
    def required_modules() -> List[Type[M.Module]]:
        return [M.DataTable, M.JQuery, M.LabExt]

    def get_auxiliary_components(self, *args) -> list:
        return self.el_auxiliaries

    def destroy(self):
        jscode = Template("""
                window.IPyCallback.delete("$tunnelId");
                window.$container.DataTable.delete("$tableId");
                """).substitute(
            tableId=self.table_id,
            tunnelId=self.tunnel.tunnel_id,
            container=M.LabExt.container,
        )
        display(Javascript(jscode))

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