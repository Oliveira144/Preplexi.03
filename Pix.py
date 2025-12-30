import streamlit as st
from collections import Counter

st.set_page_config(page_title="Football Studio", layout="wide")
emoji = {'R': '🔴', 'B': '🔵', 'T': '🟡'}

def detect_pattern(hist):
    if len(hist) < 3:
        return {"sug": "AGUARDAR", "motivo": "3+ resultados", "conf": 0}
    
    ultimo = hist[-1]
    rec4 = hist[-4:]
    rec3 = hist[-3:]
    rec2 = hist[-2:]
    
    opp = 'R' if ultimo == 'B' else 'B'
    
    if len(hist) <= 10 and rec2 == ['T', opp]:
        dom = max(Counter(hist), key=Counter(hist).get)
        if Counter(hist)[dom] >= 3:
            return {"sug": emoji[opp], "motivo": "SHOE PESADA", "conf": 95}
    
    if ultimo == 'T':
        if rec2 == ['T', 'T']:
            return {"sug": "PAUSA", "motivo": "Duplo T", "conf": 0}
        if rec4[:3] == ['B','B','B'] or rec4[:3] == ['R','R','R']:
            return {"sug": "AGUARDAR", "motivo": "T pos repeticao", "conf": 0}
        return {"sug": "AGUARDAR", "motivo": "T isolado", "conf": 0}
    
    streak = 1
    for i in range(2, 6):
        if len(hist) >= i and hist[-i] == ultimo:
            streak += 1
        else:
            break
    
    if streak >= 3:
        return {"sug": emoji[ultimo], "motivo": "Repeticao " + str(streak), "conf": 90}
    
    changes = sum(hist[i] != hist[i+1] for i in range(len(hist)-1))
    if len(hist) >= 6 and changes / len(hist) > 0.7:
        return {"sug": emoji[opp], "motivo": "Alternancia", "conf": 85}
    
    return {"sug": emoji[opp], "motivo": "Basico", "conf": 60}

def show_hist(hist):
    if not hist:
        return "Clique botao"
    rev = hist[::-1]
    linhas = []
    for i in range(0, len(rev), 9):
        linha = rev[i:i+9]
        linhas.append(''.join(emoji.get(r, '?') for r in linha))
    return '
'.join(linhas)

if 'hist' not in st.session_state:
    st.session_state.hist = []

st.title("Football Studio PRO")

col1, col2 = st.columns([3,1])

with col1:
    st.subheader("BOTOES")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔴 R"):
            st.session_state.hist.append('R')
            st.rerun()
    with c2:
        if st.button("🔵 B"):
            st.session_state.hist.append('B')
            st.rerun()
    with c3:
        if st.button("🟡 T"):
            st.session_state.hist.append('T')
            st.rerun()
    
    st.markdown("---")
    st.subheader("HISTORICO")
    st.code(show_hist(st.session_state.hist))
    
    p = min(len(st.session_state.hist)/64, 1)
    st.progress(p)

with col2:
    st.subheader("SUGESTAO")
    if st.session_state.hist:
        analise = detect_pattern(st.session_state.hist)
        if analise["conf"] > 0:
            st.success(analise["sug"])
        else:
            st.error(analise["sug"])
        st.caption(analise["motivo"] + " " + str(analise["conf"]) + "%")
        
        stats = Counter(st.session_state.hist)
        st.metric("R-B-T", f"{stats['R']}-{stats['B']}-{stats['T']}")

if st.button("LIMPAR"):
    st.session_state.hist = []
    st.rerun()
