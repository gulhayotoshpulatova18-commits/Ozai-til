"""V4.8 — conservative context layer for Uzbek morphology.

It does not claim full disambiguation. It adds explainable contextual evidence
and keeps ambiguous cases explicitly marked.
"""
import re

POSTPOSITIONS = {"bilan":"Instr","uchun":"Purp","haqida":"About","tomon":"Dir"}
COMMON_VERBS = {"bor","kel","ol","ber","qil","yoz","o‘qi","oqi","ko‘r","ayt","bil","ishla","yasa"}

def contextual_evidence(tokens):
    evidence=[]
    low=[t.lower() for t in tokens]
    for i,t in enumerate(low):
        if t in POSTPOSITIONS:
            evidence.append({"index":i,"signal":"postposition","value":POSTPOSITIONS[t]})
        if t.endswith(("ga","ka","qa")):
            evidence.append({"index":i,"signal":"case_candidate","value":"Dat"})
        if t.endswith(("ni",)):
            evidence.append({"index":i,"signal":"case_candidate","value":"Acc"})
        if t.endswith(("ning",)):
            evidence.append({"index":i,"signal":"case_candidate","value":"Gen"})
        if t.endswith(("da","ta")):
            evidence.append({"index":i,"signal":"case_candidate","value":"Loc"})
        if t.endswith(("dan",)):
            evidence.append({"index":i,"signal":"case_candidate","value":"Abl"})
    return evidence

def disambiguate_case(form, left="", right=""):
    """Return evidence, not a definitive label."""
    x=form.lower()
    if x.endswith(("ga","ka","qa")):
        if right.lower() in COMMON_VERBS:
            return {"candidate":"Dat","confidence_status":"evidence_only","reason":"fe'l oldidan yo‘nalish kandidati"}
        return {"candidate":"Dat","confidence_status":"ambiguous","reason":"qo‘shimcha shakli kontekst bilan tekshirilishi kerak"}
    return {"candidate":"_","confidence_status":"not_applicable","reason":""}
