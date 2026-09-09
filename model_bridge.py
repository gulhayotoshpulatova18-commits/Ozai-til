"""Bridge between a future model and the V5.3 contract."""
from model_adapter_contract import serialize_conllu, validate_rows

def convert_prediction(text, prediction):
    if not isinstance(prediction,dict) or "tokenlar" not in prediction:
        raise ValueError("Model chiqishida 'tokenlar' mavjud emas.")
    rows=prediction["tokenlar"]
    return {
        "valid": not bool(validate_rows(rows)),
        "errors": validate_rows(rows),
        "conllu": serialize_conllu(text,rows) if not validate_rows(rows) else None
    }
