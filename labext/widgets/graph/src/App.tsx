import G6 from "@antv/g6";
import { timeStamp } from "console";
import { observer } from "mobx-react";
import React from "react";
import { THEME, THEME_CSS } from "./env";
import { Socket, Store } from "./library";
import { StoreProps } from "./models";

interface Props {
  socket: Socket;
  store: Store<StoreProps>;
}

interface State {
  loading: boolean;
}

@observer
export default class App extends React.Component<Props, State> {
  private container = React.createRef<HTMLDivElement>();
  private graphContainer = React.createRef<HTMLDivElement>();
  public state: State = { loading: false };
  private graph: any = undefined;

  get store() {
    return this.props.store!.props
  }

  componentDidMount = () => {
    this.renderGraph();
  }

  componentDidUpdate = () => {
    this.renderGraph();
  }

  fitToCanvas = (center?: boolean) => {
    if (this.graphContainer.current === null) {
      return;
    }
    let container = this.graphContainer.current;

    // follow the code in fitView & fitCenter
    let group = this.graph.get("group");
    group.resetMatrix();
    let bbox = group.getCanvasBBox();
    if (bbox.width === 0 || bbox.height === 0) return;
    // let graphWidth = this.graph.getWidth();
    let graphWidth = container.clientWidth;

    if (center === true) {
      this.graph.moveTo(graphWidth / 2 - bbox.width / 2, 10);
    } else {
      this.graph.moveTo(4, 10);
    }
    this.graph.changeSize(graphWidth, bbox.height + 20);
  }

  renderGraph = () => {
    if (this.graphContainer.current === null || this.store.config === undefined) {
      return;
    }

    let container = this.graphContainer.current;
    let config = this.store.config;

    if (this.graph !== undefined) {
      this.graph.clear();
    }

    this.graph = new G6.Graph({
      container: container,
      width: container.scrollWidth - 4,
      height: config.height,
      linkCenter: true,
      layout: {
          type: 'force',
          preventOverlap: true,
          linkDistance: 50,
          nodeSpacing: 70,
      },
      defaultEdge: {
          type: "quadratic",
          style: {
              stroke: "#ddd",
              endArrow: {
                  fill: "black",
                  path: G6.Arrow.triangle(6, 8, 15),
                  d: 15
              },
              opacity: 1,
          },
          labelCfg: {
              style: {
                  fill: 'black',
                  background: {
                      fill: "#ffffff",
                      stroke: "#9EC9FF",
                      padding: [2, 2, 2, 2],
                      radius: 2,
                  },
              },
          },
      },
      defaultNode: {},
      modes: {
          default: [
              "drag-canvas", "drag-node",
              {
                  type: 'activate-relations',
                  resetSelected: true,
              } as any
          ],
          edit: ["click-select"],
      },
      nodeStateStyles: {
          hover: {
              fill: "lightsteelblue",
          },
          active: {
              opacity: 1,
          },
          inactive: {
              opacity: 0.2,
          }
      },
      edgeStateStyles: {
          active: {
              stroke: 'black',
              opacity: 1,
          },
          inactive: {
              opacity: 0.2,
          }
      }
    });
    this.graph.data({
      nodes: this.store.nodes,
      edges: this.store.edges
    });
    this.graph.render();
    this.graph.on("node:click", (event: any) => {
        // this.showNode(event.item._cfg.model);
    });
    this.graph.on("edge:click", (event: any) => {
        // this.showEdge(event.item._cfg.model);
    });
  }

  render() {
    return (
      <div ref={this.container} className={`app-${THEME}`}>
        <style type="text/css">{THEME_CSS}</style>
        <div style={{ display: "none" }}>{this.props.store.version}</div>
        <div className="mb-2">
          <div ref={this.graphContainer} style={{border: '2px solid #ccc'}}>
          </div>
        </div>
      </div>
    );
  }
}
