"""V4.7 — Uzbek agglutinative morphology rule layer.

Transparent rules only; not a statistical model. Order is important because
Uzbek suffixes can stack. The rule inventory is intentionally conservative.
"""
import re

SUFFIX_GROUPS = {
    "case": ["ning","dan","dagi","ga","ka","qa","ni","da","ta"],
    "possessive": ["im","ing","i","si","imiz","ingiz","lari","si"],
    "plural": ["lar"],
    "person": ["man","san","miz","siz","lar"],
    "tense": ["moqda","yapti","yapman","yapsan","yapmiz","yapsiz","di","gan","adi","ar"],
}

def suffix_hits(word):
    x=word.lower()
    hits=[]
    # longest first to avoid splitting -dagi before -da, etc.
    for group,suffixes in SUFFIX_GROUPS.items():
        for suf in sorted(set(suffixes),key=len,reverse=True):
            if len(x)>len(suf)+1 and x.endswith(suf):
                hits.append({"group":group,"suffix":suf})
                break
    return hits

def morphological_features(word):
    hits=suffix_hits(word)
    groups={h["group"] for h in hits}
    feats=[]
    if "plural" in groups: feats.append("Number=Plur")
    if "possessive" in groups: feats.append("Poss")
    if "case" in groups:
        for h in hits:
            if h["group"]=="case":
                mapping={"ning":"Gen","dan":"Abl","ga":"Dat","ka":"Dat","qa":"Dat","ni":"Acc","da":"Loc","ta":"Loc","dagi":"Loc"}
                feats.append("Case="+mapping.get(h["suffix"],"Unknown"))
                break
    return "|".join(dict.fromkeys(feats)) if feats else "_"
