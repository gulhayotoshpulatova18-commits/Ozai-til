"""V5.3 — strict model adapter contract.

Any future statistical/neural model must implement predict(text) and return
token-level fields. The wrapper validates the schema before serialization.
"""
from dataclasses import dataclass
from typing import Any

REQUIRED=("id","form","lemma","upos","xpos","feats","head","deprel","deps","misc")

@dataclass
class ModelAdapter:
    name: str = "unconnected"
    version: str = "0.0"

    def predict(self, text: str) -> dict:
        raise NotImplementedError("Haqiqiy model adapteri ulanmagan.")

def validate_rows(rows):
    errors=[]
    ids=[]
    for i,r in enumerate(rows,1):
        missing=[k for k in REQUIRED if k not in r]
        if missing: errors.append({"row":i,"type":"missing","fields":missing}); continue
        ids.append(r["id"])
        if not isinstance(r["id"],int): errors.append({"row":i,"type":"id_not_integer"})
        if not isinstance(r["head"],int): errors.append({"row":i,"type":"head_not_integer"})
        if r["head"]<0: errors.append({"row":i,"type":"negative_head"})
        if r["deprel"]=="root" and r["head"]!=0: errors.append({"row":i,"type":"root_head_must_be_zero"})
    if len(ids)!=len(set(ids)): errors.append({"type":"duplicate_id"})
    return errors

def serialize_conllu(text, rows):
    errors=validate_rows(rows)
    if errors: raise ValueError({"invalid_model_output":errors})
    out=["# sent_id = v5.3-1","# text = "+text]
    for r in rows:
        out.append("\t".join(str(r[k]) for k in REQUIRED))
    return "\n".join(out)+"\n"
