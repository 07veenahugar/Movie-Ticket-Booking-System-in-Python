import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

# Connect to Database
def connect_db():
    return sqlite3.connect("movies.db")

# User Registration Window
def register_window():
    reg_win = tk.Toplevel()
    reg_win.title("User Registration")
    reg_win.geometry("400x300")

    tk.Label(reg_win, text="Username:").pack(pady=5)
    username_entry = tk.Entry(reg_win)
    username_entry.pack(pady=5)

    tk.Label(reg_win, text="Password:").pack(pady=5)
    password_entry = tk.Entry(reg_win, show="*")
    password_entry.pack(pady=5)

    def register():
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                           (username_entry.get(), password_entry.get()))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            reg_win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
        conn.close()

    tk.Button(reg_win, text="Register", command=register).pack(pady=10)

# User Login Window
def user_login_window():
    login_win = tk.Toplevel()
    login_win.title("User Login")
    login_win.geometry("400x300")

    tk.Label(login_win, text="Username:").pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)

    def check_login():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (username_entry.get(), password_entry.get()))
        user = cursor.fetchone()
        conn.close()
        if user:
            messagebox.showinfo("Login Successful", f"Welcome {username_entry.get()}!")
            login_win.destroy()
            movie_selection_window(user[0])
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    tk.Button(login_win, text="Login", command=check_login).pack(pady=10)

# Movie Selection Window
def movie_selection_window(user_id):
    movie_win = tk.Toplevel()
    movie_win.title("Select a Movie")
    movie_win.geometry("700x400")

    tk.Label(movie_win, text="Available Movies", font=("Arial", 14)).pack(pady=10)

    tree = ttk.Treeview(movie_win, columns=("ID", "Title", "Genre", "Seats"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Genre", text="Genre")
    tree.heading("Seats", text="Seats")
    tree.pack()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, genre, seats FROM movies")
    movies = cursor.fetchall()
    conn.close()

    for movie in movies:
        tree.insert("", tk.END, values=movie)

    def book_ticket():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a movie to book tickets!")
            return

        movie_id, movie_title, _, available_seats = tree.item(selected_item)["values"]

        if available_seats == 0:
            messagebox.showerror("Error", "No seats available for this movie!")
            return

        ticket_booking_window(user_id, movie_id, movie_title, available_seats)

    tk.Button(movie_win, text="Book Ticket", command=book_ticket).pack(pady=10)

# Ticket Booking Window
def ticket_booking_window(user_id, movie_id, movie_title, available_seats):
    booking_win = tk.Toplevel()
    booking_win.title("Book Ticket")
    booking_win.geometry("400x300")

    tk.Label(booking_win, text=f"Movie: {movie_title}", font=("Arial", 14)).pack(pady=10)
    tk.Label(booking_win, text=f"Available Seats: {available_seats}").pack(pady=5)

    tk.Label(booking_win, text="Number of Seats:").pack(pady=5)
    seat_entry = tk.Entry(booking_win)
    seat_entry.pack(pady=5)

    def proceed_payment():
        num_seats = int(seat_entry.get())

        if num_seats > available_seats or num_seats <= 0:
            messagebox.showerror("Error", "Invalid seat count!")
            return

        payment_window(user_id, movie_id, movie_title, num_seats)

    tk.Button(booking_win, text="Proceed to Payment", command=proceed_payment).pack(pady=10)

# Payment Window
def payment_window(user_id, movie_id, movie_title, num_seats):
    pay_win = tk.Toplevel()
    pay_win.title("Payment")
    pay_win.geometry("400x300")

    tk.Label(pay_win, text="Select Payment Method", font=("Arial", 14)).pack(pady=10)
    payment_var = tk.StringVar(value="Card")

    tk.Radiobutton(pay_win, text="Credit/Debit Card", variable=payment_var, value="Card").pack()
    tk.Radiobutton(pay_win, text="UPI/Net Banking", variable=payment_var, value="UPI").pack()
    tk.Radiobutton(pay_win, text="Wallet", variable=payment_var, value="Wallet").pack()

    def confirm_payment():
        conn = connect_db()
        cursor = conn.cursor()

        # Insert booking
        cursor.execute("INSERT INTO bookings (user_id, movie_id, seats_booked, payment_status) VALUES (?, ?, ?, ?)",
                       (user_id, movie_id, num_seats, "Paid"))

        # Update seat count
        cursor.execute("UPDATE movies SET seats = seats - ? WHERE id = ?", (num_seats, movie_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Booking Confirmed!")
        pay_win.destroy()
        generate_ticket(user_id, movie_title, num_seats)

    tk.Button(pay_win, text="Confirm Payment", command=confirm_payment).pack(pady=10)

# Generate E-Ticket
def generate_ticket(user_id, movie_title, num_seats):
    ticket_win = tk.Toplevel()
    ticket_win.title("E-Ticket")
    ticket_win.geometry("400x300")

    tk.Label(ticket_win, text="🎟️ Your E-Ticket 🎟️", font=("Arial", 16)).pack(pady=10)
    tk.Label(ticket_win, text=f"Movie: {movie_title}").pack()
    tk.Label(ticket_win, text=f"Seats: {num_seats}").pack()
    tk.Label(ticket_win, text="Payment: ✅ Paid").pack()

# Main Application
def main():
    root = tk.Tk()
    root.title("Movie Ticket Booking")
    root.geometry("500x400")

    tk.Label(root, text="Welcome to Movie Booking", font=("Arial", 16)).pack(pady=20)

    tk.Button(root, text="User Login", command=user_login_window).pack(pady=5)
    tk.Button(root, text="Register", command=register_window).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=10)

    root.mainloop()

main()
