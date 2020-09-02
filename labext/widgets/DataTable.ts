interface Tunnel {
  send_msg: (msg: string) => number;
  on_receive: (handler: (version: number, msg: string) => void) => void;
}

class LabExtDataTable {
  $: JQueryStatic;
  $container: JQuery<HTMLElement>;
  tunnel: Tunnel;

  // style of the table: https://datatables.net/manual/styling/classes
  table_style: string;
  // list of column names
  columns: object[];
  // init options for the DataTable plugin
  options: object;
  // caption of the table
  caption?: string;

  // the data table instance. use it for re-drawing the table
  dataTable?: any;
  isInitComplete: boolean;

  constructor(jquery: JQueryStatic,
              container: JQuery<HTMLElement>,
              tunnel: Tunnel,
              columns: object[],
              table_style: string,
              options: { [key: string]: any } = {}) {
    this.$ = jquery;
    this.$container = container;
    this.tunnel = tunnel;
    this.columns = columns;

    this.table_style = table_style;
    if (options.caption !== undefined) {
      this.caption = options.caption;
      delete options.caption;
    }

    this.options = {
      deferRender: true,
      serverSide: true,
      ...options
    };
    this.isInitComplete = false;

    this.tunnel.send_msg(JSON.stringify({"type": "status", "msg": "init_start"}));

    // some options take functions, so we need to create that function from string
    // enable $ for those functions to use
    var $ = jquery;
    var fn = undefined;

    for (let col of this.columns) {
      // https://datatables.net/reference/option/columns.createdCell
      if ((col as any).createdCell !== undefined) {
        eval("fn = " + (col as any).createdCell);
        (col as any).createdCell = fn;
      }
    }

    if ((this.options as any).createdRow !== undefined) {
      eval("fn = " + (this.options as any).createdRow);
      (this.options as any).createdRow = fn;
    }
  }

  render() {
    // now render the content
    let $tbl = this.$(`<table>${this.caption || ""}</table>`)
      .attr({"class": this.table_style})
      .css({"width": "100%"})
      .appendTo(this.$container.empty());

    this.dataTable = ($tbl as any).DataTable({
      columns: this.columns,
      ajax: (data: any, callback: any, settings: any) => {
        // documentation in here: https://datatables.net/manual/server-side
        let version = this.tunnel.send_msg(JSON.stringify({
          type: "query",
          msg: {
            start: data.start || 0,
            length: data.length || 10,
          }
        }));

        this.tunnel.on_receive((returned_version, msg) => {
          if (returned_version !== version) {
            return;
          }

          let resp = JSON.parse(msg);
          callback({
            recordsTotal: resp.recordsTotal,
            recordsFiltered: resp.recordsFiltered,
            data: resp.data
          });
        });
      },
      initComplete: () => {
        this.isInitComplete = true;
        this.tunnel.send_msg(JSON.stringify({"type": "status", "msg": "init_done"}));
      },
      drawCallback: () => {
        if (this.isInitComplete) {
          this.tunnel.send_msg(JSON.stringify({"type": "status", "msg": "redraw_done"}));
        }
      },
      ...this.options
    });
  }

  draw() {
    // redraw the table: https://datatables.net/reference/api/draw()
    if (this.dataTable === undefined) return;
    this.dataTable.draw();
  }
}