import streamlit as st

# =====================
# CONFIG
# =====================
st.set_page_config(
    page_title="Football Studio – Trader de Padrões",
    layout="wide"
)

st.set_option("client.showErrorDetails", False)

# =====================
# ESTADO
# =====================
if "history" not in st.session_state:
    st.session_state.history = []

if "banca" not in st.session_state:
    st.session_state.banca = 1000.00

# =====================
# FUNÇÕES BÁSICAS
# =====================
def add_result(result: str):
    # Mais recente à esquerda
    st.session_state.history.insert(0, result)

def reset():
    st.session_state.history = []
    st.session_state.banca = 1000.00

def chunk_history(hist, size=15):
    return [hist[i:i + size] for i in range(0, len(hist), size)]

# =====================
# MOTOR DE PADRÕES (COMPLETO)
# =====================
def analyze(history):
    n = len(history)
    if n < 4:
        return "Dados insuficientes", "Aguardando formação", "AGUARDAR", 0.50

    # ----------------------
    # JANELAS
    # ----------------------
    recent6 = history[:6]      # leitura curta
    recent10 = history[:10]    # leitura média
    recent20 = history[:20]    # leitura de modo da mesa

    last = history[0]

    # ----------------------
    # CONTAGENS LOCAIS
    # ----------------------
    r6_red = recent6.count("🔴")
    r6_blue = recent6.count("🔵")
    r6_tie = recent6.count("🟡")

    # ----------------------
    # MODO DA MESA (GLOBAL)
    # ----------------------
    def media_run(seq, alvo):
        runs = []
        atual = 0
        for x in seq:
            if x == alvo:
                atual += 1
            else:
                if atual > 0:
                    runs.append(atual)
                atual = 0
        if atual > 0:
            runs.append(atual)
        return sum(runs) / len(runs) if runs else 0.0

    m_run_red = media_run(recent20, "🔴")
    m_run_blue = media_run(recent20, "🔵")
    streak_force = max(m_run_red, m_run_blue) - 1.0

    trocas = 0
    comparaveis = 0
    for i in range(min(len(recent20) - 1, 19)):
        a, b = recent20[i], recent20[i + 1]
        if a in ("🔴", "🔵") and b in ("🔴", "🔵"):
            comparaveis += 1
            if a != b:
                trocas += 1
    zigzag_ratio = trocas / comparaveis if comparaveis > 0 else 0.0

    blocos2 = 0
    for i in range(min(len(recent20) - 1, 19)):
        a, b = recent20[i], recent20[i + 1]
        if a == b and a in ("🔴", "🔵"):
            blocos2 += 1
    blocos2_ratio = blocos2 / max(1, comparaveis)

    modo = "NEUTRO"
    if streak_force >= 1.0:          # média de runs >= 2
        modo = "STREAKY"
    elif zigzag_ratio >= 0.7:        # 70%+ das vezes troca de lado
        modo = "ZIGZAG"
    elif blocos2_ratio >= 0.5:       # muitos pares seguidos
        modo = "BLOCK"

    # ----------------------
    # PADRÕES LOCAIS DE COR
    # ----------------------

    # 1️⃣ EXTENSÃO FORTE (últimos 4 iguais)
    if n >= 4 and len(set(history[:4])) == 1 and last in ("🔴", "🔵"):
        lado = "BANQUEIRO 🔴" if last == "🔴" else "JOGADOR 🔵"
        return (
            f"Extensão forte {last}",
            "Sequência longa consolidada",
            f"ENTRAR {lado}",
            0.64
        )

    # 2️⃣ EXTENSÃO LOCAL (4+ iguais nos últimos 6)
    if last != "🟡":
        if r6_red >= 4 and last == "🔴":
            return (
                "Extensão 🔴",
                "Predomínio recente de BANQUEIRO",
                "ENTRAR BANQUEIRO 🔴",
                0.60
            )
        if r6_blue >= 4 and last == "🔵":
            return (
                "Extensão 🔵",
                "Predomínio recente de JOGADOR",
                "ENTRAR JOGADOR 🔵",
                0.60
            )

    # 3️⃣ REPETIÇÃO CURTA (dois últimos iguais, sem empate)
    if n >= 2 and history[0] == history[1] and history[0] != "🟡":
        lado = "BANQUEIRO 🔴" if history[0] == "🔴" else "JOGADOR 🔵"
        return (
            "Repetição curta",
            "Curta sequência com chance de continuação",
            f"ENTRAR {lado} (stake baixa)",
            0.56
        )

    # 4️⃣ ALTERNÂNCIA LOCAL (últimos 6 trocando)
    if n >= 6:
        alterna = True
        for i in range(5):
            if history[i] == history[i + 1]:
                alterna = False
                break
        if alterna and last in ("🔴", "🔵"):
            alvo = "JOGADOR 🔵" if last == "🔴" else "BANQUEIRO 🔴"
            return (
                "Alternância",
                "Mesa alternando entre os lados",
                f"ENTRAR {alvo}",
                0.55
            )

    # ----------------------
    # PADRÕES DE EMPATE
    # ----------------------
    if last == "🟡" and n > 1:
        prev = history[1]

        # 5.1 Empates frequentes (mesa travada)
        ties_recent6 = history[:6].count("🟡")
        if ties_recent6 >= 2:
            return (
                "Empates frequentes",
                "Muitos empates recentes, mesa de alta variância",
                "AGUARDAR",
                0.48
            )

        # 5.2 Empate após streak forte (3+ iguais antes do empate)
        if n >= 4 and prev in ("🔴", "🔵"):
            antes = history[1:4]  # posições 1,2,3
            if len(set(antes)) == 1 and antes[0] in ("🔴", "🔵"):
                lado_txt = "BANQUEIRO 🔴" if antes[0] == "🔴" else "JOGADOR 🔵"
                return (
                    "Empate após streak",
                    "Empate interrompeu uma sequência forte, tendência pode retomar",
                    f"ENTRAR {lado_txt}",
                    0.58
                )

        # 5.3 Empate âncora simples (default)
        if prev in ("🔴", "🔵"):
            lado_txt = "BANQUEIRO 🔴" if prev == "🔴" else "JOGADOR 🔵"
            return (
                "Empate âncora",
                "Retomada provável do lado anterior ao empate",
                f"ENTRAR {lado_txt}",
                0.54
            )

    # ----------------------
    # OUTROS PADRÕES LOCAIS
    # ----------------------

    # 6️⃣ QUEBRA DE EXTENSÃO (A B B B)
    if n >= 4:
        a, b, c, d = history[0], history[1], history[2], history[3]
        if a != b and b == c == d and b in ("🔴", "🔵") and a in ("🔴", "🔵"):
            lado = "BANQUEIRO 🔴" if a == "🔴" else "JOGADOR 🔵"
            return (
                "Quebra de extensão",
                "Correção após sequência longa",
                f"ENTRAR {lado}",
                0.58
            )

    # 7️⃣ COMPRESSÃO (empate + equilíbrio)
    if r6_tie >= 1 and abs(r6_red - r6_blue) <= 1:
        return (
            "Compressão",
            "Mesa travada / sem dominância clara",
            "AGUARDAR",
            0.48
        )

    # 8️⃣ FALSO PADRÃO (3x2 nos últimos 5)
    recent5 = history[:5]
    if len(recent5) == 5:
        if recent5.count("🔴") == 3 and recent5.count("🔵") == 2:
            return (
                "Falso padrão 🔴",
                "Distribuição 3x2 pode enganar",
                "AGUARDAR",
                0.47
            )
        if recent5.count("🔵") == 3 and recent5.count("🔴") == 2:
            return (
                "Falso padrão 🔵",
                "Distribuição 3x2 pode enganar",
                "AGUARDAR",
                0.47
            )

    # ----------------------
    # USO DO MODO DA MESA
    # ----------------------
    if modo == "STREAKY" and last in ("🔴", "🔵"):
        lado = "BANQUEIRO 🔴" if last == "🔴" else "JOGADOR 🔵"
        return (
            "Modo STREAKY",
            "Mesa em tendência forte, surfando a favor",
            f"ENTRAR {lado}",
            0.57
        )

    if modo == "ZIGZAG" and last in ("🔴", "🔵"):
        alvo = "JOGADOR 🔵" if last == "🔴" else "BANQUEIRO 🔴"
        return (
            "Modo ZIGZAG",
            "Mesa alternando com frequência",
            f"ENTRAR {alvo}",
            0.55
        )

    if modo == "BLOCK":
        if n >= 2 and history[0] == history[1] and history[0] in ("🔴", "🔵"):
            lado = "BANQUEIRO 🔴" if history[0] == "🔴" else "JOGADOR 🔵"
            return (
                "Modo BLOCK",
                "Mesa formando blocos de 2+",
                f"ENTRAR {lado}",
                0.55
            )

    # 9️⃣ ZONA NEUTRA
    return "Zona neutra", "Sem padrão confiável", "AGUARDAR", 0.50

# =====================
# GESTÃO SIMPLIFICADA
# =====================
def sugere_stake(banca, confianca):
    """
    Traduz a confiança (0.5–0.64) em stake.
    50% → 0
    56% → ~0.5% da banca
    64% → ~1.5% da banca
    """
    if confianca <= 0.52:
        return 0.0
    edge = confianca - 0.5
    fração = min(0.015, 0.005 + edge * 0.15)
    return round(banca * fração, 2)

# =====================
# INTERFACE
# =====================
st.title("⚽ Football Studio – Trader de Padrões")
st.caption("🔵 Jogador | 🔴 Banqueiro | 🟡 Empate")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔵 Jogador", use_container_width=True):
        add_result("🔵")
        st.rerun()

with col2:
    if st.button("🔴 Banqueiro", use_container_width=True):
        add_result("🔴")
        st.rerun()

with col3:
    if st.button("🟡 Empate", use_container_width=True):
        add_result("🟡")
        st.rerun()

with col4:
    if st.button("♻️ Reset", use_container_width=True):
        reset()
        st.rerun()

st.divider()

# HISTÓRICO
st.subheader("📊 Histórico (mais recente à esquerda)")
if st.session_state.history:
    for row in chunk_history(st.session_state.history, size=15):
        st.markdown(" ".join(row))
else:
    st.caption("Ainda sem dados. Comece a registrar os resultados da mesa.")

# ANÁLISE
padrao, estado, sugestao, confianca = analyze(st.session_state.history)
stake = sugere_stake(st.session_state.banca, confianca)

st.divider()
st.subheader("🧠 Leitura da Mesa")

col_a, col_b = st.columns(2)
with col_a:
    st.write(f"**Padrão identificado:** {padrao}")
    st.write(f"**Estado da mesa:** {estado}")
with col_b:
    st.write(f"**Confiança estimada:** {confianca:.1%}")
    st.write(f"**Stake sugerida:** R$ {stake}")

st.success(f"Sugestão operacional: {sugestao}")
st.caption("⚠️ Leitura de padrões e gestão de stake. Não existe garantia de ganho.")
