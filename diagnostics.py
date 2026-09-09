"""V5.6 — explainable diagnostics and confidence status."""
def confidence_status(row):
    # Status, not a numeric probability.
    evidence=[]
    if row.get("lemma") not in (None,"_"): evidence.append("lemma")
    if row.get("upos") not in (None,"X","_"): evidence.append("upos")
    if row.get("feats") not in (None,"_"): evidence.append("morphology")
    if row.get("deprel") not in (None,"dep","_"): evidence.append("dependency")
    if len(evidence)>=3: return "dalillar_yetarli"
    if evidence: return "qisman_dalil"
    return "noaniq"

def diagnostics(rows):
    out=[]
    for r in rows:
        out.append({"id":r["id"],"so‘z":r["form"],
                    "ishonchlilik_holati":confidence_status(r),
                    "dalillar_soni":sum(x not in (None,"_","X","dep") for x in
                                        [r.get("lemma"),r.get("upos"),r.get("feats"),r.get("deprel")])})
    return out
