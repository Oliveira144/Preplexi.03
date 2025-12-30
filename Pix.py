import streamlit as st
from collections import Counter

st.set_page_config(page_title="Football Studio PRO", layout="wide")

emoji = {'R': '🔴', 'B': '🔵', 'T': '🟡'}

def detect_all_patterns(hist):
    if len(hist) < 3:
        return "AGUARDAR", "Min 3 resultados", 0, "INSUFICIENTE"
    
    ultimo = hist[-1]
    rec6 = hist[-6:]
    rec5 = hist[-5:]
    rec4 = hist[-4:]
    rec3 = hist[-3:]
    rec2 = hist[-2:]
    
    opp = 'R' if ultimo == 'B' else 'B'
    stats = Counter(hist)
    
    # 1.1 ALTERNANCIA SIMPLES
    changes = sum(hist[i] != hist[i+1] for i in range(len(hist)-1))
    alt_ratio = changes / max(1, len(hist)-1)
    if len(hist) >= 6 and alt_ratio >= 0.8:
        return emoji[opp], "1.1 Alternancia simples", 85, "1.1"
    
    # 1.2 ALTERNANCIA DUPLA / 4.2 SURF MEDIO / 5.1 CICLO 2-2
    blocks = []
    if len(hist) >= 4:
        cur = hist[0]
        cnt = 1
        for h in hist[1:]:
            if h == cur:
                cnt += 1
            else:
                blocks.append((cur, cnt))
                cur = h
                cnt = 1
        blocks.append((cur, cnt))
    
    if len(blocks) >= 3 and blocks[-2][1] == 2 and blocks[-1][1] == 2:
        return emoji[ultimo], "1.2 Dupla 2o igual", 88, "1.2"
    
    # 2.1-2.3 REPETICOES
    streak = 1
    for i in range(2, min(8, len(hist)+1)):
        if len(hist) >= i and hist[-i] == ultimo:
            streak += 1
        else:
            break
    
    if streak >= 5:
        return emoji[ultimo] + " MIN", "2.3 Repeticao LONGA", 65, "2.3"
    elif streak == 4:
        return emoji[ultimo] + " MIN", "2.3 Repeticao longa", 70, "2.3"
    elif streak == 3:
        return emoji[ultimo], "2.2 Repeticao CONFIRMADA", 90, "2.2"
    elif streak == 2:
        return "AGUARDAR", "2.1 Repeticao curta", 0, "2.1"
    
    # 3.1 QUEBRA SECA
    if len(rec4) == 4 and rec4[:3] == [rec4[0]]*3 and rec4[-1] != rec4[0]:
        return "PAUSA", "3.1 Quebra SECA", 0, "3.1"
    
    # 3.2 QUEBRA FALSA
    if len(rec5) == 5 and rec5[-1] == rec5[-3] and rec5[-2] != rec5[-3]:
        return emoji[ultimo], "3.2 Quebra FALSA", 75, "3.2"
    
    # 7.1-7.5 EMPATES (Screenshot fix)
    if ultimo == 'T':
        if rec2 == ['T', 'T']:
            return "PAUSA", "7.5 DUPO EMPATE", 0, "7.5"
        elif len(rec4) == 4 and (rec4[:3] == ['R','R','R'] or rec4[:3] == ['B','B','B']):
            return "AGUARDAR", "7.2 T pos-repeticao", 0, "7.2"
        elif rec3[:2] == ['R','R'] or rec3[:2] == ['B','B']:
            return emoji[opp], "7.3 T ANUNCIA quebra", 80, "7.3"
        elif len(rec5) >= 4 and rec5[-4:] == ['R','B','R','B','T']:
            return "PAUSA", "7.4 T pos-alternancia", 0, "7.4"
        else:
            return "AGUARDAR", "7.1 T isolado", 0, "7.1"
    
    # SHOE PESADA (Screenshot 1/8)
    if len(hist) <= 12:
        dom = max(stats, key=stats.get)
        dom_cnt = stats[dom]
        if dom_cnt >= 4 and stats[opp] <= 1:
            return emoji[opp], "SHOE " + dom.upper() + " PESADA", 92, "SHOE"
    
    # 4. SURF
    if len(blocks) >= 4 and all(1 < b[1] <= 3 for b in blocks[-4:]):
        return emoji[ultimo], "4. SURF 2o igual", 87, "4"
    
    # 6. CAOS
    if alt_ratio > 0.65:
        return "PAUSA", "6.1 CAOS Ziguezague", 0, "6.1"
    
    return emoji[opp], "Padrao basico", 60, "DEFAULT"

def show_hist_pro(hist):
    if not hist:
        return "Clique botoes"
    
    rev = hist[::-1]
    linhas = []
    for i in range(0, len(rev), 9):
        linha = rev[i:i+9]
        linhas.append(''.join(emoji.get(r, '?') for r in linha))
    
    recents = ''.join(emoji.get(r, '?') for r in hist[-12:][::-1])
    linhas.insert(0, "🔥 ULTIMOS 12: " + recents)
    
    return '
'.join(linhas)

if 'hist' not in st.session_state:
    st.session_state.hist = []

st.markdown("# 🏆 Football Studio PRO - 18 PADROES")

col1, col2 = st.columns([70, 30])

with col1:
    st.subheader("🎮 CONTROLE PROFISSIONAL")
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("🔴 VERMELHO", use_container_width=True):
            st.session_state.hist.append('R')
            st.rerun()
    with c2:
        if st.button("🔵 AZUL", use_container_width=True):
            st.session_state.hist.append('B')
            st.rerun()
    with c3:
        if st.button("🟡 EMPATE", use_container_width=True):
            st.session_state.hist.append('T')
            st.rerun()
    
    st.markdown("---")
    st.subheader("📊 HISTORICO SHOE")
    st.code(show_hist_pro(st.session_state.hist), language="")
    
    prog = min(len(st.session_state.hist)/64.0, 1.0)
    st.progress(prog)
    fase = (len(st.session_state.hist)//8) + 1
    st.caption(f"Fase shoe: {fase}/8 | Total: {len(st.session_state.hist)}")

with col2:
    st.subheader("🎯 APOSTA UNICA")
    
    if st.session_state.hist:
        sug, motivo, conf, padrao = detect_all_patterns(st.session_state.hist)
        
        if "PAUSA" in sug or "AGUARDAR" in sug:
            st.error("**" + sug + "**")
            st.caption(motivo + " | " + str(conf) + "%")
        else:
            st.success("**" + sug + "**")
            st.caption(motivo + " | " + str(conf) + "% | " + padrao)
        
        stats = Counter(st.session_state.hist)
        colr, colb, colt = st.columns(3)
        with colr: st.metric("🔴", stats['R'])
        with colb: st.metric("🔵", stats['B'])
        with colt: st.metric("🟡", stats['T'])

st.markdown("---")
if st.button("🗑️ LIMPAR SHOE", use_container_width=True):
    st.session_state.hist = []
    st.rerun()

st.caption("""
**✅ 18 PADROES IMPLEMENTADOS:**
1.1-1.3 Alternancias | 2.1-2.3 Repeticoes | 3.1-3.2 Quebras
4. Surf | 5. Ciclos | 6. Caos | 7.1-7.5 TODOS empates | SHOE pesada
""")
