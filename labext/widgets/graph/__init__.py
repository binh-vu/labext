import os
from dataclasses import dataclass
from enum import Enum
from operator import attrgetter
from pathlib import Path
from typing import Optional, Dict, List, Set
from uuid import uuid4

import ujson
from IPython.core.display import Javascript, HTML, display
from ipycallback import SlowTunnelWidget


class GraphWidget:
    def __init__(self, nodes, edges, config: Optional[dict] = None, dev: bool = False):
        self.dev = dev
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not dev:
            infile = os.path.join(current_dir, "main.js")
        else:
            infile = os.path.join(current_dir, "../build/static/js/main.js")
        
        with open(infile) as f:
            self.el_code = Javascript(f.read())

        self.tunnel = SlowTunnelWidget()
        self.el_container_id = str(uuid4())
        self.el_container = HTML(f'<div id="{self.el_container_id}"></div>')
        self.tunnel.on_receive(self.handle_incoming_msg)

        self.nodes = nodes
        self.edges = edges
        self.config = config or {"height": 500}
    
    def render(self):
        display(self.tunnel, self.el_code, self.el_container)
        display(Javascript(
            "window.%s('%s', window.IPyCallback.get('%s'))" % (
            'renderDevApp' if self.dev else 'renderApp', self.el_container_id, self.tunnel.tunnel_id)))

        self.tunnel.send_msg(ujson.dumps([
            {
                "type": "wait_for_client_ready",
            },
            {
                "type": "set_props",
                "props": {
                    "nodes": self.nodes,
                    "edges": self.edges,
                    "config": self.config
                }
            }
        ]))

    def handle_incoming_msg(self, version: int, msg: str):
        raise Exception(f"Unreachable!")
