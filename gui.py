import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("1000x650")
        self.root.configure(bg='#f0f0f0')
        
        self.db = Database()
        
        self.primary_color = '#4CAF50'
        self.secondary_color = '#2196F3'
        self.danger_color = '#f44336'
        
        self.setup_ui()
        self.refresh_expense_list()
    
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg=self.primary_color, height=70)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="💰 Personal Expense Tracker", 
                              font=('Arial', 22, 'bold'), 
                              bg=self.primary_color, fg='white')
        title_label.pack(pady=18)
        
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        left_panel = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', padx=(0, 10), ipadx=15, ipady=15)
        
        add_title = tk.Label(left_panel, text="Add New Expense", 
                            font=('Arial', 15, 'bold'), bg='white', fg='#333')
        add_title.pack(pady=(15, 25))
        
        tk.Label(left_panel, text="Amount (₹):", font=('Arial', 11), 
                bg='white', fg='#555').pack(anchor='w', padx=25, pady=(0, 5))
        self.amount_entry = tk.Entry(left_panel, font=('Arial', 13), width=22, bd=2, relief='solid')
        self.amount_entry.pack(padx=25, pady=(0, 20))
        
        tk.Label(left_panel, text="Category:", font=('Arial', 11), 
                bg='white', fg='#555').pack(anchor='w', padx=25, pady=(0, 5))
        self.category_var = tk.StringVar()
        categories = self.db.get_categories()
        self.category_combo = ttk.Combobox(left_panel, textvariable=self.category_var, 
                                          values=categories, font=('Arial', 12), 
                                          state='readonly', width=20)
        self.category_combo.set(categories[0])
        self.category_combo.pack(padx=25, pady=(0, 20))
        
        tk.Label(left_panel, text="Description:", font=('Arial', 11), 
                bg='white', fg='#555').pack(anchor='w', padx=25, pady=(0, 5))
        self.description_entry = tk.Entry(left_panel, font=('Arial', 13), width=22, bd=2, relief='solid')
        self.description_entry.pack(padx=25, pady=(0, 25))
        
        add_btn = tk.Button(left_panel, text="Add Expense", 
                           font=('Arial', 12, 'bold'), 
                           bg=self.primary_color, fg='white',
                           cursor='hand2', relief='flat',
                           command=self.add_expense, padx=20, pady=10)
        add_btn.pack(pady=10)
        
        summary_btn = tk.Button(left_panel, text="View Summary", 
                               font=('Arial', 11), 
                               bg=self.secondary_color, fg='white',
                               cursor='hand2', relief='flat',
                               command=self.show_summary, padx=20, pady=8)
        summary_btn.pack(pady=(15, 10))
        
        right_panel = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)
        
        list_title = tk.Label(right_panel, text="Recent Expenses", 
                             font=('Arial', 15, 'bold'), bg='white', fg='#333')
        list_title.pack(pady=(15, 10))
        
        tree_frame = tk.Frame(right_panel, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.expense_tree = ttk.Treeview(tree_frame, 
                                        columns=('ID', 'Amount', 'Category', 'Description', 'Date'),
                                        show='headings', 
                                        yscrollcommand=scrollbar.set,
                                        height=20)
        
        self.expense_tree.heading('ID', text='ID')
        self.expense_tree.heading('Amount', text='Amount (₹)')
        self.expense_tree.heading('Category', text='Category')
        self.expense_tree.heading('Description', text='Description')
        self.expense_tree.heading('Date', text='Date')
        
        self.expense_tree.column('ID', width=50, anchor='center')
        self.expense_tree.column('Amount', width=100, anchor='e')
        self.expense_tree.column('Category', width=120, anchor='center')
        self.expense_tree.column('Description', width=200)
        self.expense_tree.column('Date', width=150, anchor='center')
        
        scrollbar.config(command=self.expense_tree.yview)
        self.expense_tree.pack(side='left', fill='both', expand=True)
        
        delete_btn = tk.Button(right_panel, text="Delete Selected", 
                              font=('Arial', 11), 
                              bg=self.danger_color, fg='white',
                              cursor='hand2', relief='flat',
                              command=self.delete_expense, padx=20, pady=8)
        delete_btn.pack(pady=(0, 15))
    
    def add_expense(self):
        amount = self.amount_entry.get().strip()
        category = self.category_var.get()
        description = self.description_entry.get().strip()
        
        if not amount:
            messagebox.showwarning("Input Error", "Please enter an amount")
            return
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive number")
            return
        
        self.db.add_expense(amount, category, description)
        
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        
        self.refresh_expense_list()
        messagebox.showinfo("Success", f"Expense added: ₹{amount:.2f}")
    
    def refresh_expense_list(self):
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        expenses = self.db.get_all_expenses()
        for exp in expenses:
            self.expense_tree.insert('', 'end', values=(
                exp[0],
                f"₹{exp[1]:.2f}",
                exp[2],
                exp[3] if exp[3] else '-',
                exp[4]
            ))
    
    def delete_expense(self):
        selected = self.expense_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an expense to delete")
            return
        
        item = self.expense_tree.item(selected[0])
        expense_id = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            if self.db.delete_expense(expense_id):
                self.refresh_expense_list()
                messagebox.showinfo("Success", "Expense deleted")
    
    def show_summary(self):
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Expense Summary")
        summary_window.geometry("600x500")
        summary_window.configure(bg='white')
        
        title = tk.Label(summary_window, text="Expense Summary", 
                        font=('Arial', 18, 'bold'), bg='white', fg='#333')
        title.pack(pady=20)
        
        period_frame = tk.Frame(summary_window, bg='white')
        period_frame.pack(pady=10)
        
        tk.Label(period_frame, text="Select Period:", 
                font=('Arial', 11), bg='white').pack(side='left', padx=10)
        
        period_var = tk.StringVar(value='month')
        periods = [('Week', 'week'), ('Month', 'month'), ('Year', 'year'), ('All Time', 'all')]
        
        for text, value in periods:
            rb = tk.Radiobutton(period_frame, text=text, variable=period_var, 
                               value=value, font=('Arial', 10), bg='white',
                               command=lambda: self.update_summary(summary_text, period_var.get()))
            rb.pack(side='left', padx=5)
        
        text_frame = tk.Frame(summary_window, bg='white')
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        summary_text = tk.Text(text_frame, font=('Courier', 11), 
                              yscrollcommand=scrollbar.set, 
                              relief='solid', bd=1, padx=10, pady=10)
        summary_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=summary_text.yview)
        
        self.update_summary(summary_text, 'month')
    
    def update_summary(self, text_widget, period):
        text_widget.config(state='normal')
        text_widget.delete('1.0', tk.END)
        
        results = self.db.get_expenses_by_period(period)
        
        if not results:
            text_widget.insert('1.0', f"No expenses found for this period.")
            text_widget.config(state='disabled')
            return
        
        total = sum(row[1] for row in results)
        
        period_names = {'week': 'This Week', 'month': 'This Month', 
                       'year': 'This Year', 'all': 'All Time'}
        
        text_widget.insert('end', f"=== {period_names.get(period, 'Period')} ===\n\n")
        text_widget.insert('end', f"{'Category':<20} {'Amount':<15} {'Count':<10} {'%':<10}\n")
        text_widget.insert('end', "-" * 55 + "\n")
        
        for row in results:
            percentage = (row[1] / total) * 100
            text_widget.insert('end', f"{row[0]:<20} ₹{row[1]:<14.2f} {row[2]:<10} {percentage:<9.1f}%\n")
        
        text_widget.insert('end', "-" * 55 + "\n")
        text_widget.insert('end', f"{'TOTAL':<20} ₹{total:<14.2f}\n")
        
        text_widget.config(state='disabled')
    
    def on_closing(self):
        self.db.close()
        self.root.destroy()
