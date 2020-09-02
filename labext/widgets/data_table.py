import os
from abc import abstractmethod, ABC
from pathlib import Path
from string import Template
from typing import Type, List, TYPE_CHECKING, Optional, Callable, Union
from uuid import uuid4

import ipywidgets.widgets as widgets
import ujson
from IPython.core.display import Javascript, display
from ipycallback import SlowTunnelWidget

if TYPE_CHECKING:
    # do this because pandas is optional
    from pandas import DataFrame

from labext.helpers import noarg_func, read_file, identity_func
from labext.widget import WidgetWrapper
import labext.modules as M


class ITable(ABC):
    """An (abstract) table that can be displayed using DataTable widget"""

    @abstractmethod
    def columns(self) -> List[str]:
        """Return list of column names"""
        pass

    @abstractmethod
    def size(self) -> int:
        """Return number of records in the table"""
        pass

    @abstractmethod
    def get_rows(self, start: int, end: int) -> List[list]:
        """Get the records from row start to end"""
        pass


class ITableDataFrame(ITable):
    def __init__(self, df: 'DataFrame'):
        self.df = df

    def columns(self) -> List[str]:
        return self.df.columns

    def size(self) -> int:
        return len(self.df.index)

    def get_rows(self, start: int, end: int) -> List[list]:
        return self.df[start:end].values.tolist()


class DataTable(WidgetWrapper):
    def __init__(self, tbl: Union['DataFrame', ITable], table_class: str= 'display', columns: Optional[Union[dict, List[dict]]]=None, table_id: Optional[str]=None, **kwargs):
        """Show the

        Parameters
        ----------
        tbl: Union[DataFrame, ITable]
            the data frame or an instance that implement the ITable class that we want to display
        table_class: str
            html classes for formatting the table's style: https://datatables.net/manual/styling/classes
        columns: Union[dict, List[dict]]
            custom definition for each column: https://datatables.net/reference/option/columns
        table_id: Optional[str]
            id of the table, manually giving the table an id helps reducing number of instances in the client
            as we store this data table in the client side to reduce the
        kwargs
            see the [examples](https://datatables.net/examples/index) and the [options](https://datatables.net/manual/options)
            the options will be passed directly to the client
        """
        if not isinstance(tbl, ITable):
            # this should be dataframe
            self.table = ITableDataFrame(tbl)
        else:
            self.table = tbl
        self.table_class = table_class
        base_defs = [{"title": name} for name in self.table.columns()]
        if columns is not None:
            if isinstance(columns, list):
                assert len(columns) == len(base_defs)
                for i in range(len(base_defs)):
                    assert isinstance(columns[i], dict)
                    base_defs[i].update(columns[i])
            else:
                assert isinstance(columns, dict)
                for i in range(len(base_defs)):
                    base_defs[i].update(columns)
        self.columns = base_defs

        self.table_id = table_id or str(uuid4())
        self.options = kwargs

        self.tunnel = SlowTunnelWidget(tunnel_id=self.table_id)
        self.tunnel.on_receive(self.on_receive_updates)
        self.el = widgets.HTML(value="")
        self.el_class_id = f"DataTable_{self.el.model_id}"
        self.el.add_class(self.el_class_id)

        # use pkg_resources instead of __file__ to support install package via `pip install -e .`
        jscode = read_file(Path(os.path.abspath(__file__)).parent / "DataTable.js")
        # jscode = read_file(pkg_resources.resource_filename("labext", "widgets/DataTable.js"))

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
                    //     jp-Cell-outputArea
                    //     jp-OutputArea-child
                    //     jp-OutputArea-output *
                    //     widgets-output *
                    //     jp-OutputArea *
                    //     jp-OutputArea-child
                    //     jp-OutputArea-output *
                    let ptr = el;
                    while (!ptr.parent().hasClass("jp-Cell-outputArea")) {
                        ptr.css('overflow-x', 'auto');
                        ptr.css('margin', '0px');
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
                                columns=ujson.dumps(self.columns),
                                table_class=self.table_class,
                                options=ujson.dumps(self.options))

        self.el_auxiliaries = [self.tunnel, Javascript(jscode)]
        self.init_complete = False
        self.init_complete_callback = noarg_func
        self.on_draw_complete_callback = noarg_func
        self.on_redraw_complete_callback = noarg_func
        self.transform = identity_func

    @property
    def widget(self):
        return self.el

    @staticmethod
    def required_modules() -> List[Type[M.Module]]:
        return [M.DataTable]

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

    def on_init_complete(self, callback = None):
        self.init_complete_callback = callback or noarg_func
        return self

    def on_draw_complete(self, callback = None):
        self.on_draw_complete_callback = callback
        return self

    def on_redraw_complete(self, callback = None):
        self.on_redraw_complete_callback = callback
        return self

    def set_transform_fn(self, transform: Callable[[list], list]):
        self.transform = transform
        return self

    def on_receive_updates(self, version: int, msg: str):
        msg = ujson.loads(msg)
        if msg['type'] == 'query':
            msg = msg['msg']
            n_records = self.table.size()
            resp = {
                "recordsTotal": n_records,
                "recordsFiltered": n_records,
                "data":  self.transform(self.table.get_rows(msg['start'], msg['start']+msg['length']))
            }
            self.tunnel.send_msg_with_version(version, ujson.dumps(resp))
        elif msg['type'] == 'status':
            msg = msg['msg']
            if msg == 'init_done':
                self.init_complete = True
                self.init_complete_callback()
                self.on_draw_complete_callback()
            elif msg == 'redraw_done':
                self.on_draw_complete_callback()
                self.on_redraw_complete_callback()
            # elif msg == 'init_start':
            #     pass

    def redraw(self):
        M.LabExt.tunnel.send_msg(ujson.dumps({
            "fn": f"window.{M.LabExt.container}.DataTable.get('{self.table_id}').draw();"
        }))
