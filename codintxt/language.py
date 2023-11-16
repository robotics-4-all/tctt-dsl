import os
from os.path import join
from textx import language, metamodel_from_file, get_children_of_type, TextXSemanticError
import pathlib
import textx.scoping.providers as scoping_providers
from rich import print, pretty
from textx.scoping import ModelRepository, GlobalModelRepository
from codintxt.definitions import MODEL_REPO_PATH
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

pretty.install()

CURRENT_FPATH = pathlib.Path(__file__).parent.resolve()

GLOBAL_REPO = GlobalModelRepository()


def get_metamodel(debug=False) -> Any:
    metamodel = metamodel_from_file(
        CURRENT_FPATH.joinpath('grammar/codin.tx'),
        auto_init_attributes=True,
        global_repository=GLOBAL_REPO,
        debug=debug
    )

    metamodel.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(importAs=True),
            # "entities*": scoping_providers.FQNGlobalRepo(
            #     join(MODEL_REPO_PATH, 'entity', 'system_clock.smauto')
            # ),
        }
    )
    return metamodel


class Component(BaseModel):
    ctype: str
    name: str
    label: str
    topic: str
    broker: str
    position: Dict[str, Any]


class Gauge(Component):
    attribute: str
    minValue: int
    maxValue: int
    leftColor: str = ""
    rightColor: str = ""
    levels: int = 10
    hideTxt: bool = False
    unit: str = ""


class ValueDisplay(Component):
    attribute: str
    unit: str = ""


class JsonViewer(Component):
    attribute: str


class AliveDisplay(Component):
    timeout: int


class Button(Component):
    dynamic: bool = False
    color: str = ''
    background: str = ''
    hover: str = ''
    payload: Dict[str, Any]


class Broker(BaseModel):
    name: str
    btype: str
    host: str
    port: int
    auth: Dict[str, Any]


# Child class does not serialize. Workaround to use the BaseModel
class MQTTBroker(Broker):
    basePath: Optional[str] = ''
    webPath: Optional[str] = '/mqtt'
    webPort: Optional[int] = 8883


class CodinTxtModel(BaseModel):
    brokers: List[Any]
    components: List[Any]


def model_2_object(model):
    _brokers = []
    _components = []
    for broker in model.brokers:
        if broker.__class__.__name__ == 'MQTTBroker':
            br = MQTTBroker(
                name=broker.name,
                btype=broker.__class__.__name__,
                host=broker.host,
                port=broker.port,
                basePath=broker.basePath,
                webPath=broker.webPath,
                webPort=broker.webPort,
                auth={
                    'username': broker.auth.username,
                    'password': broker.auth.password,
                }
            )
        else:
            br = Broker(
                name=broker.name,
                btype=broker.__class__.__name__,
                host=broker.host,
                port=broker.port,
                auth={
                    'username': broker.auth.username,
                    'password': broker.auth.password,
                }
            )
        _brokers.append(br)
    for component in model.components:
        if component.__class__.__name__ == 'Gauge':
            cmp = Gauge(
                ctype='Gauge',
                name=component.name,
                label=component.label,
                topic=component.topic,
                broker=component.broker.name,
                attribute=component.attribute,
                minValue=component.minValue,
                maxValue=component.maxValue,
                leftColor=str(component.leftColor),
                rightColor=str(component.rightColor),
                levels=component.levels,
                hideTxt=component.hideTxt,
                unit=component.unit,
                position={
                    'x': component.position.x,
                    'y': component.position.y,
                    'w': component.position.w,
                    'h': component.position.h,
                }
            )
        elif component.__class__.__name__ == 'ValueDisplay':
            cmp = ValueDisplay(
                ctype='ValueDisplay',
                name=component.name,
                label=component.label,
                topic=component.topic,
                broker=component.broker.name,
                attribute=component.attribute,
                unit=component.unit,
                position={
                    'x': component.position.x,
                    'y': component.position.y,
                    'w': component.position.w,
                    'h': component.position.h,
                }
            )
        elif component.__class__.__name__ == 'JsonViewer':
            cmp = JsonViewer(
                ctype='JsonViewer',
                name=component.name,
                label=component.label,
                topic=component.topic,
                broker=component.broker.name,
                attribute=component.attribute,
                position={
                    'x': component.position.x,
                    'y': component.position.y,
                    'w': component.position.w,
                    'h': component.position.h,
                }
            )
        elif component.__class__.__name__ == 'AliveDisplay':
            cmp = AliveDisplay(
                ctype='AliveDisplay',
                name=component.name,
                label=component.label,
                topic=component.topic,
                broker=component.broker.name,
                timeout=component.timeout,
                position={
                    'x': component.position.x,
                    'y': component.position.y,
                    'w': component.position.w,
                    'h': component.position.h,
                }
            )
        elif component.__class__.__name__ == 'Button':
            cmp = Button(
                ctype='Button',
                name=component.name,
                label=component.label,
                topic=component.topic,
                broker=component.broker.name,
                dynamic=component.dynamic,
                color=str(component.color),
                background=str(component.bg),
                hover=str(component.hover),
                payload={attr.name: attr.default for attr in component.payload},
                position={
                    'x': component.position.x,
                    'y': component.position.y,
                    'w': component.position.w,
                    'h': component.position.h,
                }
            )
        else:
            continue
        _components.append(cmp)
    _model = CodinTxtModel(
        brokers=_brokers,
        components=_components,
    )
    return _model


def model_2_codin(model) -> Dict[str, Any]:
    _model = model_2_object(model)
    # print(_model)
    _json: Dict[str, Any] = model_2_json(model)
    codin_json: Dict[str, Any] = {
        "layout": [],
        "items": {}
    }

    colors = {
        'Red': "#ff0000",
        'Blue': "#00ff00",
        'Green': "#00ff00"
    }

    # Get the brokers
    brokers = {}
    for b in _json['brokers']:
        brokers[b['name']] = b

    # Get the components
    current_id = 0
    for c in _json["components"]:
        current_id += 1
        str_id = str(current_id)

        # Handle the layout
        l = {
            "i": str_id,
            "x": c['position']['x'],
            "y": c['position']['y'],
            "w": c['position']['w'],
            "h": c['position']['h'],
            "minW": 1,
            "minH": 1,
            "moved": False,
            "static": False,
        }
        codin_json['layout'].append(l)

        # Handle the config
        if c['ctype'] == "Gauge":
            config = {
                "type": "gauge",
                "name": c["name"],
                "source": c["broker"], # check this for duplicates
                "topic": c["topic"],
                "variable": c["attribute"],
                "minValue": c["minValue"],
                "maxValue": c["maxValue"],
                "leftColor": colors[c["leftColor"]],
                "rightColor": colors[c["rightColor"]],
                "levels": c["levels"],
                "hideText": c['hideTxt'],
                "unit": c['unit']
            }
            codin_json["items"][str_id] = config
        elif c['ctype'] == "ValueDisplay":
            config = {
                "type": "value",
                "name": c["name"],
                "source": c["broker"],
                "topic": c["topic"],
                "variable": c["attribute"],
                "unit": "%"
            }
            codin_json["items"][str_id] = config
        elif c['ctype'] == "JsonViewer":
            config = {
                "type": "json",
                "name": c["name"],
                "source": c["broker"],
                "topic": c["topic"],
                "variable": c["attribute"]
            }
            codin_json["items"][str_id] = config
        elif c['ctype'] == "AliveDisplay":
            config = {
                "type": "alive",
                "name": c["name"],
                "source": c["broker"],
                "topic": c['topic'],
                "timeout": c['timeout']
            }
            codin_json["items"][str_id] = config
        elif c['ctype'] == "Button":
            config = {
                "type": "buttons",
                "name": "Buttons",
                "alignText": "center",
                "buttonsAlign": "horizontal",
                "texts": [c['name']],
                "sources": [c["broker"]],
                "topics": [c['topic']],
                "payloads": [c['payload']],
                "isDynamic": [c['dynamic']],
                "colors": ["white" if c['color'] is None else c['color']],
                "backgrounds": ["#FF9D66" if c['background'] is None else c['background']],
                "backgroundsHover": ["#ff7e33" if c['hover'] is None else c['hover']]
            }
            codin_json["items"][str_id] = config

    overlap = check_overlapping(codin_json)
    if overlap:
        raise ValueError('Visual Component Overlapping issue!')
    return codin_json


def check_overlapping(codin_json: Dict[str, Any]):
    # Validation
    occupancy = {}
    failed = False
    msg = ""
    for element in codin_json["layout"]:
        for i in range(element["x"], element["x"] + element["w"] - 1):
            for j in range(element["y"], element["y"] + element["h"] - 1):
                if (i,j) in occupancy:
                    msg = f"Conflict between elements {element['i']} and {occupancy[(i,j)]} in place {(i,j)}"
                    failed = True
                    break
                else:
                    occupancy[(i,j)] = element['i']
            if failed:
                break
        if failed:
            break
    if failed == False:
        print("All good!")
    else:
        print("Overlapping issues!!")
    return failed


def model_2_json(model) -> Dict[str, Any]:
    _model = model_2_object(model)
    return _model.dict(exclude_unset=True)


def build_model(model_path: str, debug: bool = False):
    # Parse model
    mm = get_metamodel(debug=debug)
    model = mm.model_from_file(model_path)
    return model


def get_model_grammar(model_path):
    mm = get_metamodel()
    grammar_model = mm.grammar_model_from_file(model_path)
    return grammar_model


@language('codintxt', '*.codin')
def codintxt_language():
    "Codin Textual DSL"
    mm = get_metamodel()
    return mm
