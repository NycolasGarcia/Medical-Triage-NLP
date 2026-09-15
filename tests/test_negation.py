"""Testa a marcação de escopo de negação (caixa 6.1, §10.6 armadilha 1)."""

from src.features.negation import mark_negation, negation_flags


def test_marca_termo_apos_gatilho_de_negacao():
    marcado = mark_negation("no signs of shock")
    assert "signs_NEG" in marcado.split()
    assert "shock_NEG" in marcado.split()


def test_termo_antes_do_gatilho_nao_e_marcado():
    marcado = mark_negation("shock without signs of improvement")
    tokens = marcado.split()
    assert tokens[0] == "shock"


def test_pontuacao_encerra_o_escopo():
    marcado = mark_negation("denies chest pain. severe headache noted")
    tokens = marcado.split()
    assert "headache" in tokens  # fora do escopo, não marcado
    assert "pain_NEG" in tokens  # dentro do escopo, antes do ponto


def test_negation_flags_tamanho_bate_com_tokens():
    flags = negation_flags("patient reports no fever or chills today")
    assert len(flags) == 7
    assert flags[2] == ("no", False)  # o próprio gatilho não é marcado como negado
    assert flags[3][1] is True  # "fever" está no escopo
