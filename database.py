import sqlite3
from datetime import datetime

class FinanceManager:
    def __init__(self, db_name="mygoal.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, value REAL, type TEXT, category TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, current_amount REAL DEFAULT 0.0, target_amount REAL DEFAULT 0.0, deadline TEXT, icon TEXT DEFAULT '🎯')")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
        self.conn.commit()

    def set_monthly_cost(self, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('monthly_cost', ?)", (value,))
        self.conn.commit()

    def get_monthly_cost(self):
        self.cursor.execute("SELECT value FROM settings WHERE key = 'monthly_cost'")
        row = self.cursor.fetchone()
        return row[0] if row else 0.0

    def add_transaction(self, description, value, type, category='gasto'):
        self.cursor.execute("INSERT INTO transactions (description, value, type, category) VALUES (?, ?, ?, ?)", (description, value, type, category))
        self.conn.commit()

    def get_current_month_income(self):
        mes = datetime.now().strftime('%m')
        ano = datetime.now().strftime('%Y')
        self.cursor.execute("SELECT description, value, date FROM transactions WHERE type='receita' AND category='renda' AND strftime('%m', date) = ? AND strftime('%Y', date) = ?", (mes, ano))
        return self.cursor.fetchall()

    def get_goals(self):
        self.cursor.execute("SELECT id, name, current_amount, target_amount, deadline, icon FROM goals")
        return self.cursor.fetchall()

    def update_goal_balance(self, goal_id, amount):
        self.cursor.execute("UPDATE goals SET current_amount = current_amount + ? WHERE id = ?", (amount, goal_id))
        self.conn.commit()

    def create_goal(self, name, target_amount, deadline):
        self.cursor.execute("INSERT INTO goals (name, target_amount, deadline) VALUES (?, ?, ?)", (name, target_amount, str(deadline)))
        self.conn.commit()

    def get_financial_summary(self):
        self.cursor.execute("SELECT SUM(value) FROM transactions WHERE type='receita'")
        receitas = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(value) FROM transactions WHERE type='despesa'")
        despesas = self.cursor.fetchone()[0] or 0.0
        total_global = receitas - despesas
        
        self.cursor.execute("SELECT SUM(current_amount) FROM goals")
        total_allocated = self.cursor.fetchone()[0] or 0.0
        
        return {
            "total_global": total_global, 
            "total_allocated": total_allocated, # Chave restaurada
            "free_balance": total_global - total_allocated, 
            "monthly_cost": self.get_monthly_cost()
        }