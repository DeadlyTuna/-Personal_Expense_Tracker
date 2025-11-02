import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='expenses.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()
    
    def init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category_id INTEGER,
                description TEXT,
                date TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        default_categories = ['Food', 'Transportation', 'Entertainment', 
                            'Utilities', 'Healthcare', 'Shopping', 'Rent', 
                            'Education', 'Other']
        for cat in default_categories:
            try:
                self.cursor.execute('INSERT INTO categories (name) VALUES (?)', (cat,))
            except sqlite3.IntegrityError:
                pass
        
        self.conn.commit()
    
    def add_expense(self, amount, category, description=''):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        result = self.cursor.fetchone()
        
        if result:
            category_id = result[0]
        else:
            self.cursor.execute('INSERT INTO categories (name) VALUES (?)', (category,))
            category_id = self.cursor.lastrowid
        
        self.cursor.execute('''
            INSERT INTO expenses (amount, category_id, description, date)
            VALUES (?, ?, ?, ?)
        ''', (amount, category_id, description, date))
        
        self.conn.commit()
        return True
    
    def get_all_expenses(self):
        self.cursor.execute('''
            SELECT e.id, e.amount, c.name, e.description, e.date
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            ORDER BY e.date DESC
        ''')
        return self.cursor.fetchall()
    
    def get_expenses_by_period(self, period='month'):
        if period == 'month':
            date_filter = "date >= date('now', 'start of month')"
        elif period == 'week':
            date_filter = "date >= date('now', 'start of day', '-7 days')"
        elif period == 'year':
            date_filter = "date >= date('now', 'start of year')"
        else:
            date_filter = "1=1"
        
        self.cursor.execute(f'''
            SELECT c.name, SUM(e.amount), COUNT(e.id)
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE {date_filter}
            GROUP BY c.name
            ORDER BY SUM(e.amount) DESC
        ''')
        return self.cursor.fetchall()
    
    def delete_expense(self, expense_id):
        self.cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_categories(self):
        self.cursor.execute('SELECT name FROM categories ORDER BY name')
        return [row[0] for row in self.cursor.fetchall()]
    
    def close(self):
        self.conn.close()