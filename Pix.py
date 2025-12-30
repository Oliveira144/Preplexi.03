import streamlit as st
from collections import Counter

st.set_page_config(page_title="Football Studio PRO", layout="wide")

emoji_map = {'R': '🔴', 'B': '🔵', 'T': '🟡'}

def detect_shoe_pattern(history):
    if len(history) < 3:
        return {"suggestion": "❌ AGUARDAR", "reason": "Minimo 3 resultados", "confidence": 0, "pattern": "INSUFICIENTE"}
    
    shoe_stats = Counter(history)
    last = history[-1]
    recent_6 = history[-6:]
    recent_5 = history[-5:]
    recent_4 = history[-4:]
    recent_3 = history[-3:]
    recent_2 = history[-2:]
    
    next_color = 'R' if last == 'B' else 'B'
    
    # SHOE PESADA (Screenshot)
    if len(history) <= 10:
        dominant_color = max(shoe_stats, key=shoe_stats.get)
        dominant_count = shoe_stats[dominant_color]
        
        if dominant_count >= 3 and recent_2 == ['T', next_color] and shoe_stats[dominant_color] > shoe_stats[next_color] * 1.5:
            return {
                "suggestion": emoji_map[next_color], 
                "reason": f"SHOE {dominant_color.upper()} PESADA + TIE", 
                "confidence": 95, "pattern": "SHOE_INICIO"
            }
    
    # EMPATES (Screenshot fix)
    if last == 'T':
        if recent_2 == ['T', 'T']:
            return {"suggestion": "❌ PAUSA", "reason": "7.5 Duplo empate", "confidence": 0, "pattern": "7.5"}
        if recent_4[:3] == ['B','B','B'] or recent_4[:3] == ['R','R','R']:
            return {"suggestion": "❌ AGUARDAR", "reason": "7.2 Empate pos-repeticao", "confidence": 0, "pattern": "7.2"}
        elif recent_3[:2] == ['R','R'] or recent_3[:2] == ['B','B']:
            return {"suggestion": emoji_map[next_color], "reason": "7.3 Empate quebra", "confidence": 80, "pattern": "7.3"}
        else:
            return {"suggestion": "❌ AGUARDAR", "reason": "7.1 Empate isolado", "confidence": 0, "pattern": "7.1"}
    
    # REPETIÇÕES
    streak = 1
    for i in range(2, min(7, len(history)+1)):
        if len(history) >= i and history[-i] == last:
            streak += 1
        else:
            break
    
    if streak >= 4:
        return {"suggestion": f"{emoji_map[last]} (MIN)", "reason": f"2.3 Repeticao {streak}", "confidence": 70, "pattern": "2.3"}
    elif streak == 3:
        return {"suggestion": emoji_map[last], "reason": "2.2 Repeticao confirmada", "confidence": 90, "pattern": "2.2"}
    
    # ALTERNÂNCIAS
    changes = sum(1 for i in range(len(history)-1) if history[i] != history[i+1])
    alt_ratio = changes / max(1, len(history)-1)
    
    if len(history) >= 6 and alt_ratio >= 0.8:
        return {"suggestion": emoji_map[next_color], "reason": "1.1 Alternancia simples", "confidence": 85, "pattern": "1.1"}
    
    # QUEBRAS
    if len(recent_4) == 4 and recent_4[:3] == [recent_4[0]] * 3 and recent_4[-1] != recent_4[0]:
        return {"suggestion": "❌ PAUSA", "reason": "3.1 Quebra seca", "confidence": 0, "pattern": "3.1"}
    
    # SURF/DUPLA
    blocks = []
    if len(history) >= 4:
        current = history[0]
        count = 1
        for h in history[1:]:
            if h == current:
                count += 1
            else:
                blocks.append((current, count))
                current = h
                count = 1
        blocks.append((current, count))
    
    if len(blocks) >= 2 and blocks[-1][1] == 2:
        return {"suggestion": emoji_map[last], "reason": "4. Surf 2o igual", "confidence": 88, "pattern": "4"}
    
    # CAOS
    if alt_ratio > 0.6:
        return {"suggestion": "❌ PAUSA", "reason": "6.1 Caos", "confidence": 0, "pattern": "6.1"}
    
    return {"suggestion": emoji_map[next_color], "reason": "Padrao basico", "confidence": 60, "pattern": "DEFAULT"}

def format_history(history):
    if not history:
        return "📭 Clique para comecar"
    
    reversed_history = history[::-1]
    lines = []
    for i in range(0, len(reversed_history), 9):
        line = reversed_history[i:i+9]
        lines.append(''.join(emoji_map.get(r, '❓') for r in line))
    
    recent_line = ''.join(emoji_map.get(r, '❓') for r in history[-9:][::-1])
    lines.insert(0, f"🔥 {recent_line}")
    
    return '
'.join(lines)

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🎯 Football Studio PRO")

col_main, col_suggestion = st.columns([3, 1])

with col_main:
    st.subheader("🎮 CONTROLE")
    
    col_r, col_b, col_t = st.columns([1, 1, 1])
    with col_r:
        if st.button("🔴 VERMELHO", use_container_width=True):
            st.session_state.history.append('R')
            st.rerun()
    with col_b:
        if st.button("🔵 AZUL", use_container_width=True):
            st.session_state.history.append('B')
            st.rerun()
    with col_t:
        if st.button("🟡 EMPATE", use_container_width=True):
            st.session_state.history.append('T')
            st.rerun()
    
    st.markdown("---")
    st.subheader("📈 HISTÓRICO")
    st.code(format_history(st.session_state.history))
    
    progress = min(len(st.session_state.history) / 64, 1.0)
    st.progress(progress)
    st.caption(f"Fase: {len(st.session_state.history)//8 + 1}/8")

with col_suggestion:
    st.subheader("🎯 APOSTA")
    
    if st.session_state.history:
        analysis = detect_shoe_pattern(st.session_state.history)
        
        if analysis["confidence"] > 0:
            st.success(f"**{analysis['suggestion']}**")
        else:
            st.error(f"**{analysis['suggestion']}**")
        
        st.info(analysis['reason'])
        conf_color = "🟢" if analysis['confidence'] > 80 else "🟡" if analysis['confidence'] > 50 else "🔴"
        st.caption(f"{conf_color} {analysis['confidence']}% | {analysis['pattern']}")
        
        stats = Counter(st.session_state.history)
        st.metric("Stats", f"{stats['R']}-{stats['B']}-{stats['T']}")
    else:
        st.warning("Insira 3+ resultados")

if st.button("🗑️ LIMPAR", use_container_width=True):
    st.session_state.history = []
    st.rerun()
