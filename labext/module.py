import json
import shutil
import os
from abc import ABC
from operator import itemgetter
from pathlib import Path
from typing import List, Dict, Type
from urllib.parse import urlparse

import requests
from IPython.core.display import display, Javascript
from jupyter_core.paths import jupyter_config_dir


class Module(ABC):
    registered_modules: Dict[str, Type['Module']] = {}

    @classmethod
    def id(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def css(cls) -> List[str]:
        raise NotImplementedError()

    @classmethod
    def js(cls) -> Dict[str, str]:
        raise NotImplementedError()

    @classmethod
    def dependencies(cls) -> List[Type['Module']]:
        raise NotImplementedError()

    @classmethod
    def flatten_dependencies(cls) -> List[Type['Module']]:
        deps = {}
        for m in cls.dependencies():
            deps[m.id()] = m
            deps.update(m.flatten_dependencies())

        return [v for k, v in sorted(deps.items(), key=itemgetter(0))]

    @classmethod
    def expose(cls, varname: str):
        """Expose the module to global scope"""
        jscode = f"require(['{cls.id()}'], function ({cls.id()}) {{ window.{varname} = {cls.id()} }});"
        display(Javascript(jscode))

    @classmethod
    def register(cls, use_local: bool = True):
        """Register a module to the current notebook. This function is safed to call repeatedly"""
        if use_local:
            cls.download()
            js = {k: cls.remap_urls[url] for k, url in cls.js().items()}
            css_files = [cls.remap_urls[url] for url in cls.css()]
        else:
            js = cls.js()
            css_files = cls.css()

        modules = [cls.id()]

        for m in cls.flatten_dependencies():
            modules.append(m.id())
            if m.id() in Module.registered_modules:
                continue

            dup_js = set(js.keys()).intersection(m.js().keys())
            assert len(dup_js) == 0, f"Duplicated js: {dup_js}"

            m.register(use_local)

        if len(js) > 0:
            jscode = "require.config({ paths: %s });\n" % json.dumps(js)
        else:
            jscode = ""

        if len(css_files) > 0:
            setup_css = [f"""    if (document.querySelector("head link#{cls.id()}-css-fds82j1") === null) {{"""]
            for file in css_files:
                setup_css.append(f"""
        var el = document.createElement("link");
        el.rel = "stylesheet";
        el.id = "{cls.id()}";
        el.type = "text/css";
        el.href = "{file}";
        document.head.appendChild(el);""".strip("\n"))
            setup_css.append("    }")

            jscode += "require([{str_modules}], function ({modules}) {{\n{setup_css}\n}});\n".format(
                str_modules=json.dumps(modules)[1:-1],
                modules=", ".join(modules),
                setup_css="\n".join(setup_css))

        display(Javascript(jscode))
        Module.registered_modules[cls.id()] = True

    @classmethod
    def is_registered(cls):
        """Test if the model has been registered"""
        return cls.id() in Module.registered_modules

    @classmethod
    def download(cls):
        """Download the component in order to make it offline"""
        localdir = cls.get_local_dir()
        (localdir / "js").mkdir(exist_ok=True, parents=True)
        (localdir / "css").mkdir(exist_ok=True, parents=True)

        cls.remap_urls = {}
        for fileid, url in cls.js().items():
            norm_url = url
            if norm_url.startswith("//"):
                norm_url = "https:" + norm_url
            if not norm_url.endswith(".js"):
                norm_url += ".js"

            filename = urlparse(norm_url).path.rsplit("/", 1)[1]
            filepath = str(localdir / "js" / filename)
            if not os.path.exists(filepath):
                with open(filepath, "wb") as f:
                    f.write(requests.get(norm_url).content)

            cls.remap_urls[url] = f"/custom/labext/{cls.id()}/js/{filename[:-3]}"

        for url in cls.css():
            norm_url = url
            if norm_url.startswith("//"):
                norm_url = "https:" + norm_url
            filename = urlparse(norm_url).path.rsplit("/", 1)[1]
            filepath = str(localdir / "css" / filename)
            if not os.path.exists(filepath):
                with open(filepath, "wb") as f:
                    f.write(requests.get(norm_url).content)

            cls.remap_urls[url] = f"/custom/labext/{cls.id()}/css/{filename}"
        return localdir

    @classmethod
    def clear_download(cls):
        localdir = cls.get_local_dir()
        if (localdir / "js").exists():
            shutil.rmtree(str(localdir / "js"))

        if (localdir / "css").exists():
            shutil.rmtree(str(localdir / "css"))

    @classmethod
    def get_local_dir(cls) -> Path:
        localdir = os.path.join(jupyter_config_dir(), "custom", "labext", cls.id())
        localdir = Path(localdir)
        return localdir