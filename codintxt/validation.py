from codintxt.m2t import model_2_codin, check_overlapping
from codintxt.language import build_model
from textx import TextXSemanticError


def validate_model_file(model_path: str):
    _model = build_model(model_path)
    _codin_json = model_2_codin(_model)
    overlap = check_overlapping(_codin_json)
    if overlap:
        raise TextXSemanticError("Overlapping of visual components!!")
