import tkinter as tk
from gui import ExpenseTrackerGUI

def main():
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()