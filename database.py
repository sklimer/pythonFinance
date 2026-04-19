import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('zenmoney.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Создание таблиц"""
        # Таблица транзакций
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                account_id INTEGER DEFAULT 1
            )
        ''')
        
        # Таблица счетов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT '₽',
                icon TEXT DEFAULT '💰'
            )
        ''')
        
        # Таблица долгов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL, -- 'i_owe' (я должен) или 'owed_to_me' (мне должны)
                date TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        # Добавляем тестовые данные, если таблицы пусты
        self.cursor.execute("SELECT COUNT(*) FROM accounts")
        if self.cursor.fetchone()[0] == 0:
            sample_accounts = [
                ('Наличные', 15000, '₽', '💵'),
                ('Карта', 25000, '₽', '💳'),
                ('Сбережения', 100000, '₽', '🏦'),
            ]
            for acc in sample_accounts:
                self.cursor.execute('''
                    INSERT INTO accounts (name, balance, currency, icon)
                    VALUES (?, ?, ?, ?)
                ''', acc)
        
        self.cursor.execute("SELECT COUNT(*) FROM transactions")
        if self.cursor.fetchone()[0] == 0:
            sample_data = [
                (datetime.now().strftime('%Y-%m-%d'), 'income', 'Зарплата', 50000, 'Основная работа', 1),
                (datetime.now().strftime('%Y-%m-%d'), 'expense', 'Продукты', 3500, 'Супермаркет', 2),
                (datetime.now().strftime('%Y-%m-%d'), 'expense', 'Транспорт', 1200, 'Метро', 2),
                (datetime.now().strftime('%Y-%m-%d'), 'expense', 'Кафе', 850, 'Обед', 1),
            ]
            for data in sample_data:
                self.cursor.execute('''
                    INSERT INTO transactions (date, type, category, amount, description, account_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', data)
        
        self.cursor.execute("SELECT COUNT(*) FROM debts")
        if self.cursor.fetchone()[0] == 0:
            sample_debts = [
                ('Иван', 5000, 'owed_to_me', datetime.now().strftime('%Y-%m-%d'), 'Долг за билеты'),
                ('Магазин', 3000, 'i_owe', datetime.now().strftime('%Y-%m-%d'), 'Рассрочка'),
            ]
            for debt in sample_debts:
                self.cursor.execute('''
                    INSERT INTO debts (name, amount, type, date, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', debt)
        
        self.conn.commit()
    
    # Методы для транзакций
    def add_transaction(self, trans_type, category, amount, description, account_id=1):
        date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            INSERT INTO transactions (date, type, category, amount, description, account_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, trans_type, category, amount, description, account_id))
        self.conn.commit()
        
        # Обновляем баланс счета
        if trans_type == 'income':
            self.cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, account_id))
        else:
            self.cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (amount, account_id))
        self.conn.commit()
        
        return self.cursor.lastrowid
    
    def get_transactions_grouped_by_day(self):
        """Получение транзакций с группировкой по дням"""
        self.cursor.execute('''
            SELECT id, date, type, category, amount, description 
            FROM transactions 
            ORDER BY date DESC
        ''')
        transactions = self.cursor.fetchall()
        
        # Группируем по датам
        grouped = {}
        for trans in transactions:
            date = trans[1]
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(trans)
        
        return grouped
    
    # Методы для счетов
    def get_all_accounts(self):
        self.cursor.execute('SELECT * FROM accounts ORDER BY id')
        return self.cursor.fetchall()
    
    def add_account(self, name, balance, currency='₽', icon='💰'):
        self.cursor.execute('''
            INSERT INTO accounts (name, balance, currency, icon)
            VALUES (?, ?, ?, ?)
        ''', (name, balance, currency, icon))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def delete_account(self, account_id):
        self.cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # Методы для долгов
    def get_all_debts(self):
        self.cursor.execute('SELECT * FROM debts ORDER BY id')
        return self.cursor.fetchall()
    
    def add_debt(self, name, amount, debt_type, description):
        date = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute('''
            INSERT INTO debts (name, amount, type, date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, amount, debt_type, date, description))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def delete_debt(self, debt_id):
        self.cursor.execute('DELETE FROM debts WHERE id = ?', (debt_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_summary(self):
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="income"')
        total_income = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="expense"')
        total_expense = self.cursor.fetchone()[0] or 0
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense
        }
    
    def get_expenses_by_category(self):
        self.cursor.execute('''
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE type="expense" 
            GROUP BY category 
            ORDER BY total DESC
        ''')
        return self.cursor.fetchall()
    
    def delete_transaction(self, transaction_id):
        # Получаем информацию о транзакции для обновления баланса счета
        self.cursor.execute('SELECT type, amount, account_id FROM transactions WHERE id = ?', (transaction_id,))
        trans = self.cursor.fetchone()
        
        if trans:
            trans_type, amount, account_id = trans
            # Возвращаем баланс счета
            if trans_type == 'income':
                self.cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (amount, account_id))
            else:
                self.cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (amount, account_id))
        
        self.cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        self.conn.close()