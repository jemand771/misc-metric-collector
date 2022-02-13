import importlib.util
import inspect
import os
from pathlib import Path

from prometheus_client import make_wsgi_app
from prometheus_client.core import CollectorRegistry

from collector_base import CollectorBase, NotConfigured


def make_registry():
    classes = get_class_candidates()
    instances = try_init_classes(classes)
    registry = CollectorRegistry()
    for inst in instances:
        registry.register(inst)
    return registry


def get_class_candidates():
    classes = []
    for py_file in Path("collectors").glob("*.py"):
        spec = importlib.util.spec_from_file_location(py_file.name.rsplit(".", 1)[0], py_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and CollectorBase in obj.__bases__:
                classes.append(obj)
    return classes


def try_init_classes(classes):
    instances = []
    for class_ in classes:
        try:
            inst = class_(os.environ)
            instances.append(inst)
        except NotConfigured:
            pass
    return instances


app = make_wsgi_app(make_registry())
