import os
from os.path import join, basename
from textx import get_children_of_type, metamodel_from_file
import jinja2
from pprint import pprint

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("jinjas/"), trim_blocks=True, lstrip_blocks=True
)

env_fe_tmpl = jinja_env.get_template("env_fe.jinja")

tctt_metamodel = metamodel_from_file('../grammar/syntax/tctt.tx')
_model = tctt_metamodel.model_from_file('../grammar/examples/test.tctt')
print(_model.sentry)
# print attributes of the model
pprint(vars(_model.sentry))
modelf = env_fe_tmpl.render(model=_model)
print(modelf)