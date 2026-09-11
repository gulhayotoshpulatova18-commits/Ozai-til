[9/12/2026 1:51 AM] Toshpulatova Gulhayo: from flask import Flask, request, render_template_string

try:
    from main import matnni_tekshirish
except ImportError:
    from main import tahlil_qil as matnni_tekshirish


app = Flask(name)

MUALLIF = "Gulhayo Toshpulatova"
VERSIYA = "V1.8.1575"


SAHIFA = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>O‘zbek tili AI</title>

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
            margin: auto;
            padding: 20px 15px 40px;
        }

        .sarlavha {
            background: white;
            padding: 25px;
            border-radius: 18px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }

        h1 {
            margin: 0 0 10px;
            font-size: 30px;
        }

        .kichik {
            color: #657084;
            line-height: 1.6;
        }

        textarea {
            width: 100%;
            min-height: 230px;
            margin-top: 18px;
            padding: 16px;
            border: 2px solid #dce3ed;
            border-radius: 14px;
            font-size: 17px;
            line-height: 1.6;
            resize: vertical;
            outline: none;
        }

        textarea:focus {
            border-color: #6c5ce7;
        }

        button {
            width: 100%;
            margin-top: 15px;
            padding: 16px;
            border: none;
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
            background: white;
            padding: 22px;
            margin-top: 20px;
            border-radius: 18px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
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

        .xato {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 12px;
        }

        .haqida {
            background: white;
            margin-top: 20px;
            padding: 22px;
            border-radius: 18px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }

        .haqida h2 {
            margin-top: 0;
        }

        footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #657084;
            line-height: 1.7;
        }

        .muallif {
            font-weight: bold;
            color: #172033;
        }

        .versiya {
            font-size: 13px;
        }

        @media (max-width: 600px) {
            h1 {
                font-size: 25px;
            }

            .asosiy {
                padding: 12px 10px 30px;
            }
        }
    </style>
</head>

<body>

<div class="asosiy">

    <div class="sarlavha">

        <h1>O‘zbek tili AI</h1>

        <div class="kichik">
            O‘zbek tili uchun sun’iy intellekt asosidagi
            lingvistik tahlil tizimi.
        </div>

        <form method="POST">

            <textarea
                name="matn"
                placeholder="O‘zbekcha matnni shu yerga kiriting..."
            >{{ matn }}</textarea>

            <button type="submit">
                MATNNI TAHLIL QILISH
            </button>

        </form>

    </div>


    {% if natija %}

    <div class="natija">

        <h2>📊 Tahlil natijasi</h2>

        {% if natija.get("xato") %}
[9/12/2026 1:51 AM] Toshpulatova Gulhayo: <div class="xato">
                {{ natija["xato"] }}
            </div>

        {% else %}

            {% if natija.get("so‘zlar_soni") is not none %}

            <div class="qator">
                <span>So‘zlar soni</span>
                <span class="qiymat">
                    {{ natija["so‘zlar_soni"] }}
                </span>
            </div>

            {% elif natija.get("sozlar_soni") is not none %}

            <div class="qator">
                <span>So‘zlar soni</span>
                <span class="qiymat">
                    {{ natija["sozlar_soni"] }}
                </span>
            </div>

            {% endif %}


            {% if natija.get("gaplar_soni") is not none %}

            <div class="qator">
                <span>Gaplar soni</span>
                <span class="qiymat">
                    {{ natija["gaplar_soni"] }}
                </span>
            </div>

            {% endif %}


            {% if natija.get("belgilar_soni") is not none %}

            <div class="qator">
                <span>Belgilar soni</span>
                <span class="qiymat">
                    {{ natija["belgilar_soni"] }}
                </span>
            </div>

            {% endif %}


            {% if natija.get("ishonchlilik") is not none %}

            <div class="qator">
                <span>Ishonchlilik</span>
                <span class="qiymat">
                    {{ natija["ishonchlilik"] }}
                </span>
            </div>

            {% endif %}

        {% endif %}

    </div>

    {% endif %}


    <div class="haqida">

        <h2>ℹ️ Loyiha haqida</h2>

        <p>
            <strong>O‘zbek tili AI</strong> —
            o‘zbek tilidagi matnlarni avtomatik
            lingvistik tahlil qilishga mo‘ljallangan
            loyiha.
        </p>

        <p>
            Tizimning keyingi bosqichlarida imlo,
            morfologiya, sintaksis, lug‘aviy tahlil,
            matn sifati va insho baholash kabi
            imkoniyatlarni rivojlantirish ko‘zda tutiladi.
        </p>

        <p>
            <strong>Muallif:</strong>
            {{ muallif }}
        </p>

    </div>


    <footer>

        <div class="muallif">
            Muallif: {{ muallif }}
        </div>

        <div>
            O‘zbek tili AI — lingvistik tahlil tizimi
        </div>

        <div class="versiya">
            {{ versiya }}
        </div>

    </footer>

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

        if not matn:

            natija = {
                "xato": "Iltimos, tahlil qilish uchun matn kiriting."
            }

        else:

            try:
                natija = matnni_tekshirish(matn)

            except Exception as xato:

                natija = {
                    "xato":
                    "Tahlil vaqtida xatolik yuz berdi: "
                    + str(xato)
                }

    return render_template_string(
        SAHIFA,
        matn=matn,
        natija=natija,
        muallif=MUALLIF,
        versiya=VERSIYA
    )


if name == "main":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
