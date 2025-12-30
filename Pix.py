import streamlit as st
from collections import Counter

st.set_page_config(page_title="Football Studio Pro", layout="wide")

emoji = {"R": "🔴", "B": "🔵", "T": "🟡"}

def analisar_padrao(historico):
    if len(historico) < 3:
        return "AGUARDAR", "Minimo 3 resultados", 0, "INSUFICIENTE"
    
    ultimo = historico[-1]
    rec4 = historico[-4:]
    rec3 = historico[-3:]
    rec2 = historico[-2:]
    opp = "R" if ultimo == "B" else "B"
    
    stats = Counter(historico)
    
    # SHOE PESADA (screenshot)
    if len(historico) <= 12:
        dom = max(stats, key=stats.get)
        dom_cnt = stats[dom]
        if dom_cnt >= 4 and rec2 == ["T", opp]:
            return emoji[opp], "SHOE " + dom.upper() + " PESADA + TIE", 95, "SHOE"
    
    # REPETICAO
    streak = 1
    for i in range(2, 7):
        if len(historico) >= i and historico[-i] == ultimo:
            streak += 1
        else:
            break
    
    if streak >= 3:
        return emoji[ultimo], "REPETICAO " + str(streak), 90, "REP"
    
    # ALTERNANCIA
    trocas = sum(1 for i in range(len(historico)-1) if historico[i] != historico[i+1])
    if len(historico) >= 6 and trocas / len(historico) > 0.7:
        return emoji[opp], "ALTERNANCIA", 85, "ALT"
    
    # EMPATE
    if ultimo == "T":
        return "PAUSA", "EMPATE", 0, "TIE"
    
    # QUEBRA
    if len(rec4) == 4 and rec4[:3] == [rec4[0]] * 3 and rec4[-1] != rec4[0]:
        return "PAUSA", "QUEBRA SECA", 0, "BREAK"
    
    return emoji[opp], "BASICO", 60, "BASE"

def mostrar_historico(h):
    if not h:
        return "Clique nos botoes"
    rev = h[::-1]
    linhas = []
    for i in range(0, len(rev), 12):
        linha = rev[i:i+12]
        linhas.append("".join(emoji.get(r, "?") for r in linha))
    return "
".join(linhas)

if "historico" not in st.session_state:
    st.session_state.historico = []

st.title("🏆 Football Studio - Analise Profissional")

col_esq, col_dir = st.columns([3, 1])

with col_esq:
    st.subheader("🎮 Adicionar Resultado")
    
    col_r, col_a, col_e = st.columns(3)
    with col_r:
        if st.button("🔴 Vermelho", use_container_width=True):
            st.session_state.historico.append("R")
            st.rerun()
    with col_a:
        if st.button("🔵 Azul", use_container_width=True):
            st.session_state.historico.append("B")
            st.rerun()
    with col_e:
        if st.button("🟡 Empate", use_container_width=True):
            st.session_state.historico.append("T")
            st.rerun()
    
    st.markdown("---")
    st.subheader("📈 Historico Completo")
    st.code(mostrar_historico(st.session_state.historico))
    
    progresso = min(len(st.session_state.historico) / 64, 1.0)
    st.progress(progresso)
    st.caption(f"Shoe: {len(st.session_state.historico)}/64")

with col_dir:
    st.subheader("🎯 Sugestao de Aposta")
    
    if st.session_state.historico:
        sugestao, motivo, confianca, padrao = analisar_padrao(st.session_state.historico)
        
        stats = Counter(st.session_state.historico)
        
        if confianca > 0:
            st.success(f"### **{sugestao}**")
        else:
            st.error(f"### **{sugestao}**")
        
        st.info(f"**{motivo}**")
        st.caption(f"{confianca}% | {padrao}")
        
        st.metric("Vermelho", stats["R"])
        st.metric("Azul", stats["B"])
        st.metric("Empates", stats["T"])
    else:
        st.warning("Adicione resultados")

st.markdown("---")
if st.button("🗑️ Limpar Tudo", use_container_width=True):
    st.session_state.historico = []
    st.rerun()
