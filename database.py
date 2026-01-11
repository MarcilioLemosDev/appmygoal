import sqlite3
from datetime import datetime

class FinanceManager:
    def __init__(self, db_name="mygoal.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                description TEXT, value REAL, type TEXT, category TEXT, 
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, current_amount REAL DEFAULT 0.0, target_amount REAL DEFAULT 0.0, 
                deadline TEXT, category TEXT DEFAULT 'Outros', icon TEXT DEFAULT '🎯',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
        self.conn.commit()

    # --- GESTÃO DE GASTOS FIXOS (FUNÇÃO QUE ESTAVA FALTANDO) ---
    def set_monthly_cost(self, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('monthly_cost', ?)", (value,))
        self.conn.commit()

    def get_monthly_cost(self):
        try:
            self.cursor.execute("SELECT value FROM settings WHERE key = 'monthly_cost'")
            row = self.cursor.fetchone()
            return row[0] if row else 0.0
        except: return 0.0

    # --- TRANSAÇÕES ---
    def add_transaction(self, description, value, type, category='gasto'):
        self.cursor.execute("INSERT INTO transactions (description, value, type, category) VALUES (?, ?, ?, ?)", (description, value, type, category))
        self.conn.commit()

    def get_current_month_income(self):
        try:
            mes, ano = datetime.now().strftime('%m'), datetime.now().strftime('%Y')
            self.cursor.execute("SELECT description, value, date FROM transactions WHERE type='receita' AND category='renda' AND strftime('%m', date) = ? AND strftime('%Y', date) = ?", (mes, ano))
            return self.cursor.fetchall()
        except: return []

    # --- BLOQUINHOS ---
    def create_goal(self, name, target_amount, deadline, category="Outros"):
        icons = {"Investimento": "📈", "Viagem": "✈️", "Educação": "📚", "Casa": "🏠", "Lazer": "🎡", "Reserva": "🛡️", "Outros": "🎯"}
        icon = icons.get(category, "🎯")
        self.cursor.execute("INSERT INTO goals (name, target_amount, deadline, category, icon) VALUES (?, ?, ?, ?, ?)", (name, target_amount, str(deadline), category, icon))
        self.conn.commit()

    def get_goals(self):
        try:
            self.cursor.execute("SELECT id, name, current_amount, target_amount, deadline, icon, created_at FROM goals")
            return self.cursor.fetchall()
        except: return []

    def update_goal_balance(self, goal_id, amount):
        self.cursor.execute("UPDATE goals SET current_amount = current_amount + ? WHERE id = ?", (amount, goal_id))
        self.conn.commit()

    def update_goal_details(self, goal_id, new_name, new_target):
        self.cursor.execute("UPDATE goals SET name = ?, target_amount = ? WHERE id = ?", (new_name, new_target, goal_id))
        self.conn.commit()

    def delete_goal(self, goal_id):
        self.cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        self.conn.commit()

    # --- SUMÁRIOS E INTELIGÊNCIA ---
    def get_financial_summary(self):
        try:
            self.cursor.execute("SELECT SUM(value) FROM transactions WHERE type='receita'")
            rec = self.cursor.fetchone()[0] or 0.0
            self.cursor.execute("SELECT SUM(value) FROM transactions WHERE type='despesa'")
            desp = self.cursor.fetchone()[0] or 0.0
            self.cursor.execute("SELECT SUM(current_amount) FROM goals")
            aloc = self.cursor.fetchone()[0] or 0.0
            return {"total_global": rec - desp, "total_allocated": aloc, "free_balance": rec - desp - aloc, "monthly_cost": self.get_monthly_cost()}
        except: return {"total_global": 0, "total_allocated": 0, "free_balance": 0, "monthly_cost": 0}

    def get_historical_averages(self):
        try:
            self.cursor.execute("SELECT AVG(mensal) FROM (SELECT SUM(value) as mensal FROM transactions WHERE type='receita' GROUP BY strftime('%m-%Y', date))")
            inc = self.cursor.fetchone()[0] or 0.0
            self.cursor.execute("SELECT COUNT(DISTINCT strftime('%m-%Y', date)) FROM transactions")
            months = max(self.cursor.fetchone()[0] or 1, 1)
            self.cursor.execute("SELECT SUM(current_amount) FROM goals")
            aloc = self.cursor.fetchone()[0] or 0.0
            return inc, aloc / months
        except: return 0.0, 0.0

    def get_goal_metrics(self, goal_id, target_amount, current_amount, deadline_str, created_at_str):
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            created_at = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
            hoje = datetime.now()
            m_rest = max((deadline.year - hoje.year) * 12 + (deadline.month - hoje.month), 1)
            m_desde = max((hoje.year - created_at.year) * 12 + (hoje.month - created_at.month), 1)
            avg = current_amount / m_desde
            falta = max(target_amount - current_amount, 0)
            return {"meses_restantes": m_rest, "avg_aporte_real": avg, "aporte_necessario": falta / m_rest, "meses_estimados_final": (falta / avg) if avg > 0 else 999}
        except: return {"meses_restantes": 1, "avg_aporte_real": 0, "aporte_necessario": 0, "meses_estimados_final": 999}