"""Testa o léxico de severidade — em especial o desconto de termos negados
(risco de interação com a marcação de negação, identificado antes de implementar)."""

from src.features.lexicon import SeverityLexiconCounter


def test_conta_termo_de_alta_severidade():
    counter = SeverityLexiconCounter()
    rows = counter.transform(["patient in acute distress with severe hypotension"])
    assert rows[0][0] == 2  # acute, severe
    assert rows[0][1] == 0


def test_termo_negado_nao_conta():
    counter = SeverityLexiconCounter()
    rows = counter.transform(["denies acute distress, patient stable"])
    high, low = rows[0]
    assert high == 0  # "acute" está no escopo de "denies"
    assert low == 1  # "stable" não está negado


def test_conta_termo_de_baixa_severidade():
    counter = SeverityLexiconCounter()
    rows = counter.transform(["mild and stable, routine follow-up"])
    assert rows[0][1] == 4


def test_get_feature_names_out():
    counter = SeverityLexiconCounter()
    assert counter.get_feature_names_out() == ["severity_high_count", "severity_low_count"]
