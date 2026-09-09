from flask import Flask, request, render_template_string
from main import tahlil_qil

app = Flask(__name__)

SAHIFA = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>O‘zbek tili — Lingvistik tahlil</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #172033;
        }

        .asosiy {
            max-width: 900px;
            margin: 0 auto;
            padding: 25px 16px 50px;
        }

        .sarlavha {
            background: white;
            border-radius: 18px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }

        h1 {
            margin: 0 0 10px;
            font-size: 28px;
        }

        .izoh {
            color: #657084;
            font-size: 15px;
        }

        textarea {
            width: 100%;
            min-height: 250px;
            resize: vertical;
            border: 2px solid #dce3ed;
            border-radius: 14px;
            padding: 16px;
            font-size: 17px;
            line-height: 1.6;
            outline: none;
        }

        textarea:focus {
            border-color: #6c5ce7;
        }

        button {
            width: 100%;
            margin-top: 15px;
            padding: 16px;
            border: 0;
            border-radius: 14px;
            background: #6c5ce7;
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            opacity: 0.9;
        }

        .natija {
            margin-top: 22px;
            background: white;
            border-radius: 18px;
            padding: 22px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }

        .natija h2 {
            margin-top: 0;
        }

        .qator {
            display: flex;
            justify-content: space-between;
            padding: 14px 0;
            border-bottom: 1px solid #edf0f5;
            font-size: 17px;
        }

        .qiymat {
            font-weight: bold;
        }

        .ishonchlilik {
            margin-top: 18px;
            padding: 15px;
            border-radius: 12px;
            background: #f0edff;
        }

        .uzun {
            margin-top: 18px;
        }

        .uzun span {
            display: inline-block;
            background: #eef1f7;
            padding: 7px 10px;
            margin: 4px;
            border-radius: 8px;
        }

        .xato {
            color: #c62828;
            background: #ffebee;
            padding: 15px;
            border-radius: 12px;
        }
    </style>
</head>

<body>

<div class="asosiy">

    <div class="sarlavha">
        <h1>O‘zbek tili</h1>
        <div class="izoh">
            O‘zbek tili lingvistik tahlil tizimi
        </div>
    </div>

    <form method="POST">

        <textarea
            name="matn"
            placeholder="Tahlil qilinadigan matnni shu yerga kiriting..."
        >{{ matn }}</textarea>

        <button type="submit">
            TAHLIL QILISH
        </button>

    </form>

    {% if natija %}

    <div class="natija">

        <h2>Tahlil natijasi</h2>

        {% if natija.get("holat") == "xato" %}

            <div class="xato">
                {{ natija.get("matn", "Xatolik yuz berdi.") }}
            </div>

        {% else %}

            <div class="qator">
                <span>So‘zlar soni</span>
                <span class="qiymat">
                    {{ natija.get("sozlar_soni", 0) }}
                </span>
            </div>

            <div class="qator">
                <span>Gaplar soni</span>
                <span class="qiymat">
                    {{ natija.get("gaplar_soni", 0) }}
                </span>
            </div>

            <div class="qator">
                <span>Belgilar soni</span>
                <span class="qiymat">
                    {{ natija.get("belgilar_soni", 0) }}
                </span>
            </div>

            <div class="ishonchlilik">
                <strong>Ishonchlilik:</strong>
                {{ "%.1f"|format(natija.get("ishonchlilik", 0) * 100) }}%
            </div>

            {% if natija.get("uzun_sozlar") %}

            <div class="uzun">
                <strong>Uzun so‘zlar:</strong>

                <div>
                    {% for soz in natija.get("uzun_sozlar", []) %}
                        <span>{{ soz }}</span>
                    {% endfor %}
                </div>
            </div>

            {% endif %}

        {% endif %}

    </div>

    {% endif %}

</div>

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
            natija = tahlil_qil(matn)
        else:
            natija = {
                "holat": "xato",
                "matn": "Iltimos, matn kiriting."
            }

    return render_template_string(
        SAHIFA,
        matn=matn,
        natija=natija
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
