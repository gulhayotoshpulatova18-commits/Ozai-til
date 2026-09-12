# -*- coding: utf-8 -*-
"""
O‘zAI TIL — yagona, mustaqil MVP/V4
Muallif: Gulhayo Toshpulatova
Bu fayl alohida linguistic_core.py ga bog‘liq emas.
"""
from collections import Counter
import re
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)
MUALLIF = "Gulhayo Toshpulatova"
VERSIYA = "O‘zAI TIL V4.0 — yakuniy MVP"

# O‘zbek tiliga xos asosiy qo‘shimchalar. Heuristik tahlil:
QOSHIMCHALAR = [
    "laringiz", "larimiz", "laring", "larim", "lar", "ning", "ni", "ga", "ka",
    "qa", "dan", "tan", "da", "ta", "bilan", "dek", "day", "cha", "kor",
    "dor", "siz", "li", "lik", "chi", "la", "lan", "lashtir", "lash",
    "roq", "gina", "ku", "mi", "man", "san", "miz", "siz", "dir",
    "im", "ing", "i", "si", "imiz", "ingiz", "lari"
]
QOSHIMCHA_TARTIB = sorted(set(QOSHIMCHALAR), key=len, reverse=True)

SOZ_TURKUMLARI = {
    "va","ham","yoki","ammo","lekin","bilan","uchun","chunki","agar","shuning",
    "bu","shu","u","men","sen","siz","biz","ular","kim","nima","qanday","qaysi",
    "bir","ikki","uch","juda","eng","hamma","har","hech","emas","bor","yo‘q","yo'q"
}

IMLO_TAVSIYALAR = {
    "oqidim": "o‘qidim",
    "oqish": "o‘qish",
    "oqigan": "o‘qigan",
    "yuzimni": "yuzimni",
    "bismillahir": "bismillahir",
    "rohmanir": "rohmanir",
    "qilgin": "qilgin",
}

def to_lower(s):
    return s.lower().replace("’", "‘").replace("ʼ", "‘").replace("`", "‘")

def tokenize(text):
    return re.findall(r"[A-Za-zА-Яа-яЁёʻ‘’ʼ\-]+(?:[A-Za-zА-Яа-яЁёʻ‘’ʼ\-]+)?", text, flags=re.UNICODE)

def words_clean(text):
    return [w for w in tokenize(text) if re.search(r"[A-Za-zА-Яа-яЁё]", w)]

def split_sentences(text):
    parts = re.split(r"(?<=[.!?…])\s+|[\r\n]+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def morfologik_tahlil(soz):
    asl = soz
    kichik = to_lower(soz)
    ozak = kichik
    topilgan = []
    # Eng uzun qo‘shimchadan boshlab ketma-ket ajratish
    for _ in range(4):
        topildi = False
        for q in QOSHIMCHA_TARTIB:
            if len(ozak) - len(q) >= 2 and ozak.endswith(q):
                ozak = ozak[:-len(q)]
                topilgan.insert(0, q)
                topildi = True
                break
        if not topildi:
            break

    if kichik in SOZ_TURKUMLARI:
        turkum = "yordamchi/olmosh"
    elif re.search(r"(moq|mak|yap|yot|di|gan|adi|ydi|sin|ing|man|san|miz|siz)$", kichik):
        turkum = "fe’l"
    elif re.search(r"(li|siz|dor|kor|chan|bop)$", kichik):
        turkum = "sifat"
    elif kichik.isdigit():
        turkum = "son"
    elif kichik.endswith(("lik","chi")):
        turkum = "ot/yasama"
    elif kichik in {"men","sen","u","biz","siz","ular","bu","shu","o‘sha","usha"}:
        turkum = "olmosh"
    else:
        turkum = "ot/sifat"

    lemma = ozak if topilgan else kichik
    return {
        "so'z": asl,
        "lemma": lemma,
        "o'zak": ozak,
        "qo'shimchalar": topilgan,
        "turkum": turkum,
    }

def imlo_tekshir(words):
    xatolar = []
    for w in words:
        k = to_lower(w)
        if k in IMLO_TAVSIYALAR and IMLO_TAVSIYALAR[k] != k:
            xatolar.append({"so'z": w, "tavsiya": IMLO_TAVSIYALAR[k], "izoh": "Ehtimoliy imlo xatosi."})
    return xatolar

def tinish_tekshir(text):
    muammolar = []
    if re.search(r"\s+[,.!?;:]", text):
        muammolar.append("Tinish belgisidan oldin ortiqcha bo‘sh joy bor.")
    if re.search(r"[,.!?;:]{2,}", text):
        muammolar.append("Ketma-ket bir nechta tinish belgisi ishlatilgan.")
    if text.strip() and not re.search(r"[.!?…]$", text.strip()):
        muammolar.append("Matn oxirida yakunlovchi tinish belgisi yo‘q.")
    return muammolar

def takrorlar(words):
    c = Counter(to_lower(w) for w in words)
    return [{"so'z": w, "soni": n} for w,n in c.items() if n > 1]

def gap_tahlili(sentences):
    result = []
    for i, gap in enumerate(sentences, 1):
        ws = words_clean(gap)
        verbs = [w for w in ws if morfologik_tahlil(w)["turkum"] == "fe’l"]
        result.append({
            "gap": i, "matn": gap, "so'zlar_soni": len(ws),
            "fe'llar": verbs,
            "izoh": "Fe’l markazi aniqlangan." if verbs else "Fe’l aniq ajratilmadi; natija heuristik."
        })
    return result

def baholash(words, sentences, imlo, takror):
    n = len(words)
    if n == 0:
        return {"ball": 0, "so'z_boyligi": 0, "o'rtacha_gap_uzunligi": 0, "daraja": "Matn yo‘q"}
    noyob = len(set(to_lower(w) for w in words))
    boylik = round(noyob / n * 100, 1)
    avg = round(n / max(len(sentences), 1), 1)
    ball = 100
    ball -= min(30, len(imlo) * 5)
    ball -= min(15, max(0, len(takror) - 2) * 2)
    if n < 30: ball -= 10
    if len(sentences) < 2 and n >= 30: ball -= 5
    ball = max(0, min(100, ball))
    daraja = "Yaxshi" if ball >= 80 else "Qoniqarli" if ball >= 60 else "Takomillashtirish kerak"
    return {"ball": ball, "so'z_boyligi": boylik, "o'rtacha_gap_uzunligi": avg, "daraja": daraja}

def tahlil(matn):
    words = words_clean(matn)
    sentences = split_sentences(matn)
    chars = len(matn)
    unique = len(set(to_lower(w) for w in words))
    morph = [dict(id=i, **morfologik_tahlil(w)) for i,w in enumerate(words,1)]
    imlo = imlo_tekshir(words)
    tinish = tinish_tekshir(matn)
    takror = takrorlar(words)
    ishonch = 60
    if words: ishonch += 10
    if len(words) >= 5: ishonch += 10
    if len(sentences) >= 2: ishonch += 5
    if morph: ishonch += 10
    if len(words) >= 30: ishonch += 5
    ishonch = min(95, ishonch)
    return {
        "statistika": {
            "so'zlar_soni": len(words),
            "gaplar_soni": len(sentences),
            "belgilar_soni": chars,
            "noyob_so'zlar": unique,
            "o'rtacha_gap_uzunligi": round(len(words)/max(1,len(sentences)),1),
        },
        "so'z_tahlili": morph,
        "gap_tahlili": gap_tahlili(sentences),
        "imlo_xatolari": imlo,
        "tinish_belgisi": tinish,
        "takroriy_so'zlar": takror,
        "insho_bahosi": baholash(words, sentences, imlo, takror),
        "ishonchlilik": {
            "foiz": ishonch,
            "holat": "Yuqori" if ishonch >= 80 else "O‘rta"
        }
    }

HTML = r"""
<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>O‘zAI TIL — {{versiya}}</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f6fb;color:#172033;font-family:Arial,sans-serif}
main{max-width:1150px;margin:auto;padding:24px 16px 60px}header,.card{background:white;border-radius:18px;box-shadow:0 6px 24px rgba(0,0,0,.07)}
header{padding:26px;margin-bottom:18px}h1{margin:0 0 8px;font-size:30px}h2{margin:0 0 16px}
.sub,small{color:#667085}textarea{width:100%;min-height:240px;padding:16px;border:2px solid #dce3ed;border-radius:14px;font-size:17px;line-height:1.6;resize:vertical}
textarea:focus{outline:none;border-color:#6555e8}button{width:100%;margin-top:12px;padding:16px;border:0;border-radius:14px;background:#6555e8;color:#fff;font-size:18px;font-weight:bold;cursor:pointer}
.card{padding:22px;margin-top:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px}
.stat{padding:16px;background:#f5f3ff;border-radius:14px}.stat b{font-size:24px}.badge{display:inline-block;padding:7px 11px;border-radius:999px;background:#eef1f7;margin:3px}
.good{background:#effbf2;padding:13px;border-radius:12px}.err{background:#fff1f1;padding:13px;border-radius:12px;margin:8px 0}.warn{background:#fff8e8;padding:13px;border-radius:12px;margin:8px 0}
table{width:100%;border-collapse:collapse;display:block;overflow-x:auto}th,td{padding:9px;border-bottom:1px solid #edf0f5;text-align:left;white-space:nowrap}
.bar{height:12px;background:#e9eaf0;border-radius:8px;overflow:hidden}.bar>div{height:100%;background:#6555e8}
@media(max-width:650px){h1{font-size:24px}.card{padding:16px}}
</style></head><body><main>
<header><h1>O‘zAI TIL</h1><div class="sub">O‘zbek tili ko‘p funksiyali lingvistik tahlil tizimi</div>
<small>Muallif: {{muallif}} · {{versiya}}</small></header>
<form method="post"><textarea name="matn" placeholder="Matnni shu yerga kiriting...">{{matn}}</textarea><button>TAHLIL QILISH</button></form>
{% if natija %}
<div class="card"><h2>Umumiy natija</h2><div class="grid">
<div class="stat"><b>{{natija["statistika"]["so'zlar_soni"]}}</b><br>So‘zlar</div>
<div class="stat"><b>{{natija["statistika"]["gaplar_soni"]}}</b><br>Gaplar</div>
<div class="stat"><b>{{natija["statistika"]["belgilar_soni"]}}</b><br>Belgilar</div>
<div class="stat"><b>{{natija["statistika"]["noyob_so'zlar"]}}</b><br>Noyob so‘zlar</div>
<div class="stat"><b>{{natija["statistika"]["o'rtacha_gap_uzunligi"]}}</b><br>O‘rtacha gap</div></div></div>

<div class="card"><h2>Insho / matn bahosi</h2><div class="grid">
<div class="stat"><b>{{natija["insho_bahosi"]["ball"]}}</b><br>Umumiy ball / 100</div>
<div class="stat"><b>{{natija["insho_bahosi"]["so'z_boyligi"]}}%</b><br>Lug‘at xilma-xilligi</div>
<div class="stat"><b>{{natija["insho_bahosi"]["o'rtacha_gap_uzunligi"]}}</b><br>O‘rtacha gap</div>
<div class="stat"><b>{{natija["insho_bahosi"]["daraja"]}}</b><br>Daraja</div></div>
<div class="warn">Bu dastlabki avtomatik baho; rasmiy imtihon bali emas.</div></div>

<div class="card"><h2>Imlo tekshiruvi</h2>
{% if natija["imlo_xatolari"] %}{% for x in natija["imlo_xatolari"] %}<div class="err"><b>{{x["so'z"]}}</b> → <b>{{x.tavsiya}}</b><br><small>{{x.izoh}}</small></div>{% endfor %}
{% else %}<div class="good">Aniqlangan ehtimoliy imlo xatosi yo‘q.</div>{% endif %}</div>

<div class="card"><h2>Tinish belgilari</h2>
{% if natija["tinish_belgisi"] %}{% for x in natija["tinish_belgisi"] %}<div class="err">{{x}}</div>{% endfor %}
{% else %}<div class="good">Aniqlangan muammo yo‘q.</div>{% endif %}</div>

<div class="card"><h2>So‘zlarning morfologik tahlili</h2><table>
<tr><th>#</th><th>So‘z</th><th>Lemma</th><th>Turkum</th><th>O‘zak</th><th>Qo‘shimchalar</th></tr>
{% for x in natija["so'z_tahlili"] %}<tr><td>{{x.id}}</td><td>{{x["so'z"]}}</td><td>{{x.lemma}}</td><td>{{x.turkum}}</td><td>{{x["o'zak"]}}</td><td>{{x["qo'shimchalar"]|join(", ") if x["qo'shimchalar"] else "—"}}</td></tr>{% endfor %}
</table></div>

<div class="card"><h2>Gap tahlili</h2>{% for x in natija["gap_tahlili"] %}
<div class="warn"><b>{{x.gap}}-gap:</b> {{x.matn}}<br>So‘zlar: {{x["so'zlar_soni"]}} · Fe’llar:
{% if x["fe'llar"] %}{{x["fe'llar"]|join(", ")}}{% else %}aniqlanmadi{% endif %}<br><small>{{x.izoh}}</small></div>{% endfor %}</div>

<div class="card"><h2>Takroriy so‘zlar</h2>{% if natija["takroriy_so'zlar"] %}
{% for x in natija["takroriy_so'zlar"] %}<span class="badge">{{x["so'z"]}} — {{x.soni}} marta</span>{% endfor %}
{% else %}<div class="good">Takroriy so‘z aniqlanmadi.</div>{% endif %}</div>

<div class="card"><h2>Ishonchlilik</h2><p><b>{{natija["ishonchlilik"]["holat"]}}</b> — {{natija["ishonchlilik"]["foiz"]}}%</p>
<div class="bar"><div style="width:{{natija["ishonchlilik"]["foiz"]}}%"></div></div></div>
{% endif %}</main></body></html>
"""

@app.route("/", methods=["GET", "POST"])
def bosh_sahifa():
    matn = ""
    natija = None
    if request.method == "POST":
        matn = request.form.get("matn", "").strip()
        if matn:
            natija = tahlil(matn)
    return render_template_string(HTML, matn=matn, natija=natija, muallif=MUALLIF, versiya=VERSIYA)

@app.route("/api/tahlil", methods=["POST"])
def api_tahlil():
    data = request.get_json(silent=True) or {}
    matn = str(data.get("matn", "")).strip()
    if not matn:
        return jsonify({"xato": "Matn kiritilmagan."}), 400
    return jsonify(tahlil(matn))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

