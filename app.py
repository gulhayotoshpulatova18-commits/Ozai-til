# -*- coding: utf-8 -*-

import re
from collections import Counter
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

MUALLIF = "Gulhayo Toshpulatova"
VERSIYA = "V3.0 — ko‘p funksiyali"

YORDAMCHI = {
    "va", "ham", "yoki", "ammo", "lekin", "biroq", "chunki",
    "agar", "uchun", "bilan", "kabi", "sari", "qadar", "haqida",
    "orqali", "hamda", "ya'ni", "go‘yo", "go'yo", "negaki", "balki"
}

OLMOSHLAR = {
    "men", "sen", "u", "biz", "siz", "ular", "bu", "shu", "o‘sha",
    "o'sha", "kim", "nima", "qaysi", "qanday", "qancha", "barcha", "har"
}

IMLO = {
    "kup": "ko‘p",
    "yuq": "yo‘q",
    "yuk": "yo‘q",
    "xamma": "hamma",
    "xech": "hech",
    "xozir": "hozir",
    "boladi": "bo‘ladi",
    "qoshimcha": "qo‘shimcha",
    "ozbek": "o‘zbek"
}

QOSHIMCHALAR = (
    "ning", "ingiz", "imiz", "lari", "lar", "dan", "tan",
    "dagi", "ni", "ga", "ka", "qa", "da", "ta",
    "im", "ing", "i", "si", "lik", "chi", "kor",
    "zor", "li", "siz", "dosh", "bon", "xona", "goh", "noma"
)

FEL_QOSHIMCHALARI = (
    "yapman", "yapti", "yapmiz", "yapdi", "moqda", "moqchi",
    "dim", "ding", "di", "dik", "dingiz", "dilar",
    "gan", "kan", "qan", "sa", "sin", "man", "miz",
    "san", "siz", "adi", "ydi", "aman", "asan",
    "amiz", "asiz", "adilar"
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


def normalize(word):
    return word.lower().strip(
        ".,!?;:()[]{}\"“”‘’'"
    )


def lemma(word):
    result = normalize(word)

    for suf in sorted(
        set(QOSHIMCHALAR),
        key=len,
        reverse=True
    ):
        while (
            len(result) > len(suf) + 3
            and result.endswith(suf)
        ):
            result = result[:-len(suf)]

    return result


def suffixes(word):
    rest = normalize(word)
    found = []

    for _ in range(6):

        matched = None

        for suf in sorted(
            set(QOSHIMCHALAR),
            key=len,
            reverse=True
        ):
            if (
                len(rest) > len(suf) + 2
                and rest.endswith(suf)
            ):
                matched = suf
                break

        if not matched:
            break

        found.insert(0, matched)
        rest = rest[:-len(matched)]

    return found, rest


def pos(word):

    w = normalize(word)

    if not w:
        return "belgi"

    if w.isdigit():
        return "son"

    if w in OLMOSHLAR:
        return "olmosh"

    if w in YORDAMCHI:
        return "yordamchi"

    if w.endswith(FEL_QOSHIMCHALARI):
        return "fe’l"

    if w.endswith(
        ("lik", "chi", "kor", "zor", "dosh")
    ):
        return "ot"

    if w.endswith(
        ("li", "siz", "iy", "viy", "cha")
    ):
        return "sifat"

    if w.endswith(
        ("lab", "larcha")
    ):
        return "ravish"

    return "noma’lum"


def word_analysis(text):

    natija = []

    for i, word in enumerate(
        words_only(text),
        1
    ):

        qoshimchalar, ozak = suffixes(word)

        natija.append({
            "id": i,
            "so'z": word,
            "lemma": lemma(word),
            "turkum": pos(word),
            "o'zak": ozak,
            "qo'shimchalar": qoshimchalar
        })

    return natija


def spelling_errors(text):

    natija = []

    for word in words_only(text):

        if word in IMLO:

            natija.append({
                "so'z": word,
                "tavsiya": IMLO[word],
                "izoh": "Ehtimoliy imlo xatosi."
            })

    return natija


def punctuation_issues(text):

    issues = []

    if re.search(r"\s+[,.!?;:]", text):
        issues.append(
            "Tinish belgisidan oldin ortiqcha bo‘sh joy bor."
        )

    if re.search(r"[,.!?;:]{2,}", text):
        issues.append(
            "Ketma-ket ortiqcha tinish belgilari ishlatilgan."
        )

    if re.search(r"[!?]\S", text):
        issues.append(
            "Tinish belgisidan keyin bo‘sh joy kerak bo‘lishi mumkin."
        )

    return issues


def sentence_analysis(text):

    natija = []

    for i, sentence in enumerate(
        sentences(text),
        1
    ):

        ws = words_only(sentence)

        verbs = [
            w for w in ws
            if pos(w) == "fe’l"
        ]

        natija.append({
            "gap": i,
            "matn": sentence,
            "so'zlar_soni": len(ws),
            "fe'llar": verbs,
            "predikativ_markaz": (
                verbs[0]
                if verbs
                else ""
            ),
            "izoh": (
                "Fe’l markazi aniqlandi."
                if verbs
                else
                "Fe’l markazi avtomatik aniqlanmadi; "
                "qo‘lda tekshirish tavsiya etiladi."
            )
        })

    return natija


def repetitions(text):

    hisob = Counter(
        words_only(text)
    )

    return [
        {
            "so'z": word,
            "soni": count
        }
        for word, count in hisob.most_common()
        if count > 1
    ]


def essay_score(text):

    ws = words_only(text)
    ss = sentences(text)

    if not ws:

        return {
            "ball": 0,
            "daraja": "ma’lumot yetarli emas",
            "so'z_boyligi": 0,
            "o'rtacha_gap_uzunligi": 0,
            "eslatma": "Matn kiritilmagan."
        }

    diversity = len(
        set(ws)
    ) / len(ws)

    avg = len(ws) / max(
        len(ss),
        1
    )

    score = (
        min(25, len(ws) / 4)
        + min(25, diversity * 35)
        + min(20, len(ss) * 2)
        + (
            15
            if 8 <= avg <= 30
            else 8
        )
        + (
            15
            if text.strip().endswith(
                (".", "!", "?")
            )
            else 5
        )
    )

    score = round(
        min(100, score),
        1
    )

    if score >= 85:
        level = "juda yaxshi"
    elif score >= 70:
        level = "yaxshi"
    elif score >= 55:
        level = "o‘rtacha"
    else:
        level = "takomillashtirish kerak"

    return {
        "ball": score,
        "daraja": level,
        "so'z_boyligi": round(
            diversity * 100,
            1
        ),
        "o'rtacha_gap_uzunligi": round(
            avg,
            1
        ),
        "eslatma": (
            "Bu dastlabki avtomatik baho; "
            "rasmiy imtihon bali emas."
        )
    }


def confidence(text, analysis):

    score = 40

    if len(analysis) >= 5:
        score += 20

    if len(words_only(text)) >= 10:
        score += 20

    if len(sentences(text)) >= 2:
        score += 20

    score = min(
        score,
        100
    )

    if score >= 80:
        holat = "yuqori"
    elif score >= 60:
        holat = "o‘rtacha"
    else:
        holat = "qisman"

    return {
        "foiz": score,
        "holat": holat
    }


def full_analysis(text):

    ws = words_only(text)
    ss = sentences(text)

    soz_tahlili = word_analysis(text)

    return {

        "statistika": {

            "so'zlar_soni":
                len(ws),

            "gaplar_soni":
                len(ss),

            "belgilar_soni":
                len(text),

            "noyob_so'zlar":
                len(set(ws)),

            "o'rtacha_gap_uzunligi":
                round(
                    len(ws) /
                    max(len(ss), 1),
                    1
                )
        },

        "so'z_tahlili":
            soz_tahlili,

        "gap_tahlili":
            sentence_analysis(text),

        "imlo_xatolari":
            spelling_errors(text),

        "tinish_belgisi":
            punctuation_issues(text),

        "takroriy_so'zlar":
            repetitions(text),

        "insho_bahosi":
            essay_score(text),

        "ishonchlilik":
            confidence(
                text,
                soz_tahlili
            )
    }


SAHIFA = r"""
<!doctype html>

<html lang="uz">

<head>

<meta charset="utf-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>O‘zAI TIL — V3.0</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #f4f6fb;
    color: #172033;
    font-family: Arial, sans-serif;
}

main {
    max-width: 1150px;
    margin: auto;
    padding: 24px 16px 60px;
}

header,
.card {
    background: white;
    border-radius: 18px;
    box-shadow: 0 6px 24px rgba(0,0,0,.07);
}

header {
    padding: 26px;
    margin-bottom: 18px;
}

h1 {
    margin: 0 0 8px;
    font-size: 30px;
}

textarea {
    width: 100%;
    min-height: 240px;
    padding: 16px;
    border: 2px solid #dce3ed;
    border-radius: 14px;
    font-size: 17px;
    line-height: 1.6;
    resize: vertical;
}

button {
    width: 100%;
    margin-top: 12px;
    padding: 16px;
    border: 0;
    border-radius: 14px;
    background: #6555e8;
    color: white;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
}

.card {
    padding: 22px;
    margin-top: 18px;
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit,minmax(155px,1fr));
    gap: 12px;
}

.stat {
    padding: 16px;
    background: #f5f3ff;
    border-radius: 14px;
}

.stat b {
    font-size: 24px;
}

.ok {
    background: #effbf2;
    padding: 13px;
    border-radius: 12px;
}

.err {
    background: #fff1f1;
    padding: 13px;
    border-radius: 12px;
    margin: 8px 0;
}

.warn {
    background: #fff8e8;
    padding: 13px;
    border-radius: 12px;
    margin: 8px 0;
}

.badge {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    background: #eef1f7;
    margin: 3px;
}

table {
    width: 100%;
    border-collapse: collapse;
    display: block;
    overflow-x: auto;
}

th,
td {
    padding: 9px;
    border-bottom: 1px solid #edf0f5;
    text-align: left;
    white-space: nowrap;
}

.bar {
    height: 12px;
    background: #e9eaf0;
    border-radius: 8px;
    overflow: hidden;
}

.bar > div {
    height: 100%;
    background: #6555e8;
}

small {
    color: #667085;
}

</style>

</head>

<body>

<main>

<header>

<h1>O‘zAI TIL</h1>

<div>
O‘zbek tili ko‘p funksiyali
lingvistik tahlil tizimi
</div>

<small>
Muallif: {{ muallif }}
· {{ versiya }}
</small>

</header>


<form method="post">

<textarea
name="matn"
placeholder="Matnni shu yerga kiriting..."
>{{ matn }}</textarea>

<button type="submit">
TAHLIL QILISH
</button>

</form>


{% if natija %}


<div class="card">

<h2>Umumiy natija</h2>

<div class="grid">

<div class="stat">
<b>
{{ natija["statistika"]["so'zlar_soni"] }}
</b>
<br>
So‘zlar soni
</div>

<div class="stat">
<b>
{{ natija["statistika"]["gaplar_soni"] }}
</b>
<br>
Gaplar soni
</div>

<div class="stat">
<b>
{{ natija["statistika"]["belgilar_soni"] }}
</b>
<br>
Belgilar soni
</div>

<div class="stat">
<b>
{{ natija["statistika"]["noyob_so'zlar"] }}
</b>
<br>
Noyob so‘zlar
</div>

</div>

</div>


<div class="card">

<h2>
Morfologik tahlil
</h2>

<table>

<tr>

<th>#</th>
<th>So‘z</th>
<th>Lemma</th>
<th>Turkum</th>
<th>O‘zak</th>
<th>Qo‘shimchalar</th>

</tr>

{% for x in natija["so'z_tahlili"] %}

<tr>

<td>
{{ x["id"] }}
</td>

<td>
{{ x["so'z"] }}
</td>

<td>
{{ x["lemma"] }}
</td>

<td>
{{ x["turkum"] }}
</td>

<td>
{{ x["o'zak"] }}
</td>

<td>
{{ x["qo'shimchalar"]|join(", ")
if x["qo'shimchalar"]
else "—" }}
</td>

</tr>

{% endfor %}

</table>

</div>


<div class="card">

<h2>
Gap tahlili
</h2>

{% for x in natija["gap_tahlili"] %}

<div class="warn">

<b>
{{ x["gap"] }}-gap:
</b>

{{ x["matn"] }}

<br>

So‘zlar:
{{ x["so'zlar_soni"] }}

·

Predikativ markaz:

<b>
{{ x["predikativ_markaz"]
if x["predikativ_markaz"]
else "aniqlanmadi" }}
</b>

<br>

Fe’llar:

{{ x["fe'llar"]|join(", ")
if x["fe'llar"]
else "aniqlanmadi" }}

<br>

<small>
{{ x["izoh"] }}
</small>

</div>

{% endfor %}

</div>


<div class="card">

<h2>
Imlo tekshiruvi
</h2>

{% if natija["imlo_xatolari"] %}

{% for x in natija["imlo_xatolari"] %}

<div class="err">

<b>
{{ x["so'z"] }}
</b>

→

<b>
{{ x["tavsiya"] }}
</b>

<br>

{{ x["izoh"] }}

</div>

{% endfor %}

{% else %}

<div class="ok">
Aniqlangan ehtimoliy imlo xatosi topilmadi.
</div>

{% endif %}

</div>


<div class="card">

<h2>
Tinish belgilari
</h2>

{% if natija["tinish_belgisi"] %}

{% for x in natija["tinish_belgisi"] %}

<div class="err">
{{ x }}
</div>

{% endfor %}

{% else %}

<div class="ok">
Aniqlangan muammo topilmadi.
</div>

{% endif %}

</div>


<div class="card">

<h2>
Takroriy so‘zlar
</h2>

{% if natija["takroriy_so'zlar"] %}

{% for x in natija["takroriy_so'zlar"] %}

<span class="badge">

{{ x["so'z"] }}

—

{{ x["soni"] }} marta

</span>

{% endfor %}

{% else %}

<div class="ok">
Takroriy so‘z aniqlanmadi.
</div>

{% endif %}

</div>


<div class="card">

<h2>
Insho / matn bahosi
</h2>

<div class="grid">

<div class="stat">

<b>
{{ natija["insho_bahosi"]["ball"] }}
</b>

<br>

Ball / 100

</div>


<div class="stat">

<b>
{{ natija["insho_bahosi"]["so'z_boyligi"] }}%
</b>

<br>

Lug‘at xilma-xilligi

</div>


<div class="stat">

<b>
{{ natija["insho_bahosi"]["daraja"] }}
</b>

<br>

Daraja

</div>

</div>

<p>

{{ natija["insho_bahosi"]["eslatma"] }}

</p>

</div>


<div class="card">

<h2>
Ishonchlilik
</h2>

<p>

<b>
{{ natija["ishonchlilik"]["foiz"] }}%
</b>

—

{{ natija["ishonchlilik"]["holat"] }}

</p>

<div class="bar">

<div
style="width:{{ natija["ishonchlilik"]["foiz"] }}%">
</div>

</div>

</div>


{% endif %}

</main>

</body>

</html>
"""


@app.route("/", methods=["GET", "POST"])
def bosh_sahifa():

    matn = ""

    if request.method == "POST":
        matn = request.form.get(
            "matn",
            ""
        ).strip()

    natija = (
        full_analysis(matn)
        if matn
        else None
    )

    return render_template_string(
        SAHIFA,
        matn=matn,
        natija=natija,
        muallif=MUALLIF,
        versiya=VERSIYA
    )


@app.route(
    "/api/tahlil",
    methods=["POST"]
)
def api_tahlil():

    data = request.get_json(
        silent=True
    ) or {}

    matn = str(
        data.get("matn", "")
    ).strip()

    if not matn:

        return jsonify({
            "xato": "Matn kiritilmagan."
        }), 400

    return jsonify(
        full_analysis(matn)
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
