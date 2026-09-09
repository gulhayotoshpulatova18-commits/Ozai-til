"""O‘zbek Tili AI V5.0 — unified linguistic core.

Transparent baseline core. It does not claim to be a trained neural model.
"""
import re
from uz_morphology_rules import morphological_features, suffix_hits
from uz_context_disambiguator import disambiguate_case

def tokenize(text):
    return re.findall(r"[^\W_]+(?:['ʻ’][^\W_]+)*|[^\w\s]", text, flags=re.UNICODE)

def lemma(form):
    x=form.lower()
    for suf in ("ning","larni","lar","dan","ga","ka","qa","ni","da","ta"):
        if len(x)>len(suf)+2 and x.endswith(suf): return x[:-len(suf)]
    return x

def upos(form):
    x=form.lower()
    if x in {"men","sen","u","biz","siz","ular"}: return "PRON"
    if x in {"va","yoki","ammo","lekin"}: return "CCONJ"
    if re.fullmatch(r"[.!?,:;…]",x): return "PUNCT"
    if x.isdigit(): return "NUM"
    if x.endswith(("di","dim","ding","dik","dingiz","dilar","yapti","moqda","moq")): return "VERB"
    if x.endswith(("li","siz","iy","viy")): return "ADJ"
    return "X"

def analyze(text):
    forms=tokenize(text)
    rows=[]
    for i,f in enumerate(forms,1):
        rows.append({"id":i,"form":f,"lemma":lemma(f),"upos":upos(f),
                     "xpos":"_","feats":morphological_features(f),
                     "head":0,"deprel":"dep","deps":"_","misc":"_"})
    root=next((r["id"] for r in rows if r["upos"]=="VERB"), rows[0]["id"] if rows else 0)
    for r in rows:
        r["head"]=0 if r["id"]==root else root
        r["deprel"]="root" if r["id"]==root else ("punct" if r["upos"]=="PUNCT" else "dep")
    return rows

def report(text):
    rows=analyze(text)
    return {
      "versiya":"V5.0",
      "matn":text,
      "tokenlar":rows,
      "kontekst_dalillari":[disambiguate_case(r["form"],
                              rows[i-1]["form"] if i else "",
                              rows[i+1]["form"] if i+1<len(rows) else "")
                            for i,r in enumerate(rows)],
      "coNLL_U":"\n".join([
        "# sent_id = v5-1","# text = "+text]+[
          "\t".join(str(r[k]) for k in ["id","form","lemma","upos","xpos","feats","head","deprel","deps","misc"])
          for r in rows])
    }
