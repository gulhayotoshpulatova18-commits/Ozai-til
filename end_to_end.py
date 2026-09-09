"""V5.6 — unified end-to-end pipeline."""
from linguistic_core import report
from model_bridge import convert_prediction
from uz_explainer import explain
from diagnostics import diagnostics

class BaselineProvider:
    name="uzbek-transparent-baseline"; version="5.6"
    def predict(self,text): return report(text)

def infer(text, provider=None):
    provider=provider or BaselineProvider()
    prediction=provider.predict(text)
    checked=convert_prediction(text,prediction)
    rows=prediction.get("tokenlar",[])
    return {"versiya":"V5.6","model":{"name":provider.name,"version":provider.version},
            "valid":checked["valid"],"errors":checked["errors"],
            "tokenlar":rows,"izohli_tahlil":explain(rows),
            "diagnostika":diagnostics(rows),"coNLL_U":checked["conllu"]}
