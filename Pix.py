import streamlit as st

st.set_page_config("🎴 Football Studio PRO", layout="wide")

# =====================
# MEMÓRIA
# =====================
if "h" not in st.session_state:
    st.session_state.h = []

def add(r):
    st.session_state.h.insert(0, r)
    st.session_state.h = st.session_state.h[:120]

# =====================
# LEITURAS BÁSICAS
# =====================
def sequencia(h):
    if len(h) < 2:
        return None, 0
    c = h[0]
    n = 1
    for x in h[1:]:
        if x == c:
            n += 1
        else:
            break
    return c, n

def dupla_alternada(h):
    if len(h) < 6:
        return False
    return (
        h[0] == h[1] and
        h[2] == h[3] and
        h[0] != h[2]
    )

def empate_ancora(h):
    return len(h) >= 3 and h[1] == "🟡" and h[0] == h[2]

def falso_padrao(h):
    if len(h) < 5:
        return False
    return h[0] != h[1] and h[1] != h[2] and h[2] != h[3]

# =====================
# MOTOR PROFISSIONAL
# =====================
def analisar(h):
    if len(h) < 6:
        return "CAOS", None, 1, "🔴 BLOQUEADO"

    cor, tam = sequencia(h)

    if falso_padrao(h):
        return "FALSO PADRÃO", None, 2, "🔴 ARMADILHA"

    if tam >= 7:
        return "SATURAÇÃO", None, 9, "🔴 SAIR"

    if tam >= 5:
        return "PADRÃO MADURO", cor, 8, "⚠️ ÚLTIMA ENTRADA"

    if tam >= 3:
        return "SEQUÊNCIA SIMPLES", cor, 7, "🟢 ENTRAR"

    if empate_ancora(h):
        return "EMPATE ÂNCORA", h[0], 6, "🟡 ENTRADA CURTA"

    if dupla_alternada(h):
        return "DUPLA ALTERNADA", h[0], 7, "🟢 ENTRAR"

    return "FORMAÇÃO", None, 4, "🕒 AGUARDAR"

# =====================
# INTERFACE
# =====================
st.title("🎴 Football Studio – Leitura de Jogador Profissional")

c1, c2 = st.columns([1,2])

with c1:
    st.subheader("🎮 Entrada Manual")
    if st.button("🔴 Vermelho", use_container_width=True): add("🔴")
    if st.button("🔵 Azul", use_container_width=True): add("🔵")
    if st.button("🟡 Empate", use_container_width=True): add("🟡")
    if st.button("♻️ Resetar Mesa", use_container_width=True):
        st.session_state.h = []

with c2:
    st.subheader("📊 Histórico (recente ➜ antigo)")
    for i in range(0, len(st.session_state.h), 9):
        st.write(" ".join(st.session_state.h[i:i+9]))

st.divider()

estado, sugestao, nivel, acao = analisar(st.session_state.h)

st.subheader("🧠 Diagnóstico Profissional")
st.markdown(f"""
**Estado:** `{estado}`  
**Nível de Leitura:** `{nivel}/9`  
**Ação do Sistema:** **{acao}**
""")

if sugestao:
    st.success(f"🎯 Sugestão atual: **{sugestao}**")

st.caption("""
⚠️ Este sistema replica a leitura dos jogadores experientes:
poucas entradas, risco controlado, saída antecipada.
Não prevê cartas. Não força apostas.
""")
