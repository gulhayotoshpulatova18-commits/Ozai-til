from main import matnni_tekshirish


def test_matnni_tekshirish():
    natija = matnni_tekshirish("Men o'zbek tilini yaxshi ko'raman.")
    assert isinstance(natija, dict)
    assert "so'zlar_soni" in natija
    assert "gaplar_soni" in natija
    
