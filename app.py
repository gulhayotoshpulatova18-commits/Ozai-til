# -*- coding: utf-8 -*-
from flask import Flask, request, render_template_string, jsonify
from linguistic_core import full_analysis, MUALLIF, VERSIYA

app = Flask(__name__)

SAHIFA = r"""
<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>O‘zAI TIL — ko‘p funksiyali tahlil</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f6fb;color:#172033;font-family:Arial,sans-serif}
main{max-width:1150px;margin:auto;padding:24px 16px 60px}
header,.card{background:#fff;border-radius:18px;box-shadow:0 6px 24px rgba(0,0,0,.07)}
header{padding:26px;margin-bottom:18px}h1{margin:0 0 8px;font-size:30px}
h2{margin:0 0 16px}.sub,small{color:#667085}
textarea{width:100%;min-height:240px;padding:16px;border:2px solid #dce3ed;border-radius:14px;font-size:17px;line-height:1.6;resize:vertical}
button{width:100%;margin-top:12px;padding:16px;border:0;border-radius:14px;background:#6555e8;color:#fff;font-size:18px;font-weight:bold;cursor:pointer}
.card{padding:22px;margin-top:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px}
.stat{padding:16px;background:#f5f3ff;border-radius:14px}.stat b{font-size:24px}
.ok{background:#effbf2;padding:13px;border-radius:12px}.err{background:#fff1f1;padding:13px;border-radius:12px;margin:8px 0}
.warn{background:#fff8e8;padding:13px;border-radius:12px;margin:8px 0}
table{width:100%;border-collapse:collapse;display:block;overflow-x:auto}th,td{padding:9px;border-bottom:1px solid #edf0f5;text-align:left;white-space:nowrap}
.badge{display:inline-block;padding:7px 11px;border-radius:999px;background:#eef1f7;margin:3px}
.bar{height:12px;background:#e9eaf0;border-radius:8px;overflow:hidden}.bar>div{height:100%;background:#6555e8}
</style>
</head>
<body><main>
<header><h1>O‘zAI TIL</h1>
<div class="sub">O‘zbek tili ko‘p funksiyali lingvistik tahlil tizimi</div>
<small>Muallif: {{muallif}} · {{versiya}}</small></header>

<form method="post">
<textarea name="matn" placeholder="Matnni shu yerga kiriting...">{{matn}}</textarea>
<button type="submit">TAHLIL QILISH</button>
</form>

{% if natija %}
<div class="card"><h2>Umumiy natija</h2><div class="grid">
<div class="stat"><b>{{natija["statistika"]["so'zlar_soni"]}}</b><br>So‘zlar soni</div>
<div class="stat"><b>{{natija["statistika"]["gaplar_soni"]}}</b><br>Gaplar soni</div>
<div class="stat"><b>{{natija["statistika"]["belgilar_soni"]}}</b><br>Belgilar soni</div>
<div class="stat"><b>{{natija["statistika"]["noyob_so'zlar"]}}</b><br>Noyob so‘zlar</div>
<div class="stat"><b>{{natija["statistika"]["o'rtacha_gap_uzunligi"]}}</b><br>O‘rtacha gap</div>
</div></div>

<div class="card"><h2>So‘zlarning morfologik tahlili</h2>
<table><tr><th>#</th><th>So‘z</th><th>Lemma</th><th>So‘z turkumi</th><th>O‘zak</th><th>Qo‘shimchalar</th></tr>
{% for x in natija["so'z_tahlili"] %}
<tr><td>{{x["id"]}}</td><td>{{x["so'z"]}}</td><td>{{x["lemma"]}}</td><td>{{x["turkum"]}}</td>
<td>{{x["o'zak"]}}</td><td>{{x["qo'shimchalar"]|join(", ") if x["qo'shimchalar"] else "—"}}</td></tr>
{% endfor %}</table></div>

<div class="card"><h2>Gap tahlili</h2>
{% for x in natija["gap_tahlili"] %}
<div class="warn"><b>{{x["gap"]}}-gap:</b> {{x["matn"]}}<br>
So‘zlar soni: {{x["so'zlar_soni"]}} ·
Predikativ markaz: <b>{{x["predikativ_markaz"] or "aniqlanmadi"}}</b><br>
Fe’llar: {{x["fe'llar"]|join(", ") if x["fe'llar"] else "aniqlanmadi"}}<br>
<small>{{x["izoh"]}}</small></div>
{% endfor %}</div>

<div class="card"><h2>Imlo tekshiruvi</h2>
{% if natija["imlo_xatolari"] %}
{% for x in natija["imlo_xatolari"] %}
<div class="err"><b>{{x["so'z"]}}</b> → <b>{{x["tavsiya"]}}</b><br><small>{{x["izoh"]}}</small></div>
{% endfor %}
{% else %}<div class="ok">Aniqlangan ehtimoliy imlo xatosi topilmadi.</div>{% endif %}</div>

<div class="card"><h2>Tinish belgilari</h2>
{% if natija["tinish_belgisi"] %}
{% for x in natija["tinish_belgisi"] %}<div class="err">{{x}}</div>{% endfor %}
{% else %}<div class="ok">Aniqlangan muammo topilmadi.</div>{% endif %}</div>

<div class="card"><h2>Takroriy so‘zlar</h2>
{% if natija["takroriy_so'zlar"] %}
{% for x in natija["takroriy_so'zlar"] %}<span class="badge">{{x["so'z"]}} — {{x["soni"]}} marta</span>{% endfor %}
{% else %}<div class="ok">Takroriy so‘z aniqlanmadi.</div>{% endif %}</div>

<div class="card"><h2>Insho / matn bahosi</h2><div class="grid">
<div class="stat"><b>{{natija["insho_bahosi"]["ball"]}}</b><br>Ball / 100</div>
<div class="stat"><b>{{natija["insho_bahosi"]["so'z_boyligi"]}}%</b><br>Lug‘at xilma-xilligi</div>
<div class="stat"><b>{{natija["insho_bahosi"]["o'rtacha_gap_uzunligi"]}}</b><br>O‘rtacha gap</div>
<div class="stat"><b>{{natija["insho_bahosi"]["daraja"]}}</b><br>Daraja</div>
</div><p><small>{{natija["insho_bahosi"].get("eslatma","")}}</small></p></div>

<div class="card"><h2>Ishonchlilik</h2>
<p><b>{{natija["ishonchlilik"]["foiz"]}}%</b> — {{natija["ishonchlilik"]["holat"]}}</p>
<div class="bar"><div style="width:{{natija["ishonchlilik"]["foiz"]}}%"></div></div></div>
{% endif %}
</main></body></html>
"""

@app.route("/", methods=["GET", "POST"])
def bosh_sahifa():
    matn = ""
    natija = None
    if request.method == "POST":
        matn = request.form.get("matn", "").strip()
        if matn:
            natija = full_analysis(matn)
    return render_template_string(SAHIFA, matn=matn, natija=natija,
                                  muallif=MUALLIF, versiya=VERSIYA)

@app.route("/api/tahlil", methods=["POST"])
def api_tahlil():
    data = request.get_json(silent=True) or {}
    matn = str(data.get("matn", "")).strip()
    if not matn:
        return jsonify({"xato": "Matn kiritilmagan."}), 400
    return jsonify(full_analysis(matn))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
