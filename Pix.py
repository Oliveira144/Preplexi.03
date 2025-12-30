import streamlit as st

# =============================
# CONFIGURAÇÃO DA PÁGINA
# =============================
st.set_page_config(page_title="Football Studio – Sistema Elite", layout="centered")

st.title("🎴 Football Studio – SISTEMA ELITE COMPLETO")
st.caption("Leitura profissional • padrões • empates • decisão visual")

# =============================
# MAPAS VISUAIS
# =============================
EMOJIS = {
    "P": "🔵",
    "B": "🔴",
    "T": "🟡"
}

SUGESTAO = {
    "P": "🔵 **APOSTAR PLAYER**",
    "B": "🔴 **APOSTAR BANKER**",
    "T": "🟡 **EMPATE (ALTO RISCO)**"
}

# =============================
# SESSION STATE
# =============================
if "hist" not in st.session_state:
    st.session_state.hist = []

# =============================
# MOTOR DE PADRÕES (COMPLETO)
# =============================
def detectar_padrao(hist):
    if len(hist) < 3:
        return "Sem leitura", "⏸️ AGUARDAR", 50

    h = hist[-15:]

    # 1 Alternância simples
    if len(h) >= 4 and all(h[i] != h[i+1] for i in range(len(h)-1) if h[i] != 'T'):
        return "Alternância Simples", SUGESTAO[h[-1]], 58

    # 2 Alternância dupla
    if h[-4:] in (["P","P","B","B"], ["B","B","P","P"]):
        return "Alternância Dupla", SUGESTAO[h[-1]], 60

    # 3 Repetição curta
    if h[-1] == h[-2] != "T":
        return "Repetição Curta", "⏸️ AGUARDAR", 54

    # 4 Repetição confirmada
    if h[-1] == h[-2] == h[-3] != "T":
        return "Repetição Confirmada", SUGESTAO[h[-1]], 63

    # 5 Sequência longa
    if len(h) >= 5 and len(set(h[-5:])) == 1 and h[-1] != "T":
        return "Sequência Longa", "⚠️ ALERTA DE QUEBRA", 55

    # 6 Quebra seca
    if h[-3] == h[-2] != h[-1] and h[-1] != "T":
        return "Quebra Seca", "⏸️ AGUARDAR", 50

    # 7 Quebra falsa
    if len(h) >= 4 and h[-4] == h[-3] == h[-1] != h[-2]:
        return "Quebra Falsa", "🚫 NÃO INVERTER", 52

    # 8 Surf curto
    if h[-6:] in (["P","B","B","P","P","B"], ["B","P","P","B","B","P"]):
        return "Surf Curto", SUGESTAO[h[-1]], 61

    # 9 Surf médio
    if h[-6:] in (["P","P","B","B","P","P"], ["B","B","P","P","B","B"]):
        return "Surf Médio", SUGESTAO[h[-1]], 62

    # 10 Surf longo
    if len(h) >= 9 and h[-9:] in (
        ["P","P","P","B","B","B","P","P","P"],
        ["B","B","B","P","P","P","B","B","B"]
    ):
        return "Surf Longo", SUGESTAO[h[-1]], 64

    # 11 Ciclo 2-2
    if h[-4:] in (["P","P","B","B"], ["B","B","P","P"]):
        return "Ciclo 2-2", SUGESTAO[h[-1]], 60

    # 12 Ciclo 3-2
    if h[-5:] in (["P","P","P","B","B"], ["B","B","B","P","P"]):
        return "Ciclo 3-2", SUGESTAO[h[-1]], 60

    # 13 Ciclo 3-3
    if h[-6:] in (["P","P","P","B","B","B"], ["B","B","B","P","P","P"]):
        return "Ciclo 3-3", SUGESTAO[h[-1]], 63

    # 14 Empate isolado
    if h[-1] == "T" and h[-2] != "T":
        return "Empate Isolado", "⏸️ AGUARDAR", 50

    # 15 Empate âncora
    if h[-2] == "T" and h[-1] in ["P","B"]:
        return "Empate Âncora", SUGESTAO[h[-1]], 62

    # 16 Empate antecipador
    if h[-1] == "T" and h[-2] == h[-3] == h[-4] != "T":
        return "Empate Antecipador", "⚠️ INVERSÃO POSSÍVEL", 65

    # 17 Duplo empate
    if h[-2:] == ["T","T"]:
        return "Duplo Empate", "🚫 PAUSAR", 48

    # 18 Zigue-zague quebrado
    if h[-5:] in (["P","B","P","P","B"], ["B","P","B","B","P"]):
        return "Zigue-Zague Quebrado", "🚫 ARMADILHA", 46

    # 19 Caos total
    return "Caos Total", "🚫 NÃO OPERAR", 45

# =============================
# INPUT MANUAL
# =============================
st.subheader("🎯 Inserir resultado")

c1, c2, c3 = st.columns(3)

if c1.button("🔵 Player"):
    st.session_state.hist.append("P")

if c2.button("🔴 Banker"):
    st.session_state.hist.append("B")

if c3.button("🟡 Empate"):
    st.session_state.hist.append("T")

# =============================
# HISTÓRICO VISUAL
# =============================
st.divider()
st.subheader("📜 Histórico (mais recente à esquerda)")

hist_visual = st.session_state.hist[::-1]
emoji_hist = [EMOJIS[h] for h in hist_visual]

st.markdown(" ".join(emoji_hist))

# =============================
# ANÁLISE
# =============================
if st.session_state.hist:
    padrao, sugestao, prob = detectar_padrao(st.session_state.hist)

    st.divider()
    st.subheader("📊 Leitura Atual")

    st.write(f"**Padrão detectado:** {padrao}")
    st.write(f"**Probabilidade:** {prob}%")

    if "NÃO OPERAR" in sugestao or prob < 50:
        st.error(sugestao)
    elif "AGUARDAR" in sugestao or "PAUSAR" in sugestao:
        st.warning(sugestao)
    else:
        st.success(sugestao)

# =============================
# RESET
# =============================
st.divider()
if st.button("♻️ Resetar sessão"):
    st.session_state.hist = []
