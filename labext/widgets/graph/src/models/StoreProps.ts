import { Socket } from "../library";

export interface Node {
  id: string;
  label: string;
  // html to show in the popover
  popover?: string;
  x?: number;
  y?: number;
  type?: string;
  labelCfg?: object;
  style?: any;
  size?: number | number[];
}

export interface Edge {
  source: string;
  target: string;
  label: string;
  popover?: string;
}

export interface StoreProps {
  nodes: Node[],
  edges: Edge[],
  config: {
    height: number,
  }
}

export const deserialize = (socket: Socket, prop: string, data: any) => {
  return data;
}
