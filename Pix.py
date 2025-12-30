import streamlit as st

st.set_page_config(page_title="Football Studio PRO", layout="centered")

st.title("🎴 Football Studio – Leitura Profissional de Mesa")

# Inicialização
if "historico" not in st.session_state:
    st.session_state.historico = []

# Função de leitura profissional
def analisar_mesa(h):
    if len(h) < 3:
        return None, "⏳ Aguardando dados suficientes"

    # PÓS-QUEBRA LIMPA
    if len(h) >= 3:
        if h[2] != h[1] and h[1] == h[0]:
            return h[0], "🟢 Entrada pós-quebra (respiração curta)"

    # EMPATE ÂNCORA
    if len(h) >= 3:
        if h[1] == "🟡" and h[0] == h[2]:
            return h[0], "🟢 Confirmação imediata pós-empate"

    # PRIMEIRA REPETIÇÃO
    if len(h) >= 3:
        if h[0] == h[1] and h[1] != h[2]:
            return h[0], "🟢 Primeira repetição (timing correto)"

    # BLOQUEIOS
    if h[0] == h[1] == h[2]:
        return None, "⛔ Topo de padrão detectado (virada iminente)"

    if h[0] != h[1] and h[1] != h[2]:
        return None, "⛔ Alternância falsa (armadilha comum)"

    return None, "⛔ Timing desfavorável — sem entrada"

# Botões de entrada
st.subheader("🎯 Inserir Resultado")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔴 CASA"):
        st.session_state.historico.insert(0, "🔴")

with col2:
    if st.button("🔵 FORA"):
        st.session_state.historico.insert(0, "🔵")

with col3:
    if st.button("🟡 EMPATE"):
        st.session_state.historico.insert(0, "🟡")

# Limite de histórico
st.session_state.historico = st.session_state.historico[:90]

# Exibir histórico
st.subheader("📜 Histórico (mais recente → antigo)")

if st.session_state.historico:
    linhas = [
        st.session_state.historico[i:i+9]
        for i in range(0, len(st.session_state.historico), 9)
    ]
    for linha in linhas[:10]:
        st.write(" ".join(linha))
else:
    st.info("Nenhum resultado inserido ainda.")

# Análise
st.subheader("🧠 Leitura da Mesa")

entrada, motivo = analisar_mesa(st.session_state.historico)

if entrada:
    st.success(f"🎯 SUGESTÃO: Apostar em {entrada}")
    st.write(f"📌 Motivo: {motivo}")
else:
    st.warning(f"🚫 SEM ENTRADA")
    st.write(f"📌 Motivo: {motivo}")

# Rodapé
st.markdown("---")
st.caption("⚠️ Sistema profissional: menos entradas, mais proteção. Timing é tudo.")
