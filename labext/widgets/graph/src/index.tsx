import { Provider } from "mobx-react";
import React from "react";
import ReactDOM from "react-dom";
import { THEME } from "./env";
import {
  AppWrapper,
  RecordTunnel,
  ReplayTunnel,
  Socket,
  Store,
  Tunnel,
} from "./library";
import { deserialize } from "./models";

function renderApp(
  containerId: string,
  tunnel: Tunnel,
  defaultProps?: { [prop: string]: any }
) {
  if (defaultProps === undefined) {
    defaultProps = {};
  }

  let container = document.getElementById(containerId);
  if (container === null) {
    console.error("Invalid container id");
    return;
  }

  let enableLogging = true;
  let shadow = container.attachShadow({ mode: "open" });
  let socket = new Socket(tunnel, 60000, enableLogging);
  let store = new Store(socket, defaultProps as any, undefined, deserialize);

  store.setProps({ root: shadow });

  ReactDOM.render(
    <Provider store={store}>
      <AppWrapper socket={socket} store={store as any} />
    </Provider>,
    shadow
  );
}

// exposing the application for people to call it from outside
(window as any).renderApp = renderApp;
(window as any).renderDevApp = (
  containerId: string,
  tunnel: Tunnel,
  defaultProps?: { [prop: string]: any }
) => {
  let recordTunnel = new RecordTunnel(tunnel);
  (window as any).recordTunnel = recordTunnel;
  console.log("renderDev");
  renderApp(containerId, recordTunnel, defaultProps);
};

if (process.env.REACT_APP_DEV === "yes") {
  if (THEME === "dark") {
    (document.body as any).style = "background: black";
  }
  let hist = require("./replayDebugData").history;
  renderApp("root", new ReplayTunnel(hist));
}
