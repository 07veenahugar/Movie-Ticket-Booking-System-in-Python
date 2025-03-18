import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk

# Connect to Database
def connect_db():
    return sqlite3.connect("movies.db")

# Admin Login Window
def admin_login_window():
    login_win = tk.Toplevel()
    login_win.title("Admin Login")
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
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", 
                       (username_entry.get(), password_entry.get()))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            messagebox.showinfo("Login Successful", "Welcome Admin!")
            login_win.destroy()
            admin_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    tk.Button(login_win, text="Login", command=check_login).pack(pady=10)
    login_win.mainloop()

# Admin Dashboard Window
def admin_dashboard():
    admin_win = tk.Toplevel()
    admin_win.title("Admin Dashboard")
    admin_win.geometry("600x400")

    tk.Label(admin_win, text="Admin Panel", font=("Arial", 16)).pack(pady=10)

    tk.Button(admin_win, text="Add Movie", command=add_movie_window).pack(pady=5)
    tk.Button(admin_win, text="Edit/Remove Movie", command=manage_movies_window).pack(pady=5)

# Add Movie Window
def add_movie_window():
    add_win = tk.Toplevel()
    add_win.title("Add Movie")
    add_win.geometry("400x500")

    tk.Label(add_win, text="Title:").pack(pady=5)
    title_entry = tk.Entry(add_win)
    title_entry.pack(pady=5)

    tk.Label(add_win, text="Cast:").pack(pady=5)
    cast_entry = tk.Entry(add_win)
    cast_entry.pack(pady=5)

    tk.Label(add_win, text="Genre:").pack(pady=5)
    genre_entry = tk.Entry(add_win)
    genre_entry.pack(pady=5)

    tk.Label(add_win, text="Duration:").pack(pady=5)
    duration_entry = tk.Entry(add_win)
    duration_entry.pack(pady=5)

    tk.Label(add_win, text="Seats Available:").pack(pady=5)
    seats_entry = tk.Entry(add_win)
    seats_entry.pack(pady=5)

    tk.Label(add_win, text="Poster:").pack(pady=5)
    poster_path = tk.StringVar()

    def select_poster():
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        poster_path.set(file_path)

    tk.Button(add_win, text="Choose Poster", command=select_poster).pack(pady=5)

    def save_movie():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title, cast, genre, duration, poster, seats) VALUES (?, ?, ?, ?, ?, ?)",
                       (title_entry.get(), cast_entry.get(), genre_entry.get(), duration_entry.get(),
                        poster_path.get(), seats_entry.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Movie Added Successfully!")
        add_win.destroy()

    tk.Button(add_win, text="Add Movie", command=save_movie).pack(pady=10)

# Manage Movies (Edit/Remove)
def manage_movies_window():
    manage_win = tk.Toplevel()
    manage_win.title("Manage Movies")
    manage_win.geometry("600x400")

    tk.Label(manage_win, text="Movies List", font=("Arial", 14)).pack(pady=10)

    tree = ttk.Treeview(manage_win, columns=("ID", "Title", "Seats"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Seats", text="Seats")
    tree.pack()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, seats FROM movies")
    movies = cursor.fetchall()
    conn.close()

    for movie in movies:
        tree.insert("", tk.END, values=movie)

    def delete_movie():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a movie to delete!")
            return

        movie_id = tree.item(selected_item)["values"][0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id=?", (movie_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "Movie removed successfully!")
        tree.delete(selected_item)

    def edit_movie():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a movie to edit!")
            return

        movie_id, movie_title, movie_seats = tree.item(selected_item)["values"]

        edit_win = tk.Toplevel()
        edit_win.title("Edit Movie")
        edit_win.geometry("400x300")

        tk.Label(edit_win, text="Title:").pack(pady=5)
        title_entry = tk.Entry(edit_win)
        title_entry.insert(0, movie_title)
        title_entry.pack(pady=5)

        tk.Label(edit_win, text="Seats Available:").pack(pady=5)
        seats_entry = tk.Entry(edit_win)
        seats_entry.insert(0, movie_seats)
        seats_entry.pack(pady=5)

        def save_changes():
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE movies SET title=?, seats=? WHERE id=?",
                           (title_entry.get(), seats_entry.get(), movie_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Updated", "Movie updated successfully!")
            edit_win.destroy()
            manage_win.destroy()
            manage_movies_window()

        tk.Button(edit_win, text="Save Changes", command=save_changes).pack(pady=10)

    tk.Button(manage_win, text="Edit Movie", command=edit_movie).pack(pady=5)
    tk.Button(manage_win, text="Delete Movie", command=delete_movie).pack(pady=5)

# Main Application
def main():
    root = tk.Tk()
    root.title("Movie Ticket Booking System")
    root.geometry("500x400")

    tk.Label(root, text="Welcome to Movie Booking", font=("Arial", 16)).pack(pady=20)

    tk.Button(root, text="Admin Login", command=admin_login_window).pack(pady=10)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=10)

    root.mainloop()

main()
