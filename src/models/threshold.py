"""Caixa 6.4 — regra de decisão por limiar (ordinal, cumulativo) sobre as
probabilidades calibradas (caixa 6.2), tunada pela matriz de custo (caixa 6.3) com
o piso de recall de `urgente` decidido em §14/ADR-0005.

Regra cumulativa (`normal < atenção < urgente`): prediz `urgente` se
`P(urgente) >= THRESHOLD_URGENTE`; senão prediz `atenção` se
`P(atenção) + P(urgente) >= THRESHOLD_ATENCAO`; senão `normal`. Substitui o argmax
puro (limiar implícito de 1/3 por classe) por limiares deliberadamente enviesados
para reduzir sub-triagem, mesmo aumentando falsos `atenção`/`urgente` — exatamente
o que §7 pede.

Valores de `THRESHOLD_URGENTE`/`THRESHOLD_ATENCAO` vêm da busca de
`src/models/threshold_search.py` (ver `docs/EXPERIMENTS.md`, seção F6, e ADR-0005) —
não são escolhidos à mão aqui.
"""

RECALL_URGENTE_TARGET = 0.90  # §14/ADR-0005

# Vencedores da busca de threshold_search.py (ver docs/EXPERIMENTS.md e ADR-0005):
# maior THRESHOLD_URGENTE que ainda cumpre RECALL_URGENTE_TARGET (recall obtido:
# 0,9026), THRESHOLD_ATENCAO minimizando custo médio com o primeiro já fixado.
THRESHOLD_URGENTE = 0.31
THRESHOLD_ATENCAO = 0.09


def select_label(
    probabilities: dict[str, float],
    threshold_urgente: float = THRESHOLD_URGENTE,
    threshold_atencao: float = THRESHOLD_ATENCAO,
) -> str:
    """Aplica a regra de limiar cumulativo a um dicionário `{classe: probabilidade}`."""
    p_urgente = probabilities["urgente"]
    p_atencao_ou_mais = probabilities["atencao"] + probabilities["urgente"]
    if p_urgente >= threshold_urgente:
        return "urgente"
    if p_atencao_ou_mais >= threshold_atencao:
        return "atencao"
    return "normal"
