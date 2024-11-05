from codintxt.m2t import model_2_codin
from codintxt.language import build_model
from textx import TextXSemanticError

def validate_model_file(model_path: str, check_overlap: bool = True):
    _model = build_model(model_path)
    if check_overlap:
        _codin_json = model_2_codin(_model)
