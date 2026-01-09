import streamlit as st
from database import FinanceManager
from datetime import datetime

st.set_page_config(page_title="MyGoal - Dashboard", layout="centered")
db = FinanceManager()

# --- DADOS ---
resumo = db.get_financial_summary()
rendas_mes = db.get_current_month_income()
total_renda_mes = sum(item[1] for item in rendas_mes)
gastos_fixos = resumo['monthly_cost']
saldo_disponivel_real = max(resumo['free_balance'], 0.0)

# ==========================================
# SIDEBAR (CONTROLES)
# ==========================================
with st.sidebar:
    st.title("🎮 Painel de Controle")
    
    st.subheader("⚙️ Configuração Base")
    with st.expander("🏠 Gastos Fixos", expanded=True):
        nc = st.number_input("Valor Mensal", value=float(gastos_fixos), step=50.0)
        if st.button("Salvar Ajuste", use_container_width=True):
            db.set_monthly_cost(nc)
            st.rerun()

    st.subheader("📥 Entradas")
    t1, t2 = st.tabs(["Detalhada", "🚀 Rápida"])
    with t1:
        with st.form("f1", clear_on_submit=True):
            n_in = st.text_input("Fonte")
            v_in = st.number_input("Valor R$", min_value=0.0)
            if st.form_submit_button("Registrar", use_container_width=True):
                if n_in and v_in > 0:
                    db.add_transaction(n_in, v_in, "receita", "renda")
                    st.rerun()
    with t2:
        with st.form("f2", clear_on_submit=True):
            v_q = st.number_input("Valor R$", min_value=0.0, key="q")
            if st.form_submit_button("Adicionar Agora", use_container_width=True):
                if v_q > 0:
                    db.add_transaction("Entrada Avulsa", v_q, "receita", "renda")
                    st.rerun()

    with st.expander("📤 Retirar Saldo"):
        with st.form("f3", clear_on_submit=True):
            n_out = st.text_input("Motivo")
            v_out = st.number_input("Valor", min_value=0.0)
            if st.form_submit_button("Confirmar Saída"):
                if n_out and v_out > 0:
                    db.add_transaction(f"RET: {n_out}", v_out, "despesa", "correcao")
                    st.rerun()

    st.subheader("🎯 Novo Projeto")
    with st.form("f4", clear_on_submit=True):
        nn = st.text_input("Nome")
        vv = st.number_input("Alvo", min_value=0.0)
        dd = st.date_input("Prazo")
        if st.form_submit_button("Criar Bloquinho", use_container_width=True):
            if nn and vv > 0:
                db.create_goal(nn, vv, dd)
                st.rerun()

# ==========================================
# CORPO (DASHBOARD) - FORA DA SIDEBAR
# ==========================================
st.title(f"📊 Dashboard de {datetime.now().strftime('%B').capitalize()}")

# --- SEÇÃO 1: RESUMO COMPACTO (4 COLUNAS - CONEXÃO TOTAL) ---
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4) # Agora com 4 colunas
    
    with c1:
        st.caption("💰 RENDA NO MÊS")
        st.subheader(f"R$ {total_renda_mes:,.2f}")
        st.progress(1.0)
    
    with c2:
        st.caption("🏠 GASTOS FIXOS")
        st.subheader(f"R$ {gastos_fixos:,.2f}")
        p2 = min(gastos_fixos / total_renda_mes, 1.0) if total_renda_mes > 0 else 0
        st.progress(p2)

    with c3:
        # NOVO: Somatório de tudo que está nos bloquinhos
        total_alocado = resumo['total_allocated']
        st.caption("🔒 TOTAL ALOCADO")
        st.subheader(f"R$ {total_alocado:,.2f}")
        p3 = min(total_alocado / total_renda_mes, 1.0) if total_renda_mes > 0 else 0
        st.progress(p3)
    
    with c4:
        # DISPONÍVEL: Renda - Gastos Fixos - Total Alocado
        st.caption("✨ DISPONÍVEL AGORA")
        st.subheader(f"R$ {saldo_disponivel_real:,.2f}")
        p4 = min(saldo_disponivel_real / total_renda_mes, 1.0) if total_renda_mes > 0 else 0
        st.progress(p4)

# Alerta de saldo zerado
if saldo_disponivel_real <= 0 and total_renda_mes > 0:
    st.warning("⚠️ Você já distribuiu todo o seu saldo entre Gastos Fixos e Projetos!")

# PROJETOS
st.subheader("🎯 Meus Projetos")
lista_metas = db.get_goals()
if not lista_metas:
    st.info("Crie um projeto na barra lateral.")
else:
    cols = st.columns(2)
    for i, g in enumerate(lista_metas):
        g_id, g_name, g_curr, g_target, g_dead, g_icon = g
        with cols[i % 2].container(border=True):
            st.write(f"### {g_icon} {g_name}")
            st.progress(min(g_curr / g_target, 1.0) if g_target > 0 else 0)
            st.write(f"R$ {g_curr:,.2f} / R$ {g_target:,.2f}")
            with st.popover("Gerenciar Saldo", use_container_width=True):
                val_m = st.number_input("Valor R$", min_value=0.0, key=f"m_{g_id}")
                cb1, cb2 = st.columns(2)
                if cb1.button("Guardar", key=f"in_{g_id}", type="primary"):
                    if val_m <= saldo_disponivel_real:
                        db.update_goal_balance(g_id, val_m)
                        st.rerun()
                if cb2.button("Resgatar", key=f"out_{g_id}"):
                    if val_m <= g_curr:
                        db.update_goal_balance(g_id, -val_m)
                        st.rerun()

st.divider()
with st.expander("📋 Extrato"):
    if rendas_mes:
        st.table([{"Data": datetime.strptime(r[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m'), "Fonte": r[0], "Valor": f"R$ {r[1]:,.2f}"} for r in rendas_mes])