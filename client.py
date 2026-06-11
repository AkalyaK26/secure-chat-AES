import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from utils.crypto import derive_key, encrypt_message, decrypt_message

class SecureChatClient:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 65432
        self.client_socket = None
        self.username = ""
        self.aes_key = b""
        
        # --- LOGIN GUI ---
        self.login_window = tk.Tk()
        self.login_window.title("Secure Login")
        self.login_window.geometry("350x230")
        self.login_window.resizable(False, False)
        
        tk.Label(self.login_window, text="AES Encrypted Chat", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(self.login_window, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_window, width=28)
        self.username_entry.pack(pady=2)
        
        tk.Label(self.login_window, text="Secret AES Key:").pack()
        self.key_entry = tk.Entry(self.login_window, show="*", width=28)
        self.key_entry.pack(pady=2)
        
        tk.Button(self.login_window, text="Login & Connect", command=self.attempt_login, bg="#4CAF50", fg="white").pack(pady=15)
        self.login_window.mainloop()

    def attempt_login(self):
        self.username = self.username_entry.get().strip()
        secret_input = self.key_entry.get().strip()
        
        if not self.username or not secret_input:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        self.aes_key = derive_key(secret_input)
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.login_window.destroy()
            self.build_chat_gui()
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Cannot connect to server:\n{e}")

    def build_chat_gui(self):
        self.chat_window = tk.Tk()
        self.chat_window.title(f"Chat - Logged in as: {self.username}")
        self.chat_window.geometry("450x550")
        self.chat_window.minsize(380, 450) # Strict screen scale shield

        # --- USING ABSOLUTE PLACE MANAGER (Kali manager cannot collapse this) ---
        
        # 1. UPPER CHAT AREA: Spans from top (0%) down to 80% of window height
        self.chat_area = scrolledtext.ScrolledText(self.chat_window, state='disabled', wrap='word')
        self.chat_area.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.78)
        
        # 2. FIXED TYPING BOX: Placed explicitly at 83% height, spanning 75% width
        # Height parameter logic bound with system text structure
        self.msg_entry = tk.Text(self.chat_window, font=("Arial", 11), bg="#ffffff", fg="#000000", bd=1, relief=tk.SOLID)
        self.msg_entry.place(relx=0.02, rely=0.83, relwidth=0.75, relheight=0.12)
        self.msg_entry.bind("<Return>", lambda event: self.send_message())
        self.msg_entry.focus_set()
        
        # 3. SEND BUTTON: Placed explicitly right next to typing box at 83% height
        send_btn = tk.Button(self.chat_window, text="Send", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=self.send_message)
        send_btn.place(relx=0.79, rely=0.83, relwidth=0.19, relheight=0.12)
        
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.chat_window.mainloop()

    def display(self, text):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, text + "\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def send_message(self):
        raw_text = self.msg_entry.get("1.0", tk.END).strip()
        if not raw_text:
            return
        
        self.msg_entry.delete("1.0", tk.END)
        self.display(f"[You]: {raw_text}")
        
        full_payload = f"{self.username}: {raw_text}"
        encrypted_bytes = encrypt_message(full_payload, self.aes_key)
        
        try:
            self.client_socket.send(encrypted_bytes)
        except Exception:
            self.display("[SYSTEM ERROR] Failed to deliver message.")

    def receive_messages(self):
        while True:
            try:
                encrypted_payload = self.client_socket.recv(4096)
                if not encrypted_payload:
                    break
                decrypted_msg = decrypt_message(encrypted_payload, self.aes_key)
                self.display(decrypted_msg)
            except Exception:
                self.display("[SYSTEM] Connection lost.")
                break

if __name__ == "__main__":
    SecureChatClient()
