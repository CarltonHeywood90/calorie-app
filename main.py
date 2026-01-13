import tkinter as tk
from gui.screens.login_screen import LoginScreen

user_id = 1

root = tk.Tk()
root.title("User Login")
root.geometry("400x400")

screen = LoginScreen(root, on_login_success=lambda user: print(f"Logged in user: {user}"))

root.mainloop()
