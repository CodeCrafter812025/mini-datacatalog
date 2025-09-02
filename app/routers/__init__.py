# app/routers/__init__.py  (موقتاً با این محتوا جایگزین کن)
from importlib import import_module
from pkgutil import iter_modules
import sys

def register_blueprints(app):
    package = __name__  # should be 'app.routers'
    found = []
    for finder, name, ispkg in iter_modules(__path__):
        if ispkg:
            continue
        fullname = f"{package}.{name}"
        found.append(fullname)
        try:
            module = import_module(fullname)
            for attr in ("bp", "blueprint"):
                bp = getattr(module, attr, None)
                if bp:
                    app.register_blueprint(bp)
                    print(f"registered blueprint from {fullname}", file=sys.stderr)
                    break
        except Exception as e:
            print(f"failed to import {fullname}: {e}", file=sys.stderr)
    print("auto-register scanned:", found, file=sys.stderr)

def init_app(app):
    register_blueprints(app)
