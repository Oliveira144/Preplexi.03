import streamlit as st
from collections import Counter
import numpy as np

st.set_page_config("Football Studio IA v3.4", layout="wide")
st.title("🧠 Football Studio – IDENTIFICAÇÃO PERFEITA v3.4")

if "h" not in st.session_state:
    st.session_state.h = []
    st.session_state.shoe = 0
    st.session_state.loss_streak = 0
    st.session_state.last_bet = None

# BOTÕES
col1, col2, col3, col_undo, col_reset = st.columns([1, 1, 1, 0.8, 0.5])

with col1:
    if st.button("🔴 VERMELHO", use_container_width=True):
        st.session_state.h.insert(0, "R")
        st.session_state.shoe += 1
        if st.session_state.last_bet == "B": st.session_state.loss_streak += 1
        st.session_state.last_bet = None
        st.rerun()

with col2:
    if st.button("🔵 AZUL", use_container_width=True):
        st.session_state.h.insert(0, "B")
        st.session_state.shoe += 1
        if st.session_state.last_bet == "R": st.session_state.loss_streak += 1
        st.session_state.last_bet = None
        st.rerun()

with col3:
    if st.button("🟡 EMPATE", use_container_width=True):
        st.session_state.h.insert(0, "E")
        st.session_state.shoe += 1
        st.session_state.last_bet = None
        st.rerun()

with col_undo:
    if st.button("↶ DESFAZER", use_container_width=True):
        if st.session_state.h:
            st.session_state.h.pop(0)
            st.session_state.shoe -= 1
            st.rerun()

with col_reset:
    if st.button("♻️", use_container_width=True):
        st.session_state = {"h": [], "shoe": 0, "loss_streak": 0, "last_bet": None}
        st.rerun()

st.session_state.h = st.session_state.h[:120]

# BIG EYE ROAD - IDENTIFICA EXATAMENTE SEUS PADRÕES
def big_eye_road(h):
    if len(h) < 6: return None
    eye = ['R' if h[i] == h[i-2] else 'B' for i in range(2, len(h))]
    recent = eye[-6:]
    reds = recent.count('R')
    if reds >= 4: return ("🔴 BIG EYE: REPETIÇÃO", "seguir", 35)
    if reds <= 2: return ("🔵 BIG EYE: CHOPPY", "contrariar", 32)
    return None

# SURF EXATO DAS SUAS IMAGENS
def detectar_surf(h):
    if not h or h[0] == "E": return None
    cor = h[0]; count = 0
    for x in h[:10]:  # Olha 10 primeiras
        if x == cor: count += 1
        else: break
    if count >= 5: return ("🚫 SURF ≥5", "pausa", 0)
    if count == 4: return ("🌊 Surf 4", "seguir", 35)
    if count == 3: return ("🌊 Surf 3", "seguir", 28)
    if count == 2: return ("🌊 Surf 2", "seguir", 22)  # SEU PADRÃO AZUL x2
    return None

# PADRÕES GERAIS
def detectar_padroes(h):
    padroes = []
    
    # Big Eye (prioridade máxima)
    bigeye = big_eye_road(h)
    if bigeye: padroes.append(bigeye)
    
    # Surf (segundo)
    surf = detectar_surf(h)
    if surf: padroes.append(surf)
    
    # Seus padrões específicos
    if len(h) >= 6:
        ultimos6 = h[:6]
        if ultimos6[:4] in [["R","B","R","B"], ["B","R","B","R"]]:
            padroes.append(("🔄 ALTERNÂNCIA 4", "neutro", 18))
        if ultimos6.count("R") == ultimos6.count("B") == 3:
            padroes.append(("⚖️ SIMETRIA 3x3", "alerta", 20))
    
    return padroes

# DECISÃO MELHORADA
def decidir(h):
    if len(h) < 6: return None, {}, [], "AGUARDAR"
    
    score = {"R": 0, "B": 0, "conf": 0}
    padroes = detectar_padroes(h)
    
    for nome, tipo, peso in padroes:
        score["conf"] += peso * 0.85
        
        # ANTI-FOSSAR AGRESSIVO
        if st.session_state.loss_streak >= 1:
            peso *= 0.5  # Metade após 1 perda
        
        if tipo == "pausa": return None, score, padroes, "PAUSAR"
        if tipo == "seguir" and h[0] in ("R","B"):
            score[h[0]] += peso
        if tipo == "contrariar":
            opp = "B" if h[0] == "R" else "R"
            score[opp] += peso
    
    # PAUSA AUTOMÁTICA se confiança baixa OU perda recente
    if score["conf"] < 25 or st.session_state.loss_streak >= 2:
        return None, score, padroes, "PAUSAR"
    
    lado = "R" if score["R"] >= score["B"] else "B"
    return lado, score, [p[0] for p in padroes], "ENTRAR"

# RENDER
def render(h):
    mapa = {"R": "🔴", "B": "🔵", "E": "🟡"}
    for i in range(0, len(h), 12):
        st.write(" ".join(mapa[x] for x in h[i:i+12]))

st.subheader("📊 Mesa Completa")
col1, col2, col3 = st.columns([3,1,1])
with col1: render(st.session_state.h)
with col2: 
    progress = min(100, (st.session_state.shoe % 416) / 416 * 100)
    st.metric("Shoe", f"{st.session_state.shoe//52+1}/8")
with col3:
    st.metric("⚠️ Losses", st.session_state.loss_streak)

# PAINEL
if len(st.session_state.h) >= 6:
    st.divider()
    lado, score, padroes, acao = decidir(st.session_state.h)
    
    col_dec, col_score = st.columns([1,1])
    with col_dec:
        st.markdown("### 🧠 **DECISÃO**")
        if acao == "PAUSAR":
            st.error("⛔ **PAUSAR**")
        elif acao == "ENTRAR":
            emoji = "🔴" if lado == "R" else "🔵"
            st.success(f"🚀 **APOSTAR {emoji}**")
        else:
            st.info("⏳ **AGUARDAR**")
    
    with col_score:
        st.markdown("### 📊 SCORES")
        st.metric("🔴 R", f"{score['R']:.0f}")
        st.metric("🔵 B", f"{score['B']:.0f}")
    
    if padroes:
        st.markdown("### 🔍 **PADRÕES DETECTADOS**")
        for p in padroes[:4]:
            st.write(f"• **{p}**")

st.caption("v3.4: IDENTIFICA seus padrões AZULx2 + pausa agressiva [file:68]")
