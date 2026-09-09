"""
O‘zbek tili — asosiy ishga tushirish fayli
Loyiha: O‘zbek tili lingvistik tahlil tizimi
"""

from typing import Any, Dict


LOYIHA_NOMI = "O‘zbek tili"
VERSIYA = "1.8.1575"


def natija(
    matn: str,
    holat: str = "tayyor",
    ishonchlilik: float = 0.0,
) -> Dict[str, Any]:
    """Tahlil natijasini yagona ko‘rinishga keltiradi."""
    return {
        "loyiha": LOYIHA_NOMI,
        "versiya": VERSIYA,
        "holat": holat,
        "matn": matn,
        "ishonchlilik": round(max(0.0, min(1.0, ishonchlilik)), 3),
    }


def matnni_tekshirish(matn: str) -> Dict[str, Any]:
    """O‘zbekcha matnni asosiy darajada tekshiradi."""

    if not isinstance(matn, str):
        return natija("", "xato", 0.0)

    matn = matn.strip()

    if not matn:
        return natija("", "bo‘sh matn", 1.0)

    so‘zlar = matn.split()
    gaplar = [
        gap.strip()
        for gap in matn.replace("!", ".").replace("?", ".").split(".")
        if gap.strip()
    ]

    belgilar_soni = len(matn)
    so‘zlar_soni = len(so‘zlar)
    gaplar_soni = len(gaplar)

    uzun_so‘zlar = [
        so‘z.strip(".,!?;:()[]{}\"'«»")
        for so‘z in so‘zlar
        if len(so‘z.strip(".,!?;:()[]{}\"'«»")) >= 12
    ]

    natija_ma'lumoti = natija(
        matn,
        "tahlil qilindi",
        0.75,
    )

    natija_ma'lumoti.update(
        {
            "belgilar_soni": belgilar_soni,
            "so‘zlar_soni": so‘zlar_soni,
            "gaplar_soni": gaplar_soni,
            "uzun_so‘zlar": uzun_so‘zlar,
            "tahlil": {
                "matn_mavjud": True,
                "so‘zlar_mavjud": so‘zlar_soni > 0,
                "gaplar_mavjud": gaplar_soni > 0,
            },
        }
    )

    return natija_ma'lumoti


def tahlil_qil(matn: str) -> Dict[str, Any]:
    """
    Loyihaning asosiy tahlil nuqtasi.
    Mavjud lingvistik modullar bo‘lsa, ulardan foydalanishga harakat qiladi.
    """
    asosiy_natija = matnni_tekshirish(matn)

    try:
        from linguistic_core import tahlil_qil as lingvistik_tahlil

        tashqi_natija = lingvistik_tahlil(matn)

        if isinstance(tashqi_natija, dict):
            asosiy_natija["lingvistik_tahlil"] = tashqi_natija
            asosiy_natija["ishonchlilik"] = 0.90

    except (ImportError, AttributeError, TypeError):
        pass

    return asosiy_natija


def asosiy():
    """Dasturni ishga tushiradi."""

    print(f"{LOYIHA_NOMI} — {VERSIYA}")
    print("O‘zbek tili lingvistik tahlil tizimi ishga tayyor.")
    print("Matn kiriting. Chiqish uchun: chiqish")

    while True:
        try:
            matn = input("\nMatn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDastur yakunlandi.")
            break

        if matn.lower() == "chiqish":
            print("Dastur yakunlandi.")
            break

        if not matn:
            print("Iltimos, matn kiriting.")
            continue

        natija_ma'lumoti = tahlil_qil(matn)

        print("\n--- TAHLIL NATIJASI ---")
        print(f"So‘zlar soni: {natija_ma'lumoti['so‘zlar_soni']}")
        print(f"Gaplar soni: {natija_ma'lumoti['gaplar_soni']}")
        print(
            "Ishonchlilik: "
            f"{natija_ma'lumoti['ishonchlilik'] * 100:.1f}%"
        )


if __name__ == "__main__":
    asosiy()
