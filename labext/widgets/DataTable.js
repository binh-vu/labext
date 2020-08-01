class LabExtDataTable {
    constructor(jquery, container, tunnel, columns, table_style, options = {}) {
        this.$ = jquery;
        this.$container = container;
        this.tunnel = tunnel;
        this.columns = columns;
        this.table_style = table_style;
        this.options = Object.assign({ deferRender: true, serverSide: true }, options);
        this.isInitComplete = false;
        this.tunnel.send_msg(JSON.stringify({ "type": "status", "msg": "init_start" }));
    }
    render() {
        // now render the content
        let $tbl = $("<table></table>")
            .attr({ "class": this.table_style })
            .css({ "width": "100%" })
            .appendTo(this.$container.empty());
        $tbl.DataTable(Object.assign({ columns: this.columns, ajax: (data, callback, settings) => {
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
            }, initComplete: () => {
                this.isInitComplete = true;
                this.tunnel.send_msg(JSON.stringify({ "type": "status", "msg": "init_done" }));
            }, drawCallback: () => {
                if (this.isInitComplete) {
                    this.tunnel.send_msg(JSON.stringify({ "type": "status", "msg": "redraw_done" }));
                }
            } }, this.options));
    }
}
