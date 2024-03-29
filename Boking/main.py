import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog
from tkinter import ttk
import psycopg2
from psycopg2.errors import TransactionRollbackError


class UserManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Главное окно")

        self.conn = psycopg2.connect(
            host="127.0.0.1",
            database="Booking",
            user="postgres",
            password="02092004Art"
        )
        # Кнопки
        self.btn_register = ttk.Button(root, text="Зарегистрироваться", command=self.open_registration_form)
        self.btn_register.pack(pady=10)

        self.btn_authenticate = ttk.Button(root, text="Авторизоваться", command=self.open_authentication_form)
        self.btn_authenticate.pack(pady=10)

        self.btn_exit = ttk.Button(root, text="Закрыть приложение", command=root.destroy)
        self.btn_exit.pack(pady=10)

    def open_registration_form(self):
        registration_window = tk.Toplevel(self.root)
        registration_window.title("Форма регистрации")
        registration_form = RegistrationForm(registration_window)

    def open_authentication_form(self):
        authentication_window = tk.Toplevel(self.root)
        authentication_window.title("Форма аутентификации")
        authentication_form = AuthenticationForm(authentication_window)


class RegistrationForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Форма регистрации")
        self.conn = psycopg2.connect(
            host="127.0.0.1",
            database="Booking",
            user="postgres",
            password="02092004Art"
        )

        self.label_username = ttk.Label(root, text="Имя пользователя:")
        self.entry_username = ttk.Entry(root)

        self.label_password = ttk.Label(root, text="Пароль:")
        self.entry_password = ttk.Entry(root, show="*")

        self.label_first_name = ttk.Label(root, text="Имя:")
        self.entry_first_name = ttk.Entry(root)

        self.label_last_name = ttk.Label(root, text="Фамилия:")
        self.entry_last_name = ttk.Entry(root)

        self.btn_register = ttk.Button(root, text="Зарегистрироваться", command=self.register_user)

        # Размещение элементов на форме
        self.label_username.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_username.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_password.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_password.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_first_name.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_first_name.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_last_name.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_last_name.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        self.btn_register.grid(row=4, columnspan=2, pady=10)

    def register_user(self):
        # Получите значения из элементов интерфейса
        user_login = self.entry_username.get()
        user_password = self.entry_password.get()
        user_first_name = self.entry_first_name.get()
        user_last_name = self.entry_last_name.get()

        # Проверка наличия данных
        if any(not data.strip() for data in [user_login, user_password, user_first_name, user_last_name]):
            messagebox.showerror("Error", "All fields must be filled")
            return

        try:
            # Открываем транзакцию
            with self.conn:
                with self.conn.cursor() as cursor:
                    # Проверяем наличие пользователя в базе данных
                    cursor.execute("SELECT 1 FROM Users WHERE user_login = %s", (user_login,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        messagebox.showerror("Error", "User with this login already exists")
                        return

                    # Вызываем процедуру регистрации
                    cursor.execute("CALL create_user(%s, %s, %s, %s, %s)",
                                   (user_login, user_password, user_first_name, user_last_name, 2))

            # Показываем сообщение об успешном выполнении
            messagebox.showinfo("Success", "Operation completed successfully!")
            #UserMainWindow(self.root, self.conn, 2)


        except TransactionRollbackError as e:
            # В случае ошибки откатываем транзакцию
            print("Error", f"An error occurred: {e}")

        #finally:
            #self.root.destroy()


def get_table_columns(table_name, conn):
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
        """
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cursor.close()


def create_table_from_columns(root, table_columns):
    table_frame = ttk.Frame(root)
    table_frame.pack()

    for column_name, in table_columns:
        label = ttk.Label(table_frame, text=column_name, borderwidth=1, relief="solid", width=20)
        label.pack(side="left")

    return table_frame


def remove_treeview(root):
    # Получить все дочерние элементы root
    children = root.winfo_children()

    # Найти и удалить объект ttk.Treeview
    for child in children:
        if isinstance(child, ttk.Treeview):
            child.destroy()


def load_data(root, conn, table_name='actionlog'):
    remove_treeview(root)

    try:
        with conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            results = cursor.fetchall()

            # Create Treeview widget
            treeview = ttk.Treeview(root)
            treeview["columns"] = [column_name for column_name, in get_table_columns(table_name, conn)]
            treeview.heading("#0", text="", anchor="w")
            treeview.column("#0", anchor="w", width=1)

            for column_name, in get_table_columns(table_name, conn):
                treeview.heading(column_name, text=column_name)
                treeview.column(column_name, anchor="w", width=100)

            treeview.pack()

            # Fill Treeview with data
            for row in results:
                treeview.insert("", "end", values=row)

    except Exception as e:
        print(f"Error: {e}")


def get_user_id_by_login(conn, user_login):
    try:
        with conn.cursor() as cursor:
            query = "SELECT id_user FROM users WHERE user_login = %s"
            cursor.execute(query, (user_login,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    except Exception as e:
        print(f"Error: {e}")
        return None


class CreateOfferWindow:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn

        self.create_order_window = tk.Toplevel(root)
        self.create_order_window.title("Create Offer")

        # Fetch data for dropdown list
        apartment_data = self.fetch_apartment_data()

        # Dropdown for apartment selection
        self.apartment_label = tk.Label(self.create_order_window, text="Apartment:")
        self.apartment_var = tk.StringVar()
        self.apartment_dropdown = ttk.Combobox(self.create_order_window, textvariable=self.apartment_var,
                                               values=apartment_data)
        self.apartment_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.apartment_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Other entry fields for order details
        self.price_label = tk.Label(self.create_order_window, text="Price per Night:")
        self.price_entry = tk.Entry(self.create_order_window)
        self.price_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.price_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        self.stay_days_label = tk.Label(self.create_order_window, text="Stay Days:")
        self.stay_days_entry = tk.Entry(self.create_order_window)
        self.stay_days_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.stay_days_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        self.country_label = tk.Label(self.create_order_window, text="Country:")
        self.country_entry = tk.Entry(self.create_order_window)
        self.country_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.country_entry.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)

        self.address_label = tk.Label(self.create_order_window, text="Address:")
        self.address_entry = tk.Entry(self.create_order_window)
        self.address_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        self.address_entry.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

        # Button to submit the order
        self.submit_button = tk.Button(self.create_order_window, text="Submit Order", command=self.submit_order)
        self.submit_button.grid(row=5, column=0, columnspan=2, pady=20)

    def fetch_apartment_data(self):
        try:
            with self.conn.cursor() as cursor:
                query = """
                SELECT
                    type_name,
                    num_of_floors,
                    num_of_rooms,
                    num_of_beds,
                    apartment_type
                FROM
                    apartments
                LEFT JOIN apartmenttypes ON apartments.apartment_type::int = apartmenttypes.id;
                """
                cursor.execute(query)
                apartment_data = cursor.fetchall()
                return [f"{data[0]} - {data[1]} floors, {data[2]} rooms, {data[3]} beds" for data in apartment_data]
        except Exception as e:
            print(f"Error fetching apartment data: {e}")
            return []

    def validate_numeric_input(self, value):
        try:
            float_value = float(value)
            if float_value < 0:
                return False
            return True
        except ValueError:
            return False

    def submit_order(self):
        try:
            selected_apartment = self.apartment_var.get()
            print(self.apartment_var.get())
            price_per_night = self.price_entry.get()
            stay_days = self.stay_days_entry.get()
            country = self.country_entry.get()
            address = self.address_entry.get()

            if not self.validate_numeric_input(price_per_night) or not self.validate_numeric_input(stay_days):
                tk.messagebox.showerror("Error", "Invalid numeric input for price per night or stay days")
                return

            if not selected_apartment or not country or not address:
                tk.messagebox.showerror("Error", "All fields must be filled")
                return

            with self.conn.cursor() as cursor:
                apartment_type = selected_apartment.split(" - ")[0]
                cursor.execute("SELECT id FROM apartmenttypes WHERE type_name = %s", (apartment_type,))
                apartment_id = cursor.fetchone()[0]

                insert_query = """
                INSERT INTO Offers (apartment_id, price_per_night, stay_days, country, address)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_offer;
                """
                cursor.execute(insert_query, (apartment_id, price_per_night, stay_days, country, address))
                offer_id = cursor.fetchone()[0]

                self.conn.commit()

                tk.messagebox.showinfo("Success", f"Offer submitted successfully! Offer ID: {offer_id}")

                # Close the create_order_window
                self.create_order_window.destroy()

        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")


class AdminMainWindow:
    def __init__(self, root, conn, admin_id):
        self.root = root
        self.conn = conn
        self.admin_id = admin_id

        self.label_welcome = tk.Label(self.root, text=f"Welcome, Admin (Admin ID: {admin_id})")
        self.label_welcome.pack()

        self.treeview = ttk.Treeview(self.root)

        self.button_load_data = tk.Button(self.root, text="Load data", command=self.load_data_1)
        self.button_create_offer = tk.Button(self.root, text="Create Offer", command=self.create_offer)
        self.button_update_user = tk.Button(self.root, text="Update User", command=self.update_user_role)
        self.button_delete_user = tk.Button(self.root, text="Delete User", command=self.delete_user)
        self.button_edit_answer = tk.Button(self.root, text="Edit Answer", command=self.answer_question)

        self.button_load_data.pack()
        self.button_create_offer.pack()
        self.button_update_user.pack()
        self.button_delete_user.pack()
        self.button_edit_answer.pack()

    def load_data_1(self, name='actionlog'):
        load_data(self.root, self.conn, name)

    def create_offer(self):
        create_order_window = CreateOfferWindow(root, self.conn)

        # Ждем, пока окно заказа не будет закрыто
        root.wait_window(create_order_window.create_order_window)

        # После закрытия окна заказа выполняем load_data
        load_data(self.root, self.conn, 'offers')

    def update_user_role(self):
        update_user_role_window = UpdateUserRoleWindow(root, self.conn)

    def delete_user(self):
        delete_user_window = DeleteUserWindow(root, self.conn)

    def answer_question(self):
        edit_answer_window = EditAnswerWindow(self.root, self.conn)


class UpdateUserRoleWindow:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn

        self.update_user_role_window = tk.Toplevel(root)
        self.update_user_role_window.title("Update User Role")

        # Label and Combobox for User Login
        self.user_login_label = tk.Label(self.update_user_role_window, text="User Login:")
        self.user_login_var = tk.StringVar()
        self.user_login_combobox = ttk.Combobox(self.update_user_role_window, textvariable=self.user_login_var)
        self.user_login_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.user_login_combobox.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Label and Combobox for User Role
        self.user_role_label = tk.Label(self.update_user_role_window, text="User Role:")
        self.user_role_var = tk.StringVar()
        self.user_role_combobox = ttk.Combobox(
            self.update_user_role_window,
            textvariable=self.user_role_var,
            values=["Admin", "Moderator", "User"]
        )
        self.user_role_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.user_role_combobox.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Button to update user role
        self.update_button = tk.Button(self.update_user_role_window, text="Update Role", command=self.update_role)
        self.update_button.grid(row=2, column=0, columnspan=2, pady=20)

        # Fetch user data for Combobox
        self.fetch_user_data()

    def fetch_user_data(self):
        try:
            with self.conn.cursor() as cursor:
                query = "SELECT id_user, user_login, role_id FROM users"
                cursor.execute(query)
                user_data = cursor.fetchall()

            # Update Combobox with user logins
            logins = [f"{login} ({role})" for _, login, role in user_data]
            self.user_login_combobox["values"] = logins

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while fetching user data: {e}")

    def update_role(self):
        try:
            selected_login = self.user_login_var.get()
            user_id = selected_login.split(" ")[0]  # Extract user ID from the selected login
            user_role = self.user_role_var.get()
            tmp = {"Admin": 1, "User": 2, "Moderator": 4}
            user_role = tmp.get(user_role)

            with self.conn.cursor() as cursor:
                # Assuming you have a table named "users" with columns "id" and "role"
                update_query = "UPDATE users SET role_id = %s WHERE user_login = %s"
                cursor.execute(update_query, (user_role, user_id))

            self.conn.commit()
            messagebox.showinfo("Success", "User role updated successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


class UserMainWindow:
    def __init__(self, root, conn, login):
        self.root = root
        self.conn = conn
        self.login = login

        # Добавьте элементы интерфейса для окна пользователя
        self.label_welcome = tk.Label(self.root, text=f"Welcome, User (User: {login})")
        self.label_welcome.pack(pady=10)

        self.btn_view_offers = tk.Button(self.root, text="View Offers", command=self.view_offers)
        self.btn_view_offers.pack(pady=5)

        self.btn_view_reviews = tk.Button(self.root, text="View Reviews", command=self.view_reviews)
        self.btn_view_reviews.pack(pady=5)

        self.btn_create_question = tk.Button(self.root, text="Ask a Question", command=self.create_question)
        self.btn_create_question.pack(pady=5)

        self.btn_create_review = tk.Button(self.root, text="Write a Review", command=self.create_review)
        self.btn_create_review.pack(pady=5)

        self.btn_create_order = tk.Button(self.root, text="Create Order", command=self.create_order)
        self.btn_create_order.pack(pady=5)

        self.btn_cansel_order = tk.Button(self.root, text="Cancel Order", command=self.cansel_order)
        self.btn_cansel_order.pack(pady=5)
        # Создайте новый контейнер с использованием pack
        self.treeview = ttk.Treeview(self.root)

    def view_offers(self):
        load_data(self.root, self.conn, 'offers')

    def view_reviews(self):
        load_data(self.root, self.conn, 'reviews')

    def create_question(self):
        user_id = get_user_id_by_login(self.conn, self.login)
        qAWindow = QAWindow(self.root, self.conn, user_id)

    def create_review(self):
        user_id = get_user_id_by_login(self.conn, self.login)
        createReviewWindow = CreateReviewWindow(self.root, self.conn, user_id)

    def create_order(self):
        user_id = get_user_id_by_login(self.conn, self.login)
        createWindow = CreateOrderWindow(root, self.conn, user_id)

    def cansel_order(self):
        user_id = get_user_id_by_login(self.conn, self.login)
        canselWindow = CancelOrderWindow(self.root, self.conn, user_id)


class DeleteUserWindow:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn

        self.delete_user_window = tk.Toplevel(root)
        self.delete_user_window.title("Delete User")

        # Label and Combobox for User Login
        self.user_login_label = tk.Label(self.delete_user_window, text="User Login:")
        self.user_login_var = tk.StringVar()
        self.user_login_combobox = ttk.Combobox(self.delete_user_window, textvariable=self.user_login_var)
        self.user_login_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.user_login_combobox.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Button to delete user
        self.delete_button = tk.Button(self.delete_user_window, text="Delete User", command=self.delete_user)
        self.delete_button.grid(row=1, column=0, columnspan=2, pady=20)

        # Fetch user data for Combobox
        self.fetch_user_data()

    def fetch_user_data(self):
        try:
            with self.conn.cursor() as cursor:
                query = "SELECT id_user, user_login FROM users"
                cursor.execute(query)
                user_data = cursor.fetchall()

            # Update Combobox with user logins
            logins = [f"{login} (ID: {user_id}" for user_id, login in user_data]
            self.user_login_combobox["values"] = logins

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while fetching user data: {e}")

    def delete_user(self):
        try:
            selected_login = self.user_login_var.get()
            user_id = selected_login.split("ID: ")[1]  # Extract user ID from the selected login
            print(user_id)

            with self.conn.cursor() as cursor:
                # Assuming you have a table named "users" with columns "id_user"
                delete_query = "DELETE FROM users WHERE id_user = %s"
                cursor.execute(delete_query, (user_id,))

            self.conn.commit()
            messagebox.showinfo("Success", "User deleted successfully!")

        except Exception as e:
            # messagebox.showerror("Error", f"An error occurred: {e}")
            print("Error", f"An error occurred: {e}")


class QAWindow:
    def __init__(self, root, conn, user_id):
        self.root = root
        self.conn = conn
        self.user_id = user_id

        self.qa_window = tk.Toplevel(root)
        self.qa_window.title("Q&A Window")

        # Создаем PanedWindow для разделения окна на две части
        self.paned_window = ttk.Panedwindow(self.qa_window, orient=tk.HORIZONTAL)
        self.paned_window.pack(expand=True, fill=tk.BOTH)

        # Создаем Frame для отображения вопросов и ответов
        self.qa_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.qa_frame, weight=1)

        # Создаем Treeview для отображения вопросов и ответов
        self.qa_treeview = ttk.Treeview(self.qa_frame, columns=("User", "Question", "Answer"),
                                        displaycolumns=("User", "Question", "Answer"))
        self.qa_treeview.heading("User", text="User")
        self.qa_treeview.heading("Question", text="Question")
        self.qa_treeview.heading("Answer", text="Answer")
        self.qa_treeview.column("#0", width=0, stretch=tk.NO)  # Устанавливаем ширину 0, чтобы скрыть столбец ID
        self.qa_treeview.pack(expand=True, fill=tk.BOTH)

        # Создаем Frame для создания вопроса
        self.create_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.create_frame, weight=1)

        # Label и Text Entry для вопроса

        self.question_label = tk.Label(self.create_frame, text="Question:")
        self.question_entry = tk.Text(self.create_frame, height=5, width=50)
        self.question_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.question_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Button для создания вопроса
        self.create_button = tk.Button(self.create_frame, text="Create Question", command=self.create_question)
        self.create_button.grid(row=2, column=0, columnspan=2, pady=20)

        # Инициализируем Treeview данными
        self.fetch_questions()

    def create_question(self):
        try:
            # Получаем информацию о пользователе и вопросе
            question_text = self.question_entry.get("1.0", tk.END).strip()

            # Проверяем, что пользователь и вопрос не пусты
            if not question_text:
                return

            self.add_question(self.user_id, question_text)

            self.question_entry.delete("1.0", tk.END)

            # Обновляем Treeview
            self.fetch_questions()

            messagebox.showinfo("Success", "Question created successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def add_question(self, user_id, question_text):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    INSERT INTO questions (user_id, status, question_text, answer_text)
                    VALUES (%s, false, %s, '-');
                """
                cursor.execute(query, (user_id, question_text))
                self.conn.commit()
                self.fetch_questions()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while adding a question: {e}")

    def fetch_questions(self):
        try:
            with self.conn.cursor() as cursor:
                query = """
                    SELECT user_login, question_text, answer_text
                    FROM questions
                    RIGHT JOIN users ON questions.user_id = users.id_user
                    WHERE status IS NOT NULL
                """
                cursor.execute(query)
                results = cursor.fetchall()

                # Очищаем Treeview перед обновлением
                self.qa_treeview.delete(*self.qa_treeview.get_children())

                # Заполняем Treeview снова
                for row in results:
                    self.qa_treeview.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while fetching questions: {e}")


class EditAnswerWindow:
    def __init__(self, root, conn):
        self.edit_answer_window = tk.Toplevel(root)
        self.edit_answer_window.title("Edit Answer Window")

        self.conn = conn

        # Создаем переменные для фильтрации вопросов
        self.show_unanswered = tk.BooleanVar(value=True)
        self.show_answered = tk.BooleanVar(value=True)

        # Создаем фрейм для фильтров
        filter_frame = tk.Frame(self.edit_answer_window)
        filter_frame.pack(pady=10)

        # Создаем чекбоксы для фильтрации вопросов

        # Создаем Treeview для отображения вопросов
        self.treeview = ttk.Treeview(self.edit_answer_window, columns=("User", "Question", "Answer"),
                                     displaycolumns=("User", "Question", "Answer"))
        self.treeview.heading("User", text="User")
        self.treeview.heading("Question", text="Question")
        self.treeview.heading("Answer", text="Answer")
        self.treeview.column("#0", width=0, stretch=tk.NO)  # Устанавливаем ширину 0, чтобы скрыть столбец ID

        self.treeview.pack(expand=True, fill=tk.BOTH)

        # Button для изменения ответа
        tk.Button(self.edit_answer_window, text="Edit Answer", command=self.edit_answer).pack(pady=10)

        # Загрузим данные в Treeview
        self.load_data()

    def load_data(self):
        try:
            with self.conn.cursor() as cursor:
                # Формируем запрос в зависимости от выбранных фильтров
                query = "SELECT user_login, question_text, answer_text FROM questions RIGHT JOIN users ON questions.user_id = users.id_user WHERE status IS NOT NULL"

                conditions = []
                if not self.show_unanswered.get():
                    conditions.append("status = false")
                if not self.show_answered.get():
                    conditions.append("status = true")
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                cursor.execute(query)
                results = cursor.fetchall()

                # Очищаем Treeview
                self.treeview.delete(*self.treeview.get_children())

                # Заполняем Treeview с новыми данными
                for row in results:
                    self.treeview.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def edit_answer(self):
        # Получите выделенный вопрос из Treeview
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a question to edit.")
            return

        # Получите данные о выделенном вопросе
        question_data = self.treeview.item(selected_item, "values")
        print(question_data)

        # Диалог для ввода нового ответа
        new_answer_text = simpledialog.askstring("Edit Answer", "Enter the new answer:")
        print(new_answer_text)

        # Обновите ответ в базе данных
        with self.conn.cursor() as cursor:
            query = ("UPDATE questions "
                     "SET answer_text = %s, status = true "
                     "WHERE user_id = (SELECT id_user FROM users WHERE user_login = %s) "
                     "AND question_text = %s")

            cursor.execute(query, (new_answer_text, question_data[0], question_data[1]))

        self.conn.commit()

        # Обновите Treeview
        self.load_data()

        messagebox.showinfo("Success", "Answer edited successfully!")


def open_main_window(user_id):
    root = tk.Tk()
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="Booking",
        user="postgres",
        password="02092004Art")

    with conn.cursor() as cursor:
        query = "SELECT role_id, user_login FROM Users WHERE id_user = %s;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

    if result[0] == 1:  # Пример ID для администратора
        AdminMainWindow(root, conn, result[1])
    elif result[0] == 2:  # Пример ID для пользователя
        UserMainWindow(root, conn, result[1])
    elif result[0] == 4:  # Пример ID для модератора
        ModeratorMainWindow(root, conn, result[1])


    root.mainloop()


class AuthenticationForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Форма аутентификации")
        self.conn = psycopg2.connect(
            host="127.0.0.1",
            database="Booking",
            user="postgres",
            password="02092004Art"
        )

        # Элементы интерфейса для формы аутентификации
        self.label_username = ttk.Label(root, text="Имя пользователя:")
        self.entry_username = ttk.Entry(root)
        self.entry_username.insert(0, '1')

        self.label_password = ttk.Label(root, text="Пароль:")
        self.entry_password = ttk.Entry(root, show="*", )
        self.entry_password.insert(0, '1')

        self.btn_authenticate = ttk.Button(root, text="Войти", command=self.authenticate_user)

        # Размещение элементов на форме
        self.label_username.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_username.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_password.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_password.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.btn_authenticate.grid(row=2, columnspan=2, pady=10)

    def authenticate_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            # Открываем транзакцию
            self.conn.autocommit = False

            with self.conn.cursor() as cursor:
                # Вызываем процедуру аутентификации
                cursor.execute("SELECT authenticate_user(%s, %s)", (username, password))

                # Получаем результат
                result = cursor.fetchone()

                # Если результат True, то аутентификация прошла успешно
                if result and result[0]:
                    # cursor.execute("CALL log_authentication(%s, %s)", (result[0], "User authenticated successfully"))
                    # messagebox.showinfo("Authentication", "Authentication successful!")
                    self.root.destroy()
                    open_main_window(result[0])
                else:
                    messagebox.showerror("Authentication", "Authentication failed.")

            # Подтверждаем транзакцию
            self.conn.commit()


        except Exception as e:
            # В случае ошибки выводим сообщение и откатываем транзакцию
            print("Error", f"An error occurred: {e}")
            self.conn.rollback()

        finally:
            # Восстанавливаем режим автокоммита и закрываем соединение
            self.conn.autocommit = True
            #self.root.destroy()


class CreateReviewWindow:
    def __init__(self, root, conn, user_id):
        self.root = root
        self.conn = conn
        self.user_id = user_id

        self.create_review_window = tk.Toplevel(root)
        self.create_review_window.title("Create Review")

        # Label и Combobox для выбора предложения
        self.offer_label = tk.Label(self.create_review_window, text="Select Offer:")
        self.offer_combobox = ttk.Combobox(self.create_review_window)
        self.offer_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.offer_combobox.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Label и Text Entry для отзыва

        self.review_label = tk.Label(self.create_review_window, text="Review:")
        self.review_entry = tk.Text(self.create_review_window, height=5, width=50)
        self.review_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.review_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        # Rating
        self.rating_label = tk.Label(self.create_review_window, text="Rating:")
        self.rating_combobox = ttk.Combobox(self.create_review_window, values=[i for i in range(1, 6)])
        self.rating_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.rating_combobox.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)

        # Button для создания отзыва
        self.create_button = tk.Button(self.create_review_window, text="Create Review", command=self.create_review)
        self.create_button.grid(row=4, column=0, columnspan=2, pady=20)

        # Заполним Combobox данными
        self.populate_combobox()

    def populate_combobox(self):
        try:
            with self.conn.cursor() as cursor:
                query = ("SELECT "
                         "id_offer,"
                         " price_per_night,"
                         " stay_days, "
                         "country,"
                         " address "
                         "FROM"
                         " offers")
                cursor.execute(query)
                offers = cursor.fetchall()

                # Формируем текст для отображения в Combobox
                display_values = [f"{offer[3]} - {offer[4]} - {offer[2]} - {offer[1]} - {offer[0]} " for offer in
                                  offers]

                self.offer_combobox['values'] = display_values

                # Установим первый элемент по умолчанию
                self.offer_combobox.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def create_review(self):
        try:
            # Получаем информацию о предложении, пользователе, отзыве и рейтинге
            offer_name = self.offer_combobox.get().strip()
            offer_id = int(offer_name.split('-')[4])

            review_text = self.review_entry.get("1.0", tk.END).strip()
            rating = self.rating_combobox.get().strip()

            # Проверяем, что предложение, пользователь, отзыв и рейтинг не пусты
            if not offer_name or not review_text or not rating:
                messagebox.showwarning("Warning", "Please enter offer, user, review, and rating.")
                return

            # Выполняем логику сохранения отзыва в базу данных
            with self.conn.cursor() as cursor:
                query = "INSERT INTO reviews (review_text, rating, user_id, offer_id) VALUES (%s, %s, %s, %s)"
                print(review_text, rating, self.user_id, offer_id)

                cursor.execute(query, (review_text, int(rating), self.user_id, offer_id))
                self.conn.commit()

            # Очищаем поля после создания
            self.offer_combobox.set('')
            self.review_entry.delete("1.0", tk.END)
            self.rating_combobox.set('')

            # Оповещаем пользователя об успешном создании отзыва
            messagebox.showinfo("Success", "Review created successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


class CreateOrderWindow:
    def __init__(self, root, conn, user_id):
        self.root = root
        self.conn = conn
        self.user_id = user_id

        self.create_order_window = tk.Toplevel(root)
        self.create_order_window.title("Create Order")

        # Label и Combobox для выбора предложения
        self.offer_label = tk.Label(self.create_order_window, text="Select Offer:")
        self.offer_combobox = ttk.Combobox(self.create_order_window)
        self.offer_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.offer_combobox.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Label и Entry для ввода даты заказа
        self.date_label = tk.Label(self.create_order_window, text="Order Date:")
        self.date_entry = tk.Entry(self.create_order_window)
        self.date_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.date_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Button для создания заказа
        self.create_button = tk.Button(self.create_order_window, text="Create Order", command=self.create_order)
        self.create_button.grid(row=2, column=0, columnspan=2, pady=20)

        # Заполним Combobox данными
        self.populate_combobox()

    def populate_combobox(self):
        try:
            with self.conn.cursor() as cursor:
                query = (
                    "SELECT offers.country, offers.address, offers.price_per_night, offers.stay_days, offers.id_offer "
                    "FROM orders "
                    "RIGHT JOIN offers ON orders.offer_id = offers.id_offer")
                cursor.execute(query)
                orders = cursor.fetchall()

                # Формируем текст для отображения в Combobox
                display_values = [f"{order[0]} - {order[1]} - {order[2]} - {order[3]} - {order[4]}" for order in orders]

                self.offer_combobox['values'] = display_values

                # Установим первый элемент по умолчанию
                self.offer_combobox.current(0)
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

    def create_order(self):
        try:
            # Получаем информацию о выбранном предложении и введенной дате
            selected_order = self.offer_combobox.get().strip()
            order_date = self.date_entry.get().strip()

            # Проверяем, что оба поля не пусты
            if not selected_order or not order_date:
                tk.messagebox.showwarning("Warning", "Please select an offer and enter a date.")
                return

            # Разделяем строку предложения для получения offer_id
            offer_id = int(selected_order.split('-')[4])

            # Выполняем запрос к базе данных для создания заказа
            with self.conn.cursor() as cursor:
                query = "INSERT INTO Orders (offer_id, total_price, order_date, user_id) VALUES (%s, NULL, %s, %s)"
                cursor.execute(query, (offer_id, order_date, self.user_id))
                # Вставка записи в actionlog
                action_text = 'User created an order'
                query_actionlog = "INSERT INTO actionlog (user_id, action, action_date, description) VALUES (%s, %s, %s,%s)"
                cursor.execute(query_actionlog, (self.user_id, action_text, datetime.now(), action_text))

                self.conn.commit()

            # Очищаем поля после создания
            self.offer_combobox.set('')
            self.date_entry.delete(0, tk.END)

            # Оповещаем пользователя об успешном создании заказа
            tk.messagebox.showinfo("Success", "Order created successfully!")

        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

class CancelOrderWindow:
    def __init__(self, root, conn, user_id):
        self.root = root
        self.conn = conn
        self.user_id = user_id

        self.cancel_order_window = tk.Toplevel(root)
        self.cancel_order_window.title("Cancel Order")

        # Label и Combobox для выбора заказа
        self.order_label = tk.Label(self.cancel_order_window, text="Select Order:")
        self.order_combobox = ttk.Combobox(self.cancel_order_window)
        self.order_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.order_combobox.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Button для отмены заказа
        self.cancel_button = tk.Button(self.cancel_order_window, text="Cancel Order", command=self.cancel_order)
        self.cancel_button.grid(row=1, column=0, columnspan=2, pady=20)

        # Заполним Combobox данными
        self.populate_combobox()

    def populate_combobox(self):
        try:
            with self.conn.cursor() as cursor:
                query = "SELECT id_order FROM Orders WHERE user_id = %s"
                cursor.execute(query, (self.user_id,))
                orders = cursor.fetchall()

                # Формируем текст для отображения в Combobox
                display_values = [f"Order {order[0]}" for order in orders]

                self.order_combobox['values'] = display_values

                # Установим первый элемент по умолчанию
                self.order_combobox.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def cancel_order(self):
        try:
            # Получаем информацию о выбранном заказе
            selected_order = self.order_combobox.get()
            order_id = int(selected_order.split()[1])

            # Выполняем логику отмены заказа
            with self.conn.cursor() as cursor:
                # Добавим логирование отмены заказа в actionlog
                action_text = f"User canceled order {order_id}"

                # Удаляем заказ
                query_cancel_order = "DELETE FROM Orders WHERE id_order = %s"
                cursor.execute(query_cancel_order, (order_id,))
                query_actionlog = "INSERT INTO actionlog (user_id, action, action_date, description) VALUES (%s, %s, %s,%s)"
                cursor.execute(query_actionlog, (self.user_id, action_text, datetime.now(), action_text))
                self.conn.commit()

            # Обновим Combobox после отмены заказа
            self.populate_combobox()

            # Оповестим пользователя об успешной отмене заказа
            messagebox.showinfo("Success", f"Order {order_id} canceled successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


class ModeratorMainWindow:
    def __init__(self, root, conn, username):
        self.root = root
        self.conn = conn
        self.username = username

        self.root.title("Moderator Main Window")


        # Добавьте здесь ваш интерфейс для окна модератора

        self.label_welcome = tk.Label(self.root, text=f"Welcome, Moderator {self.username}")
        self.label_welcome.pack(pady=10)

        # ПКнопка для загрузки данных
        self.button_create_order = tk.Button(self.root, text="Load Data", command=self.load_data_1)
        self.button_create_order.pack(pady=10)

        # Кнопка для ответа
        self.button_cancel_order = tk.Button(self.root, text="Answer", command=self.answer_question)
        self.button_cancel_order.pack(pady=10)

    def answer_question(self):
        edit_answer_window = EditAnswerWindow(self.root, self.conn)

    def load_data_1(self, name='actionlog'):
        load_data(self.root, self.conn, name)

if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementApp(root)
    root.mainloop()