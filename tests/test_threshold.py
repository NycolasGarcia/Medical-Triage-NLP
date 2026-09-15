"""Testa a regra de decisão por limiar cumulativo (caixa 6.4)."""

from src.models.threshold import select_label


def test_urgente_quando_acima_do_limiar():
    probs = {"normal": 0.1, "atencao": 0.3, "urgente": 0.6}
    assert select_label(probs, threshold_urgente=0.5, threshold_atencao=0.4) == "urgente"


def test_atencao_quando_urgente_baixo_mas_cumulativo_alto():
    probs = {"normal": 0.3, "atencao": 0.5, "urgente": 0.2}
    assert select_label(probs, threshold_urgente=0.5, threshold_atencao=0.4) == "atencao"


def test_normal_quando_nenhum_limiar_atingido():
    probs = {"normal": 0.7, "atencao": 0.2, "urgente": 0.1}
    assert select_label(probs, threshold_urgente=0.5, threshold_atencao=0.4) == "normal"


def test_limiar_baixo_de_urgente_captura_mais_casos_que_argmax():
    # urgente não seria o argmax (perde para atencao), mas passa no limiar deliberadamente baixo
    probs = {"normal": 0.1, "atencao": 0.55, "urgente": 0.35}
    assert max(probs, key=probs.get) == "atencao"  # argmax discordaria
    assert select_label(probs, threshold_urgente=0.3, threshold_atencao=0.4) == "urgente"


def test_usa_constantes_padrao_quando_nao_especificado():
    # bem acima de THRESHOLD_ATENCAO (0,09 combinado) e THRESHOLD_URGENTE (0,31)
    probs = {"normal": 0.97, "atencao": 0.02, "urgente": 0.01}
    assert select_label(probs) == "normal"
