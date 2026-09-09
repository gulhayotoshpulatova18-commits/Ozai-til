"""V5.5 — user-facing Uzbek explanation layer."""
CASE_UZ={"Gen":"qaratqich kelishigi","Dat":"jo‘nalish kelishigi","Acc":"tushum kelishigi","Loc":"o‘rin-payt kelishigi","Abl":"chiqish kelishigi"}
def explain_token(r):
    feats=r.get("feats","_")
    parts=[]
    if "Number=Plur" in feats: parts.append("ko‘plik")
    if "Poss" in feats: parts.append("egalik")
    for p in feats.split("|"):
        if p.startswith("Case="): parts.append(CASE_UZ.get(p.split("=",1)[1],"kelishik"))
    return {"so‘z":r.get("form",""),"lemma":r.get("lemma","_"),
            "so‘z_turkumi":r.get("upos","_"),"morfologik_belgilar":parts or ["belgi aniqlanmadi"],
            "bog‘lanish":{"bosh_so‘z_id":r.get("head"),"munosabat":r.get("deprel")}}
def explain(rows):
    return [explain_token(r) for r in rows]
