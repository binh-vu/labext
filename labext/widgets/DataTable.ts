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

  isInitComplete: boolean;

  constructor(jquery: JQueryStatic,
              container: JQuery<HTMLElement>,
              tunnel: Tunnel,
              columns: object[],
              table_style: string,
              options: {} = {}) {
    this.$ = jquery;
    this.$container = container;
    this.tunnel = tunnel;
    this.columns = columns;

    this.table_style = table_style;
    this.options = {
      deferRender: true,
      serverSide: true,
      ...options
    };
    this.isInitComplete = false;

    this.tunnel.send_msg(JSON.stringify({"type": "status", "msg": "init_start"}));
  }

  render() {
    // now render the content
    let $tbl = $("<table></table>")
      .attr({"class": this.table_style})
      .css({"width": "100%"})
      .appendTo(this.$container.empty());

    ($tbl as any).DataTable({
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
}