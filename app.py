import streamlit as st
from database import FinanceManager
from datetime import datetime

st.set_page_config(page_title="MyGoal", layout="centered")
db = FinanceManager()
resumo = db.get_financial_summary()

st.title(f"📅 Ciclo de Janeiro")

# Cálculos de Ciclo
rendas_mes = db.get_current_month_income()
total_renda_mes = sum(item[1] for item in rendas_mes)
custo_fixo = resumo['monthly_cost']
saldo_limpo = max(total_renda_mes - custo_fixo, 0.0)

# --- RESUMO DO CICLO ---
st.subheader("🏁 Resumo do Ciclo")

# Barra 1: Cobertura
perc_cob = min(total_renda_mes / custo_fixo, 1.0) if custo_fixo > 0 else 0
st.write(f"Cobertura do Custo Indispensável: R$ {total_renda_mes:,.2f} / R$ {custo_fixo:,.2f}")
st.progress(perc_cob)

# Barra 2: Saldo Limpo
perc_limpo = (saldo_limpo / total_renda_mes) if total_renda_mes > 0 else 0
st.write(f"Saldo Limpo (Excesso): R$ {saldo_limpo:,.2f}")
st.progress(perc_limpo)

st.divider()

# --- PATRIMÔNIO ---
st.subheader("💰 Patrimônio e Alocação")
total_patrimonio = max(resumo['total_global'], 0.1)

# Barra 3: Saldo Disponível
perc_free = min(resumo['free_balance'] / total_patrimonio, 1.0) if total_patrimonio > 0 else 0
st.write(f"Saldo Disponível em Conta: R$ {resumo['free_balance']:,.2f}")
st.progress(perc_free)

# Barra 4: Alocado
perc_aloc = min(resumo['total_allocated'] / total_patrimonio, 1.0) if total_patrimonio > 0 else 0
st.write(f"Total em Bloquinhos: R$ {resumo['total_allocated']:,.2f}")
st.progress(perc_aloc)

st.divider()

# --- REGISTRO DE RENDA ---
st.subheader("📥 Registrar Nova Renda")
with st.form("renda", clear_on_submit=True):
    c1, c2 = st.columns([2, 1])
    nome = c1.text_input("Fonte")
    valor = c2.number_input("Valor", min_value=0.0)
    if st.form_submit_button("Confirmar Entrada", type="primary"):
        if nome and valor > 0:
            db.add_transaction(nome, valor, "receita", "renda")
            st.rerun()

# --- BLOQUINHOS ---
st.subheader("🎯 Bloquinhos")
lista = db.get_goals()
for g in lista:
    g_id, g_name, g_curr, g_target, g_dead, g_icon = g
    with st.container(border=True):
        st.write(f"**{g_icon} {g_name}** | R$ {g_curr:,.2f} / R$ {g_target:,.2f}")
        st.progress(min(g_curr/g_target, 1.0) if g_target > 0 else 0)
        
        ca, cb = st.columns([2, 1])
        v_aloc = ca.number_input("Quanto guardar?", min_value=0.0, key=f"in_{g_id}")
        if cb.button("Alocar", key=f"btn_{g_id}", use_container_width=True):
            if v_aloc <= resumo['free_balance']:
                db.update_goal_balance(g_id, v_aloc)
                st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Definições")
    nc = st.number_input("Custo Indispensável", value=float(custo_fixo))
    if st.button("Atualizar"):
        db.set_monthly_cost(nc)
        st.rerun()
    
    st.divider()
    with st.form("nova"):
        st.write("Novo Bloquinho")
        nn = st.text_input("Nome")
        vv = st.number_input("Alvo")
        dd = st.date_input("Prazo")
        if st.form_submit_button("Criar"):
            db.create_goal(nn, vv, dd)
            st.rerun()