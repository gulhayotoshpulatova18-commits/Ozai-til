# O'zbek tili AI — ko'p funksiyali lingvistik tahlil tizimi
# Muallif: Gulhayo Toshpulatova
# Versiya: V2.0
# Talab: Flask

import re
from collections import Counter
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

MUALLIF = "Gulhayo Toshpulatova"
VERSIYA = "V2.0"

YORDAMCHI = {
    "va", "ham", "yoki", "ammo", "lekin", "biroq", "chunki", "agar",
    "uchun", "bilan", "kabi", "sari", "qadar", "haqida", "orqali",
    "hamda", "ya'ni", "go'yo", "negaki", "shuning", "balki"
}

OLMOSHLAR = {
    "men", "sen", "u", "biz", "siz", "ular", "bu", "shu", "o'sha",
    "kim", "nima", "qaysi", "qanday", "qancha", "barcha", "har"
}

FE_L_QOSHIMCHALARI = (
    "yapman", "yapti", "yapmiz", "yapdi", "moqda", "moqchi",
    "dim", "ding", "di", "dik", "dingiz", "dilar",
    "gan", "kan", "qan", "sa", "sin", "man", "miz", "san", "siz",
    "adi", "ydi", "aman", "asan", "amiz", "asiz", "adilar"
)

KELISHIK = ("ning", "ni", "ga", "ka", "qa", "da", "ta", "dan", "tan")
EGALIK = ("im", "ing", "i", "si", "imiz", "ingiz", "lari")
KOPLIK = ("lar", "ler")
SOZ_YASOVCHI = (
    "chi", "kor", "zor", "li", "siz", "lik", "chilik",
    "dosh", "bon", "xona", "goh", "noma"
)

IMLO_ALMASHTIRISH = {
    "kup": "ko'p",
    "yuq": "yo'q",
    "yuk": "yo'q",
    "xamma": "hamma",
    "xech": "hech",
    "xozir": "hozir",
    "boladi": "bo'ladi",
    "qoshimcha": "qo'shimcha",
    "ozbek": "o'zbek",
}

def tokenize(text):
    return re.findall(
        r"[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳЗзʼ'‘’ʻ\-]+|\d+(?:[.,]\d+)?|[.!?;:,()\[\]{}\"“”]",
        text
    )

def words_only(text):
    return re.findall(
        r"[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳЗзʼ'‘’ʻ\-]+",
        text.lower()
    )

def sentences(text):
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", text.strip())
        if s.strip()
    ]

def normalize_word(word):
    return word.lower().strip(".,!?;:()[]{}\"“”‘’'")

def lemma(word):
    w = normalize_word(word)
    if not w:
        return ""
    result = w
    suffixes = sorted(
        set(KELISHIK + EGALIK + KOPLIK + SOZ_YASOVCHI),
        key=len,
        reverse=True
    )
    changed = True
    while changed and len(result) > 3:
        changed = False
        for suf in suffixes:
            if result.endswith(suf) and len(result) - len(suf) >= 3:
                result = result[:-len(suf)]
                changed = True
                break
    return result

def suffixes(word):
    w = normalize_word(word)
    if not w:
        return []
    found = []
    all_suffixes = sorted(
        set(KELISHIK + EGALIK + KOPLIK + SOZ_YASOVCHI),
        key=len,
        reverse=True
    )
    rest = w
    while len(rest) > 3:
        matched = None
        for suf in all_suffixes:
            if rest.endswith(suf) and len(rest) - len(suf) >= 3:
                matched = suf
                break
        if not matched:
            break
        found.insert(0, matched)
        rest = rest[:-len(matched)]
    return found

def pos(word):
    w = normalize_word(word)
    if not w:
        return "belgi"
    if w.isdigit():
        return "son"
    if w in OLMOSHLAR:
        return "olmosh"
    if w in YORDAMCHI:
        return "yordamchi"
    if w.endswith(FE_L_QOSHIMCHALARI):
        return "fe'l"
    if w.endswith(("lik", "chi", "kor", "zor", "li", "siz", "dosh")):
        return "ot/sifat"
    if w.endswith(("cha", "ona", "iy", "viy")):
        return "sifat"
    if w.endswith(("lab", "larcha")):
        return "ravish"
    return "noma'lum"

def word_analysis(text):
    out = []
    for i, w in enumerate(words_only(text), 1):
        sf = suffixes(w)
        root_len = len(w) - sum(len(x) for x in sf)
        out.append({
            "id": i,
            "so'z": w,
            "lemma": lemma(w),
            "turkum": pos(w),
            "qo'shimchalar": sf,
            "o'zak": w[:root_len] if root_len > 0 else w
        })
    return out

def spelling_errors(text):
    errors = []
    for m in re.finditer(
        r"\b[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳЗзʼ'‘’ʻ\-]+\b",
        text
    ):
        original = m.group(0)
        key = original.lower()
        if key in IMLO_ALMASHTIRISH:
            errors.append({
                "so'z": original,
                "tavsiya": IMLO_ALMASHTIRISH[key],
                "izoh": "Ehtimoliy imlo xatosi"
            })
    return errors

def punctuation_issues(text):
    issues = []
    if re.search(r"\s+[,.!?;:]", text):
        issues.append("Tinish belgisidan oldin ortiqcha bo'sh joy bor.")
    if re.search(r"[,.!?;:]{2,}", text):
        issues.append("Ketma-ket bir nechta tinish belgisi ishlatilgan.")
    if re.search(r"[!?]\w", text):
        issues.append("Tinish belgisidan keyin bo'sh joy kerak bo'lishi mumkin.")
    return issues

def repetitions(text):
    counts = Counter(words_only(text))
    return [
        {"so'z": w, "soni": n}
        for w, n in counts.most_common()
        if n > 1
    ]

def sentence_analysis(text):
    result = []
    for i, s in enumerate(sentences(text), 1):
        ws = words_only(s)
        verbs = [w for w in ws if pos(w) == "fe'l"]
        result.append({
            "gap": i,
            "matn": s,
            "so'zlar_soni": len(ws),
            "fe'llar": verbs,
            "predikativ_markaz": verbs[0] if verbs else None,
            "izoh": (
                "Fe'l markazi aniqlandi."
                if verbs else
                "Fe'l markazi avtomatik aniqlanmadi; qo'lda tekshirish tavsiya etiladi."
            )
        })
    return result

def essay_score(text):
    ws = words_only(text)
    ss = sentences(text)
    if not ws:
        return {
            "ball": 0,
            "daraja": "ma'lumot yetarli emas"
        }

    unique = len(set(ws))
    diversity = unique / len(ws)
    avg_sentence = len(ws) / max(len(ss), 1)

    score = 0
    score += min(25, len(ws) / 4)
    score += min(25, diversity * 35)
    score += min(20, len(ss) * 2)
    score += min(15, 15 if 8 <= avg_sentence <= 30 else 8)
    score += min(15, 15 if text.strip().endswith((".", "!", "?")) else 5)

    score = round(min(100, score), 1)

    if score >= 85:
        level = "juda yaxshi"
    elif score >= 70:
        level = "yaxshi"
    elif score >= 55:
        level = "o'rtacha"
    else:
        level = "takomillashtirish kerak"

    return {
        "ball": score,
        "daraja": level,
        "so'z_boyligi": round(diversity * 100, 1),
        "o'rtacha_gap_uzunligi": round(avg_sentence, 1),
        "eslatma": "Bu dastlabki avtomatik baho; rasmiy imtihon bali emas."
    }

def confidence(text, analyses):
    evidence = 0
    if len(analyses) >= 3:
        evidence += 1
    if len(words_only(text)) >= 10:
        evidence += 1
    if len(sentences(text)) >= 2:
        evidence += 1

    if evidence >= 3:
        return {"holat": "yuqori", "foiz": 90}
    if evidence == 2:
        return {"holat": "o'rtacha", "foiz": 75}
    if evidence == 1:
        return {"holat": "qisman", "foiz": 60}
    return {"holat": "noaniq", "foiz": 40}

def full_analysis(text):
    wa = word_analysis(text)
    ws = words_only(text)
    ss = sentences(text)

    return {
        "versiya": VERSIYA,
        "muallif": MUALLIF,
        "matn": text,
        "statistika": {
            "so'zlar_soni": len(ws),
            "gaplar_soni": len(ss),
            "belgilar_soni": len(text),
            "noyob_so'zlar": len(set(ws)),
            "o'rtacha_gap_uzunligi": round(
                len(ws) / max(len(ss), 1), 1
            )
        },
        "so'z_tahlili": wa,
        "gap_tahlili": sentence_analysis(text),
        "imlo_xatolari": spelling_errors(text),
        "tinish_belgisi": punctuation_issues(text),
        "takroriy_so'zlar": repetitions(text),
        "insho_bahosi": essay_score(text),
        "ishonchlilik": confidence(text, wa)
    }

SAHIFA = r"""
<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>O'zbek tili AI</title>
<style>
body{font-family:Arial,sans-serif;background:#f3f5fb;margin:0;color:#172033}
header{background:white;padding:24px;border-radius:0 0 24px 24px}
main{max-width:1000px;margin:24px auto;padding:0 16px}
textarea{width:100%;min-height:180px;padding:16px;border:1px solid #ddd;border-radius:16px;font-size:17px;box-sizing:border-box}
button{margin-top:12px;padding:14px 24px;border:0;border-radius:12px;background:#6555e8;color:white;font-size:16px;font-weight:bold}
.card{background:white;padding:20px;margin-top:16px;border-radius:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.stat{padding:16px;background:#f5f3ff;border-radius:14px}
.err{background:#fff1f1;padding:10px;border-radius:10px;margin:7px 0}
.ok{background:#effbf2;padding:10px;border-radius:10px}
table{width:100%;border-collapse:collapse}
td,th{padding:8px;border-bottom:1px solid #eee;text-align:left}
small{color:#667085}
</style>
</head>
<body>
<header>
<h1>O'zbek tili AI</h1>
<p>Ko'p funksiyali o'zbek tili lingvistik tahlil tizimi</p>
<small>Muallif: {{muallif}} · {{versiya}}</small>
</header>
<main>
<form method="post">
<textarea name="matn" placeholder="Matnni shu yerga kiriting...">{{matn}}</textarea>
<br>
<button type="submit">TAHLIL QILISH</button>
</form>

{% if natija %}
<div class="card">
<h2>Umumiy natija</h2>
<div class="grid">
<div class="stat"><b>{{natija.statistika["so'zlar_soni"]}}</b><br>So'zlar</div>
<div class="stat"><b>{{natija.statistika.gaplar_soni}}</b><br>Gaplar</div>

<div class="stat"><b>{{natija.ishonchlilik.foiz}}%</b><br>Ishonchlilik</div>
</div>
</div>
<div class="card">
<h2>Insho / matn bahosi</h2>
<p><b>{{natija.insho_bahosi.ball}} / 100</b> — {{natija.insho_bahosi.daraja}}</p>
<small>{{natija.insho_bahosi.eslatma}}</small>
</div>

<div class="card">
<h2>Imlo tekshiruvi</h2>
{% if natija.imlo_xatolari %}
{% for x in natija.imlo_xatolari %}
<div class="err"><b>{{x.so'z}}</b> → {{x.tavsiya}}<br><small>{{x.izoh}}</small></div>
{% endfor %}
{% else %}
<div class="ok">Aniqlangan ehtimoliy imlo xatosi yo'q.</div>
{% endif %}
</div>

<div class="card">
<h2>Tinish belgilari</h2>
{% if natija.tinish_belgisi %}
{% for x in natija.tinish_belgisi %}
<div class="err">{{x}}</div>
{% endfor %}
{% else %}
<div class="ok">Aniqlangan muammo yo'q.</div>
{% endif %}
</div>

<div class="card">
<h2>So'z tahlili</h2>
<table>
<tr><th>So'z</th><th>Lemma</th><th>Turkum</th><th>O'zak</th><th>Qo'shimchalar</th></tr>
{% for x in natija.so'z_tahlili %}
<tr>
<td>{{x.so'z}}</td>
<td>{{x.lemma}}</td>
<td>{{x.turkum}}</td>
<td>{{x["o'zak"]}}</td>
<td>{{x["qo'shimchalar"]|join(", ")}}</td>
</tr>
{% endfor %}
</table>
</div>

<div class="card">
<h2>Gap tahlili</h2>
{% for x in natija.gap_tahlili %}
<p>
<b>{{x.gap}}-gap:</b> {{x.matn}}<br>
So'zlar: {{x.so'zlar_soni}} ·
Fe'llar: {{x.fe'llar|join(", ") if x.fe'llar else "aniqlanmadi"}}<br>
<small>{{x.izoh}}</small>
</p>
{% endfor %}
</div>

<div class="card">
<h2>Takroriy so'zlar</h2>
{% if natija.takroriy_so'zlar %}
{% for x in natija.takroriy_so'zlar %}
{{x.so'z}} ({{x.soni}} marta) ·
{% endfor %}
{% else %}
<div class="ok">Takroriy so'z aniqlanmadi.</div>
{% endif %}
</div>
{% endif %}
</main>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def bosh_sahifa():
    matn = ""
    natija = None

    if request.method == "POST":
        matn = request.form.get("matn", "").strip()
        if matn:
            natija = full_analysis(matn)

    return render_template_string(
        SAHIFA,
        matn=matn,
        natija=natija,
        muallif=MUALLIF,
        versiya=VERSIYA
    )

@app.route("/api/tahlil", methods=["POST"])
def api_tahlil():
    data = request.get_json(silent=True) or {}
    matn = str(data.get("matn", "")).strip()

    if not matn:
        return jsonify({"xato": "Matn kiritilmagan."}), 400

    return jsonify(full_analysis(matn))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
