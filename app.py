import streamlit as st
from database import FinanceManager
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="MyGoal | Consultoria", layout="centered", page_icon="🚀")

# --- ESTILIZAÇÃO UI PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 800; }
    .stProgress > div > div > div > div { background-color: #6d28d9; }
    [data-testid="stExpander"] { border: 1px solid #30363d; border-radius: 12px; background-color: #161b22; }
    .insight-card { padding: 10px; border-radius: 8px; margin-top: 5px; border-left: 5px solid #6d28d9; background: #1e1e2e; }
    </style>
    """, unsafe_allow_html=True)

db = FinanceManager()

# --- PROCESSAMENTO DE DADOS ---
resumo = db.get_financial_summary()
rendas_mes = db.get_current_month_income()
total_renda_mes = sum(item[1] for item in rendas_mes) if rendas_mes else 0.0
gastos_fixos = resumo['monthly_cost']
total_alocado = resumo['total_allocated']
saldo_seguranca = max(resumo['free_balance'], 0.0)

# Inteligência de Médias
avg_income, avg_allocated = db.get_historical_averages()

# ==========================================
# SIDEBAR (CONTROLES)
# ==========================================
with st.sidebar:
    st.title("🎯 MyGoal")
    st.caption("Do Saldo ao Propósito")
    
    st.divider()
    
    with st.expander("🏠 Definir Gastos Fixos"):
        nc = st.number_input("Custo de Vida Mensal", value=float(gastos_fixos))
        if st.button("Salvar Ajuste"):
            db.set_monthly_cost(nc)
            st.rerun()

    st.subheader("📥 Entradas")
    t1, t2 = st.tabs(["Identificada", "🚀 Rápida"])
    with t1:
        with st.form("f_det", clear_on_submit=True):
            n_in = st.text_input("Fonte")
            v_in = st.number_input("Valor R$", min_value=0.0)
            if st.form_submit_button("Registrar"):
                if n_in and v_in > 0:
                    db.add_transaction(n_in, v_in, "receita", "renda")
                    st.rerun()
    with t2:
        with st.form("f_rap", clear_on_submit=True):
            v_q = st.number_input("Valor R$", min_value=0.0, key="quick")
            if st.form_submit_button("Adição Instantânea", type="primary"):
                if v_q > 0:
                    db.add_transaction("Entrada Avulsa", v_q, "receita", "renda")
                    st.rerun()

    st.divider()
    st.subheader("🎯 Novo Projeto")
    with st.form("f_meta_new", clear_on_submit=True):
        nn = st.text_input("Nome do Projeto")
        vv = st.number_input("Valor Alvo R$", min_value=0.0)
        cat = st.selectbox("Tipo", ["Investimento", "Viagem", "Educação", "Casa", "Lazer", "Reserva", "Outros"])
        dd = st.date_input("Prazo Final")
        if st.form_submit_button("Criar Bloquinho", use_container_width=True):
            if nn and vv > 0:
                db.create_goal(nn, vv, dd, cat)
                st.rerun()

# ==========================================
# DASHBOARD (INTELIGÊNCIA)
# ==========================================
st.title("Inteligência e Performance")

# Painel Atual vs Histórico
tab_mes, tab_historico = st.tabs(["📍 Status do Ciclo", "📊 Desempenho Médio"])

with tab_mes:
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Renda Atual", f"R$ {total_renda_mes:,.2f}")
        c2.metric("Gastos Fixos", f"R$ {gastos_fixos:,.2f}")
        c3.metric("Alocado", f"R$ {total_alocado:,.2f}")
        
        destinado = gastos_fixos + total_alocado
        p_dest = min(destinado / total_renda_mes, 1.0) if total_renda_mes > 0 else 0
        st.progress(p_dest, text=f"{int(p_dest*100)}% da renda destinada")

with tab_historico:
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("Renda Média", f"R$ {avg_income:,.2f}")
        m2.metric("Média Guardada", f"R$ {avg_allocated:,.2f}")
        eficiencia = (avg_allocated / avg_income * 100) if avg_income > 0 else 0
        m3.metric("Eficiência", f"{eficiencia:.1f}%")
        st.caption("A eficiência mostra o quanto da sua renda média vira patrimônio.")

st.divider()

# ==========================================
# PROJETOS COM INSIGHTS
# ==========================================
st.subheader("🚀 Seus Bloquinhos")
lista_metas = db.get_goals()

if not lista_metas:
    st.info("Crie um projeto para ver as projeções.")
else:
    cols = st.columns(2)
    for i, g in enumerate(lista_metas):
        # Desempacotando id, nome, atual, alvo, prazo, ícone, data_criacao
        g_id, g_name, g_curr, g_target, g_dead, g_icon, g_created = g
        
        # Cálculo de Métricas de Consultoria
        metrics = db.get_goal_metrics(g_id, g_target, g_curr, g_dead, g_created)
        
        with cols[i % 2].container(border=True):
            st.markdown(f"### {g_icon} {g_name}")
            st.progress(min(g_curr/g_target, 1.0) if g_target > 0 else 0)
            
            # Sub-métricas do Bloquinho
            sm1, sm2 = st.columns(2)
            sm1.metric("Aporte Médio", f"R$ {metrics['avg_aporte_real']:,.2f}")
            # Delta indica se está acima ou abaixo do necessário
            dif_ritmo = metrics['avg_aporte_real'] - metrics['aporte_necessario']
            sm2.metric("Necessário", f"R$ {metrics['aporte_necessario']:,.2f}", 
                       delta=f"{dif_ritmo:,.2f}", delta_color="normal")
            
            # --- INSIGHTS VALIOSOS ---
            with st.expander("💡 Insights e Projeções"):
                # Insight 1: Ajuste de Rota
                if dif_ritmo < 0:
                    st.warning(f"**Ajuste de Rota:** Faltam R$ {abs(dif_ritmo):,.2f}/mês para bater o prazo.")
                else:
                    st.success("**Meta Saudável:** Ritmo superior ao planejado.")
                
                # Insight 2: Previsão Realista
                meses_reais = metrics['meses_estimados_final']
                if meses_reais < 999:
                    st.info(f"**Previsão Real:** Conclusão em approx. {meses_reais:.1f} meses.")
                else:
                    st.error("**Ação Necessária:** Aporte atual não permite previsão de conclusão.")

            # Gerenciamento
            b1, b2 = st.columns(2)
            with b1:
                with st.popover("💰 Saldo", use_container_width=True):
                    val = st.number_input("Valor", min_value=0.0, key=f"v_{g_id}")
                    if st.button("Guardar", key=f"g_{g_id}", type="primary"):
                        if val <= saldo_seguranca:
                            db.update_goal_balance(g_id, val)
                            st.rerun()
                        else: st.error("Sem saldo!")
                    if st.button("Resgatar", key=f"r_{g_id}"):
                        db.update_goal_balance(g_id, -val); st.rerun()
            with b2:
                with st.popover("⚙️ Editar", use_container_width=True):
                    nn = st.text_input("Nome", value=g_name, key=f"n_{g_id}")
                    vv = st.number_input("Alvo", value=float(g_target), key=f"t_{g_id}")
                    if st.button("Salvar", key=f"s_{g_id}"):
                        db.update_goal_details(g_id, nn, vv); st.rerun()
                    if st.button("Excluir", key=f"d_{g_id}"):
                        db.delete_goal(g_id); st.rerun()

st.divider()
with st.expander("📋 Extrato de Rendas"):
    if rendas_mes:
        st.table([{"Data": datetime.strptime(r[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m'), 
                   "Fonte": r[0], "Valor": f"R$ {r[1]:,.2f}"} for r in rendas_mes])