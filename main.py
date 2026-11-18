import shutil
import os
import json

import tkinter as tk
from tkinter import messagebox, Entry
import sqlite3
import hashlib


from PIL import Image, ImageTk
from tkinter import filedialog
from datetime import datetime, timedelta
from tkinter import ttk






class MuscleLabApp:

    def __init__(self):

        self.p_image = None
        self.main = None
        self.sidebar = None
        self.p_desc = None
        self.ep_desc = None
        self.root = tk.Tk()
        self.root.title("Muscle Lab")
        self.root.geometry("1000x700")
        self.root.configure(bg="#eef2f7")

        self.conn = sqlite3.connect("muscle_lab.db")
        self.cursor = self.conn.cursor()


        self.create_tables()
        self.seed_products()

        self.current_user = None
        self.cart = {}


        self.email = None
        self.password = None
        self.reg_entries = {}

        self.p_name = None
        self.p_price = None
        self.p_stock = None


        self.ep_name = None
        self.ep_price = None
        self.ep_stock = None
        if os.path.exists("session.json"):
            with open("session.json", "r") as f:
                self.current_user = json.load(f)
            self.home()
        else:

            self.show_login()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT,
            full_name TEXT,
            contact TEXT,
            address TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            stock INTEGER,
            description TEXT,
            image TEXT
        )
        """)

        self.cursor.execute("""
       CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            total REAL,
            items TEXT,
            placed_time TEXT,
            shipped_time TEXT,
            delivery_time TEXT,
            received_time TEXT,
            eta_time TEXT,
            status TEXT,
            notified INTEGER DEFAULT 0
            )
        """)

        self.cursor.execute("""
       CREATE TABLE IF NOT EXISTS feedback(
           id INTEGER PRIMARY KEY,
           user_id INTEGER,
           order_id INTEGER,
           message TEXT,
           date TEXT          
       )
       """)

        self.conn.commit()



    def seed_products(self):
        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            data = [
                (
                    "Whey Protein",
                    2500,
                    20,
                    "Whey Protein is a fast-absorbing protein supplement that supports muscle growth, recovery, and repair after workouts." 
                    "It provides your body with essential amino acids needed to rebuild muscle tissues, making it perfect for post-workout nutrition." 
                    "Whether you’re building muscle or maintaining a lean physique, whey protein helps you reach your fitness goals efficiently."
                    ,"product_images/whey.png"

                ),
                (
                    "Creatine Monohydrate",
                    1200,
                    30,
                    "Creatine Monohydrate is a powerful and well-researched supplement that helps increase strength, power, and muscle performance" 
                    "during high-intensity workouts. It boosts your body’s ability to produce energy quickly,"
                    " allowing you to lift heavier, train harder, and improve overall muscle gains over time."
                    "Ideal for anyone looking to build size and improve workout performance."
                    ,"product_images/creatine.png"
                ),
                (
                    "Pre Workout",
                    1800,
                    15,
                    "Pre-Workout is a performance-boosting supplement designed to increase energy, focus, and endurance before training sessions. "
                    "It helps reduce fatigue and enhances workout intensity, allowing you to push harder and stay motivated throughout your exercise."
                    " Perfect for intense gym sessions and improving overall performance."
                    ,"product_images/preworkout.png"
                ),
                (
                    "BCAA",
                    1500,
                    25,
                    "BCAA is a muscle-support supplement that helps reduce muscle breakdown, improve recovery, and decrease fatigue during and after workouts."
                    " It provides essential amino acids that your body cannot produce on its own, helping you recover faster and maintain lean muscle mass."
                    " Ideal for endurance training, cutting phases, and intense workouts."
                    ,"product_images/bcaa.png"
                )
            ]

            self.cursor.executemany(
                "INSERT INTO products VALUES (NULL,?,?,?,?,?)", data)
            self.conn.commit()

    def update_status(self, order_id, status):

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if status == "Shipped":


            win = tk.Toplevel(self.root)
            win.title("Set Delivery Time")

            tk.Label(win, text="Enter delivery duration hours/mins/sec:").pack(pady=5)

            eta_entry = tk.Entry(win)
            eta_entry.pack(pady=5)

            def confirm_eta():
                try:
                    hours = int(eta_entry.get())
                    eta_time = datetime.now() + timedelta(hours=hours)

                    self.cursor.execute(""" UPDATE orders SET status=?,shipped_time=?,eta_time=? WHERE id = ?
                                        """,("Shipped", current_time,eta_time.strftime("%Y-%m-%d %H:%M:%S"),order_id ))
                    self.conn.commit()
                    win.destroy()
                    messagebox.showinfo("Updated", "Order shipped with ETA")
                    self.manage_orders()

                except:
                    messagebox.showerror("Error", "Enter valid number")

            tk.Button(win, text="Confirm", command=confirm_eta).pack(pady=10)

        elif status == "Delivered":
            self.cursor.execute(""" UPDATE orders SET status=?, delivery_time=? WHERE id = ?
                                """,(status, current_time, order_id))

            self.conn.commit()
            messagebox.showinfo("Updated", "Order delivered")
            self.manage_orders()

    @staticmethod
    def get_eta_remaining(eta_time):
        try:
            eta = datetime.strptime(eta_time, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()

            if eta <= now:
                return "Arrived"

            remaining = eta - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            return f"{remaining.days}d {hours}h {minutes}m"

        except:
            return "N/A"


    @staticmethod
    def hash_password(p):
        return hashlib.sha256(p.encode()).hexdigest()


    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def header(self, text):
        tk.Label(self.root, text=text, font=("Arial", 20, "bold"),
                 bg="#1e3a8a", fg="white").pack(fill="x")

    def layout(self):
        self.clear()

        # Sidebar
        self.sidebar = tk.Frame(self.root, bg="#1e293b", width=200)
        self.sidebar.pack(side="left", fill="y")

        # Main content
        self.main = tk.Frame(self.root, bg="#f1f5f9")
        self.main.pack(side="right", expand=True, fill="both")

    def sidebar_menu(self):
        tk.Label(self.sidebar, text="Muscle Lab", bg="#1e293b",
                 fg="white", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Button(self.sidebar, text="🏠 Home", width=20, command=self.home).pack(pady=5)
        tk.Button(self.sidebar, text="📖 About Us", width=20, command=self.about_us).pack(pady=5)
        tk.Button(self.sidebar, text="🛒 Shop", width=20, command=self.shop).pack(pady=5)
        tk.Button(self.sidebar, text="🛍 Cart", width=20, command=self.view_cart).pack(pady=5)
        tk.Button(self.sidebar, text="📦 My Orders", width=20, command=self.view_orders).pack(pady=5)

        if self.current_user["role"] == "admin":
            tk.Button(self.sidebar, text="⚙️ Admin Panel", width=20, command=self.admin_panel).pack(pady=5)

        tk.Button(self.sidebar, text="⚙️ Settings", width=20, command=self.settings).pack(pady=5)
        tk.Button(self.sidebar, text="🚪 Logout", width=20, command=self.logout).pack(pady=20)

    def show_login(self):
        self.clear()
        self.header(" MuscleventLab Login")

        tk.Label(self.root, text="Email Address", font=("Arial", 12, "bold"),
                 bg="#eef2f7").pack(pady=(20, 5))

        tk.Label(self.root, text="Enter your registered email (e.g. user@gmail.com)",
                 font=("Arial", 9), fg="gray", bg="#eef2f7").pack()

        self.email = tk.Entry(self.root, width=40)
        self.email.insert(0, "example@email.com")
        self.email.pack(pady=10)

        def clear_placeholder():
            if self.email.get() == "example@email.com":
                self.email.delete(0, tk.END)

        def add_placeholder():
            if self.email.get() == "":
                self.email.insert(0, "example@email.com")

        self.email.bind("<FocusIn>", lambda event: clear_placeholder())
        self.email.bind("<FocusOut>", lambda event: add_placeholder())


        tk.Label(self.root, text="Password", font=("Arial", 12, "bold"),
                 bg="#eef2f7").pack(pady=(10, 5))

        tk.Label(self.root, text="Enter your password",
                 font=("Arial", 9), fg="gray", bg="#eef2f7").pack()

        self.password = tk.Entry(self.root, show="*", width=40)
        self.password.pack(pady=10)

        # Buttons
        tk.Button(self.root, text="Login", width=20, command=self.login).pack(pady=10)
        tk.Button(self.root, text="Register", command=self.show_register).pack()

    def show_register(self):
        self.clear()
        self.header("Register")

        self.reg_entries = {}
        fields = ["username", "email", "password", "full_name", "contact", "address"]

        for f in fields:
            tk.Label(self.root, text=f).pack()
            event: Entry = tk.Entry(self.root)
            event.pack()
            self.reg_entries[f] = event

        tk.Button(self.root, text="Create", command=self.register).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_login).pack()

    def register(self):
        data = {k: v.get() for k, v in self.reg_entries.items()}

        if "" in data.values():
            messagebox.showerror("Error", "Fill all fields")
            return

        role = "admin" if self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0 else "customer"

        try:
            self.cursor.execute("""
            INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)
            """, (
                data["username"],
                data["email"],
                self.hash_password(data["password"]),
                role,
                data["full_name"],
                data["contact"],
                data["address"]
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "Account created")
            self.show_login()


        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username or Email exists")

    def login(self):
        email = self.email.get()
        pw = self.hash_password(self.password.get())

        self.cursor.execute("SELECT id,username,role FROM users WHERE email=? AND password=?", (email, pw))
        user = self.cursor.fetchone()

        if user:
            self.current_user = {"id": user[0], "name": user[1], "role": user[2]}

            #SAVE SESSION
            with open("session.json", "w") as f:
                json.dump(self.current_user, f)

            self.home()
        else:
            messagebox.showerror("Error", "Invalid login")

    def settings(self):
        self.layout()
        self.sidebar_menu()

        tk.Label(self.main, text="Settings",
                 font=("Arial", 18, "bold"),
                 bg="#f1f5f9").pack(pady=10)

        tk.Button(self.main, text="Change Password", width=25,
                  command=self.change_password).pack(pady=10)

        tk.Button(self.main, text="Clear Session (Logout Everywhere)", width=25,
                  command=self.clear_session).pack(pady=10)

    def change_password(self):
        win = tk.Toplevel(self.root)
        win.title("Change Password")

        tk.Label(win, text="New Password").pack(pady=5)
        new_pw = tk.Entry(win, show="*")
        new_pw.pack(pady=5)

        def update_pw():
            pw = new_pw.get()
            if not pw:
                messagebox.showerror("Error", "Password cannot be empty")
                return

            hashed = self.hash_password(pw)

            self.cursor.execute(
                "UPDATE users SET password=? WHERE id=?",
                (hashed, self.current_user["id"])
            )
            self.conn.commit()

            messagebox.showinfo("Success", "Password updated")
            win.destroy()

        tk.Button(win, text="Save", command=update_pw).pack(pady=10)

    def clear_session(self):
        if os.path.exists("session.json"):
            os.remove("session.json")

        messagebox.showinfo("Session Cleared", "You will be logged out")
        self.logout()

    def logout(self):
        self.current_user = None
        self.cart.clear()
        if os.path.exists("session.json"):
            os.remove("session.json")
        self.show_login()

    def home(self):
        if not self.current_user:
            self.show_login()
            return

        self.layout()
        self.sidebar_menu()

        tk.Label(self.main,
                 text=f"Welcome, {self.current_user['name']}!",
                 font=("Arial", 20, "bold"),
                 bg="#f1f5f9").pack(pady=20)

        tk.Label(self.main,
                 text="Your fitness journey starts here 💪",
                 bg="#f1f5f9").pack(pady=10)


    def about_us(self):
        self.layout()
        self.sidebar_menu()

        tk.Label(self.main, text="About Muscle Lab",
                 font=("Arial", 18, "bold"),
                 bg="#f1f5f9").pack(pady=10)

        tk.Label(
            self.main,
            text="Muscle Lab is an online shop that offers premium gym supplements designed to support "
                 "muscle growth, strength, and overall fitness performance, helping athletes and fitness "
                 "enthusiasts reach their goals faster with high-quality products and trusted nutrition.\n\n"
                 "visit us at Cagayan de Oro, Julio Pacana St; for inquiries or orders,\n"
                 "you may contact 0934556728",

            wraplength=600,
            justify="left",
            bg="#f1f5f9"
        ).pack(pady=10)



    def shop(self):
        self.layout()
        self.sidebar_menu()

        tk.Label(self.main, text="Products",
                 font=("Arial", 18, "bold"),
                 bg="#f1f5f9").pack(pady=10)

        self.cursor.execute("SELECT * FROM products")

        for p in self.cursor.fetchall():
            card = tk.Frame(self.main, bg="white", bd=1, relief="solid")
            card.pack(padx=20, pady=10, fill="x")

            # Load image
            try:
                img = Image.open(p[5])  # image path
                img = img.resize((100, 100))
                photo = ImageTk.PhotoImage(img)

                img_label = tk.Label(card, image=photo, bg="white")
                img_label.image = photo  # prevent garbage collection
                img_label.pack(side="left", padx=10, pady=10)
            except:
                pass

            info_frame = tk.Frame(card, bg="white")
            info_frame.pack(side="left", fill="both", expand=True)
            tk.Label(info_frame, text=p[1],font=("Arial", 14, "bold"),bg="white").pack(anchor="w")
            tk.Label(info_frame, text=f"₱{p[2]} | Stock: {p[3]}",bg="white").pack(anchor="w")
            tk.Label(info_frame, text=p[4],wraplength=500, justify="left",fg="gray",bg="white").pack(anchor="w")
            tk.Button(info_frame, text="Add to Cart",bg="#2563eb", fg="white",command=lambda x=p: self.add_cart(x)).pack(pady=5)

    def browse_image(self):
        file = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if file:
            self.p_image.delete(0, tk.END)
            self.p_image.insert(0, file)


    def add_cart(self, p):
        pid = p[0]

        if p[3] <= 0:
            messagebox.showwarning("No stock", "Out of stock")
            return

        if pid in self.cart:
            self.cart[pid]["qty"] += 1
        else:
            self.cart[pid] = {
                "name": p[1],
                "price": p[2],
                "qty": 1
            }

        messagebox.showinfo("Added", f"{p[1]} added to cart")



    def view_cart(self):
        self.layout()
        self.sidebar_menu()

        tk.Label(self.main, text="Your Cart",
                 font=("Arial", 18, "bold"),
                 bg="#f1f5f9").pack(pady=10)

        total = 0

        if not self.cart:
            tk.Label(self.main, text="Cart is empty",
                     bg="#f1f5f9").pack(pady=20)
            return

        for pid, item in self.cart.items():
            frame = tk.Frame(self.main, bg="white", bd=1)
            frame.pack(fill="x", padx=20, pady=5)

            subtotal = item["price"] * item["qty"]

            tk.Label(frame,
                     text=f"{item['name']} | ₱{item['price']} x {item['qty']} = ₱{subtotal}",
                     bg="white").pack(side="left", padx=10)

            tk.Button(frame, text="+", command=lambda x=pid: self.increase_qty(x)).pack(side="right")
            tk.Button(frame, text="-", command=lambda x=pid: self.decrease_qty(x)).pack(side="right")

            total += subtotal

        tk.Label(self.main, text=f"Total: ₱{total}",
                 font=("Arial", 14, "bold"),
                 bg="#f1f5f9").pack(pady=10)

        tk.Button(self.main, text="Checkout",
                  bg="green", fg="white",
                  command=self.checkout).pack(pady=10)



    def view_orders(self):

        self.clear()
        self.header("My Orders")

        self.cursor.execute(
            "SELECT id, total, items, placed_time, shipped_time, delivery_time, received_time, status, eta_time, notified "
                "FROM orders WHERE user_id=? ORDER BY placed_time DESC",
            (self.current_user["id"],)
        )

        orders = self.cursor.fetchall()

        if not orders:

            empty_frame = tk.Frame(self.root)
            empty_frame.pack(fill="both", expand=True, pady=50)

            (tk.Label(empty_frame,text="📦 No Orders Yet",font=("Arial", 18, "bold"),fg="gray")
             .pack(pady=10))
            (tk.Label( empty_frame,text="Looks like you haven't placed any orders.\nStart shopping now!",fg="gray")
             .pack(pady=5))
            (tk.Button( empty_frame, text="🛒 Go to Shop", bg="#2563eb", fg="white", command=self.shop)
             .pack(pady=15))
            tk.Button(self.root, text="Back", command=self.home).pack(pady=10)

            return
        for order in orders:

            f = tk.Frame(self.root, bd=2, relief="solid")
            f.pack(fill="x", padx=20, pady=5)

            tk.Label(
                f,
                text=f"Order #{order[0]}\nItems: {order[2]}\nTotal: ₱{order[1]}\nPlaced: {order[3]}\nStatus: {order[7]}",
                justify="left"
            ).pack(anchor="w", padx=10, pady=5)


            # DURATIONS
            if order[3] and order[5]:
                d = self.calculate_duration(order[3], order[5])
                tk.Label(f, text=f" Delivery Time: {d}", fg="blue").pack(anchor="w")

            if order[3] and order[6]:
                t = self.calculate_duration(order[3], order[6])
                tk.Label(f, text=f"⏱ Total Time: {t}", fg="green").pack(anchor="w")

            # ETA (NEW )
            if order[7] == "Shipped" and order[8]:
                eta_remaining = self.get_eta_remaining(order[8])
                tk.Label(f, text=f" ETA: {eta_remaining}", fg="orange").pack(anchor="w")

                tk.Label(f, text=f"Expected at: {order[8]}", fg="gray").pack(anchor="w")

            # NOTIFICATION
            if order[7] == "Shipped" and order[9] == 0:
                messagebox.showinfo("Order Update", f"Order #{order[0]} is on the way!")
                self.cursor.execute("UPDATE orders SET notified=1 WHERE id=?",(order[0],))
                self.conn.commit()

            elif order[7] == "Delivered" and order[9] == 0:
                messagebox.showinfo("Order Update", f"Order #{order[0]} delivered!")
                self.cursor.execute("UPDATE orders SET notified=1 WHERE id=?",(order[0],))
                self.conn.commit()

            # STATUS MESSAGE
            if order[7] == "Shipped":
                tk.Label(f, text="🔔 Order shipped!", fg="orange").pack()

            elif order[7] == "Delivered":
                tk.Label(f, text="Delivered! Please confirm receipt.", fg="green").pack()

            # TIMELINE
            if order[3]:
                tk.Label(f, text=f"Placed: {order[3]}").pack(anchor="w")

            if order[4]:
                tk.Label(f, text=f"Shipped: {order[4]}").pack(anchor="w")

            if order[5]:
                tk.Label(f, text=f"Delivered: {order[5]}").pack(anchor="w")

            if order[6]:
                tk.Label(f, text=f"Received: {order[6]}").pack(anchor="w")

            # PROGRESS BAR 🔥
            progress_value = 0

            if order[7] == "Placed":
                progress_value = 25
            elif order[7] == "Shipped":
                progress_value = 50
            elif order[7] == "Delivered":
                progress_value = 75
            elif order[7] == "Received":
                progress_value = 100

            progress = ttk.Progressbar(f, length=300, mode='determinate')
            progress['value'] = progress_value
            progress.pack(pady=5)

            tk.Label(f, text=f"{progress_value}% Complete").pack(anchor="w")

            # CONFIRM BUTTON
            if order[7] == "Delivered":
                tk.Button(
                    f,
                    text="Confirm Received",
                    bg="green",
                    fg="white",
                    command=lambda oid=order[0]: self.confirm_received(oid)
                ).pack()
        tk.Button(self.root, text="Back", command=self.home).pack(pady=10)


    def increase_qty(self, pid):
        self.cursor.execute("SELECT stock FROM products WHERE id=?", (pid,))
        stock = self.cursor.fetchone()[0]

        if self.cart[pid]["qty"] >= stock:
            messagebox.showwarning("Limit", "Not enough stock")
            return

        self.cart[pid]["qty"] += 1
        self.view_cart()

    def decrease_qty(self, pid):
        self.cart[pid]["qty"] -= 1

        if self.cart[pid]["qty"] <= 0:
            del self.cart[pid]

        self.view_cart()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty", "Cart is empty")
            return

        total = 0
        items_list = []

        for pid, item in self.cart.items():
            subtotal = item["price"] * item["qty"]
            total += subtotal

            items_list.append(f"{item['name']} x{item['qty']}")

            self.cursor.execute(
                "UPDATE products SET stock=stock-? WHERE id=?",
                (item["qty"], pid)
            )

        items = ", ".join(items_list)

        self.cursor.execute("""
                            INSERT INTO orders (user_id, total, items, placed_time, status, notified)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                self.current_user["id"],
                                total,
                                items,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Placed",
                                0  
                            ))
        self.conn.commit()
        self.cart.clear()

        messagebox.showinfo("Success", "Order placed!")
        self.home()

    def admin_panel(self):
        self.clear()
        self.header("Admin Panel")

        btn1 = tk.Button(self.root, text="Add Product", command=self.add_product)
        btn1.pack(pady=5)

        btn2 = tk.Button(self.root, text="Manage Products", command=self.manage_products)
        btn2.pack(pady=5)

        btn3 = tk.Button(self.root, text="View Dashboard", command=self.admin_dashboard)
        btn3.pack(pady=5)

        btn4 = tk.Button(self.root, text="Manage Orders", command=self.manage_orders)
        btn4.pack(pady=5)

        btn5 = tk.Button(self.root, text="Back", command=self.home)
        btn5.pack(pady=20)

    def add_product(self):
        self.clear()
        self.header("Add Product")
        self.p_image = tk.Entry(self.root)
        self.p_image.pack(pady=5)

        self.p_name = tk.Entry(self.root)
        self.p_price = tk.Entry(self.root)
        self.p_stock = tk.Entry(self.root)
        self.p_desc = tk.Entry(self.root, width=50)
        self.p_desc.pack(pady=5)

        for w in [self.p_name, self.p_price, self.p_stock]:
            w.pack(pady=5)

        save_btn = tk.Button(self.root, text="Save", command=self.save_product)
        save_btn.pack()
        back_btn = tk.Button(self.root, text="Back", command=self.admin_panel)
        back_btn.pack()
        tk.Label(self.root, text="(Image Path)",font=("Arial", 9), fg="gray", bg="#eef2f7").pack()

        self.p_image = tk.Entry(self.root, width=40)
        self.p_image.pack(pady=5)

        tk.Button(self.root, text="Browse Image", command=self.browse_image).pack()

    def save_product(self):
        name = self.p_name.get()
        price = self.p_price.get()
        stock = self.p_stock.get()
        desc = self.p_desc.get()
        image = self.p_image.get()

        #validation
        if image:
            filename = os.path.basename(image)
            new_path = f"product_images/{filename}"
            shutil.copy(image, new_path)
            image = new_path

        if not name or not price or not stock or not desc or not image:
            messagebox.showerror("Error", "Please!! all fields are required...")
            return
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Error", "Price must be number, and stock must be integer")

            self.cursor.execute("INSERT INTO products VALUES (NULL,?,?,?,?,?)"),(name, price, stock, desc, image)


            self.conn.commit()
            messagebox.showinfo("Success", "Product added successfully!")
            self.admin_panel()


    def manage_products(self):
        self.clear()
        self.header("Manage Products")

        self.cursor.execute("SELECT * FROM products")
        for p in self.cursor.fetchall():
            f = tk.Frame(self.root)
            f.pack(fill="x")

            tk.Label(f, text=f"{p[1]} ₱{p[2]} Stock:{p[3]}").pack(side="left")

            tk.Button(f, text="Delete", command=lambda x=p[0]: self.delete_product(x)).pack(side="right")
            tk.Button(f, text="Edit", command=lambda x=p: self.edit_product(x)).pack(side="right")

        tk.Button(self.root, text="Back", command=self.admin_panel).pack()

    def admin_dashboard(self):
        self.clear()
        self.header("Admin Dashboard")

        self.cursor.execute("SELECT SUM(total) FROM orders")
        total_sales = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT name, stock FROM products WHERE stock <= 5")
        low_stock = self.cursor.fetchall()

        tk.Label(self.root, text=f"Total Sales: ₱{total_sales}", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text=f"Total Orders: {total_orders}", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text="Low Stock Products:", font=("Arial", 14, "bold")).pack(pady=(20, 5))

        if not low_stock:
            tk.Label(self.root, text="All products have sufficient stock").pack()
        else:
            for p in low_stock:
                tk.Label(self.root, text=f"{p[0]} - Stock: {p[1]}").pack(anchor="w", padx=20)

        tk.Button(self.root, text="Back", command=self.admin_panel).pack(pady=20)


    def delete_product(self, pid):
        self.cursor.execute("DELETE FROM products WHERE id=?", (pid,))
        self.conn.commit()
        self.manage_products()



    def reset_database(self):
        self.cursor.execute("DROP TABLE IF EXISTS users")
        self.cursor.execute("DROP TABLE IF EXISTS products")
        self.cursor.execute("DROP TABLE IF EXISTS orders")
        self.conn.commit()
        self.create_tables()
        self.seed_products()


    def edit_product(self, p):
        self.clear()
        self.header("Edit Product")

        self.ep_name = tk.Entry(self.root)
        self.ep_price = tk.Entry(self.root)
        self.ep_stock = tk.Entry(self.root)
        self.ep_desc = tk.Entry(self.root, width=50)

        self.ep_name.insert(0, p[1])
        self.ep_price.insert(0, p[2])
        self.ep_stock.insert(0, p[3])
        self.ep_desc.insert(0, p[4])

        for w in [self.ep_name, self.ep_price, self.ep_stock, self.ep_desc]:
            w.pack(pady=5)

        tk.Button(self.root, text="Update",command=lambda: self.update_product(p[0])).pack()
        tk.Button(self.root, text="Back",command=self.manage_products).pack()



    def manage_orders(self):
        self.clear()
        self.header("Manage Orders")

        self.cursor.execute("SELECT id, items, status FROM orders")
        order_list = self.cursor.fetchall()  # renamed

        for o in order_list:
            f = tk.Frame(self.root)
            f.pack(fill="x", pady=5)

            tk.Label(
                f,
                text=f"Order #{o[0]} | {o[1]} | Status: {o[2]}"
            ).pack(side="left")

            tk.Button(
                f,
                text="Ship",
                command=lambda oid=o[0]: self.update_status(oid, "Shipped")
            ).pack(side="right", padx=5)

            tk.Button(
                f,
                text="Deliver",
                command=lambda oid=o[0]: self.update_status(oid, "Delivered")
            ).pack(side="right", padx=5)

        # separate widget (no chaining issue)
        back_btn = tk.Button(self.root, text="Back", command=self.admin_panel)
        back_btn.pack(pady=10)



    @staticmethod
    def calculate_duration(start, end):
        try:
            start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

            duration = end_time - start_time

            days = duration.days
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            return f"{days}d {hours}h {minutes}m"
        except:
            return "N/A"

    def ask_feedback(self, order_id):
        win = tk.Toplevel(self.root)
        win.title("Feedback")

        tk.Label(win, text="Leave your feedback").pack(pady=10)
        feedback_entry = tk.Text(win, width=40, height=5)
        feedback_entry.pack(pady=10)

        def submit():
            msg = feedback_entry.get("1.0", tk.END).strip()

            if msg:
                self.cursor.execute("""
                                    INSERT INTO feedback (user_id, order_id, message, date)
                                    VALUES (?, ?, ?, ?)
                                    """, (
                self.current_user["id"], order_id,msg,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                self.conn.commit()

                messagebox.showinfo("Thanks!", "Feedback submitted")
                win.destroy()
            else:
                messagebox.showwarning("Empty", "Please write something")

        tk.Button(win, text="Submit", command=submit).pack(pady=10)

    def update_product(self, pid):
        try:
            self.cursor.execute("""
                UPDATE products SET name=?,price=?,stock=?,description=? WHERE id=?
                """, (
                    self.ep_name.get(),
                    float(self.ep_price.get()),
                    int(self.ep_stock.get()),
                    self.ep_desc.get(),
                    pid))
            self.conn.commit()
            self.manage_products()

        except ValueError:
            messagebox.showerror("Error", "Invalid price or stock")


    def run(self):
        self.root.mainloop()



    def confirm_received(self, order_id):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("""UPDATE orders SET status='Received',received_time=? WHERE id = ?
                              """,(current_time, order_id))
        self.conn.commit()

        messagebox.showinfo("Thank you", "Order marked as received")

        self.ask_feedback(order_id)
        self.view_orders()


    def view_feedback(self):
        self.clear()
        self.header("Customer Feedback")

        self.cursor.execute("""
                            SELECT user_id, order_id, message, date FROM feedback """)
        data = self.cursor.fetchall()

        if not data:
            tk.Label(self.root, text="No feedback yet").pack()
        else:
            for f in data:
                tk.Label(self.root, text=f"User {f[0]} | Order #{f[1]}\n{f[2]}\n{f[3]}",justify="left",
                wraplength=600 ).pack(pady=5)

        tk.Button(self.root, text="Back", command=self.admin_panel).pack(pady=10)


if __name__ == "__main__":
    try:
        app = MuscleLabApp()
        app.run()
    except Exception as e:
        print("ERROR:", e)
        input("Press Enter to exit...")