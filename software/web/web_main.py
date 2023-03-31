####### IMPORTS #######
from flask import Flask, redirect, url_for, send_from_directory, render_template, request, session, flash, Markup
from flask_mysqldb import MySQL
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import smtplib
from email.message import EmailMessage
import string
import secrets
import hashlib
import re
from requests import get
import auxiliary_functions as func
import database_functions as dbsql

app = Flask(__name__)
# app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))
app.secret_key = "Test"  # Make key complicated at one point
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TBUASv565GdfPByVKdx2@senior-project.cqpzjknbrdd2.us-west-2.rds.amazonaws.com'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.sqlite3'
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False
# permanent session will be kept for this long
app.permanent_session_lifetime = timedelta(days=1)

database_name = "SJSU"
database_table_name = "PERSONNELS"
database_pass = "TBUASv565GdfPByVKdx2"

app.config['MYSQL_HOST'] = "senior-project.cqpzjknbrdd2.us-west-2.rds.amazonaws.com"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = database_pass
app.config['MYSQL_DB'] = database_name
mysql = MySQL(app)

database_columns = {}

database_object = dbsql.Database(user="root",
                                 host="senior-project.cqpzjknbrdd2.us-west-2.rds.amazonaws.com",
                                 database_name=database_name)

db = SQLAlchemy(app)
global_roles = ["user", "sysop", "root"]
admin_roles = global_roles[1:]


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # unique identity
    user = db.Column(db.String(100))  # name containing max 100 characters
    email = db.Column(db.String(100))  # email containing max 100 characters
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(100))  # email containing max 100 characters
    roles = db.Column(db.String)
    ip = db.Column(db.String)
    active = db.Column(db.Boolean)

    def __init__(self, user, email, first_name, last_name, password, roles, active=False, ip=""):
        self.user = user
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.roles = roles
        self.active = active
        self.ip = ip


####### ACTIVE PAGES #######
# HOME PAGE
@app.route("/")  # "/" means default page. In this case, the homepage.
@app.route("/home")
def home():
    if "id" in session:
        current_id = session["id"]
        current_email = Users.query.filter(Users.id == current_id).first()
        current_user = current_email.user
    return redirect(url_for("view"))
    # return render_template("home.html", user=current_user) #using render_template so that it renders the content ot the HTML and does no not affect URL


# LOG IN PAGE
@app.route("/login", methods=["POST", "GET"])
def login():
    if "id" in session:
        func.flash_red(
            "You are currently logged in. <a href=\"logout\">Sign out</a> to log in on another account.")
        return redirect(url_for("user"))

    if request.method == "POST":
        session.permanent = True  # enable/disable permanent session
        email = request.form["email"]
        password = request.form["password"]

        if (email == "") or (password == ""):
            func.flash_red("Please fill all entries.")
            return render_template("login.html", email=email, password=password)
        else:
            user = my_sql_get_one(
                f"SELECT * from {database_name}.{database_table_name} WHERE EMAIL = '{email}' AND PASSWORD = '{password}'")
            if user:
                # storing value of email in the dictionary.
                session["id"] = my_sql_get_one(
                    f"SELECT * from {database_name}.{database_table_name} WHERE EMAIL = '{email}' AND PASSWORD = '{password}'")[database_columns["ID"]]
                # current_ip_address = get("https://api.ipify.org").content.decode('utf8')
                # current_time = datetime.now()
                # regex_match = re.search(r'([0-9]{1,2}-[0-9]{1,2}-[0-9]{4}): ([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3});',
                #                         my_sql_get_one(f"SELECT * from {database_name}.{database_table_name} WHERE EMAIL = '{email}' AND PASSWORD = '{password}")[database_columns["IP"]])
                # If an audit of time and IP Address (for log in) exists
                # if regex_match is not None:
                #     date = regex_match[1]
                #     ip_address = regex_match[2]
                #     # if date and IP address of recent record matches with the current date and current IP address, no need to record.
                #     if date == f"{current_time.month}-{current_time.day}-{current_time.year}" and ip_address == current_ip_address:
                #         pass
                #     # Record time and IP Address if neither of them match.
                #     else:
                #         email_password_match.ip = f"{current_time.month}-{current_time.day}-{current_time.year}: {current_ip_address}" + ";" + email_password_match.ip
                #         db.session.commit()
                # # If the audit for the user login (time and IP address) is empty...
                # else:
                #     email_password_match.ip = f"{current_time.month}-{current_time.day}-{current_time.year}: {current_ip_address}"
                #     db.session.commit()
                func.flash_green("Logged in successfully!")
                return redirect(url_for("user"))
            else:
                func.flash_red(
                    "Username or password does not match in database. Please check your entries or <a href=\"signup\">sign up</a>.")
                return render_template("login.html", email=email, password=password)
    else:
        return render_template("login.html")


# CHANGE PASSWORD PAGE
@app.route("/change-password", methods=["POST", "GET"])
def change_password():
    return redirect(url_for("home"))
    current_user = None
    if "id" in session:
        id = session["id"]
        user_info = Users.query.filter(Users.id == id).first()
        current_user = user_info.user
        current_id = user_info.id

    if request.method == "POST":
        current_id = Users.query.filter(Users.id == id).first()
        current_password = current_id.password

        oldpass = request.form["oldpass"]
        newpassword = request.form["newpass"]
        renewpassword = request.form["renewpass"]

        # If either of the 3 inputs are blank...
        if (oldpass == "") or (newpassword == "") or (renewpassword == ""):
            flash(Markup("<img style=\"vertical-align: middle;\" src=\"static\pictures\Exclamation Point Icon.png\" height=\"18px\" width=\"18px\"/> <span style=\"color: red;\">Please fill all entries.</span>"))
            return render_template("change-password.html")

        # If the password typed in "oldpass" does not natch wit the current password in the database
        elif current_password != oldpass:
            flash(Markup("<img style=\"vertical-align: middle;\" src=\"static\pictures\Exclamation Point Icon.png\" height=\"18px\" width=\"18px\"/> <span style=\"color: red;\">Old Password does not match with account's current password. Enter correct current password.</span>"))
            return render_template("change-password.html")

        # If the input typed in the "newpass" and "renewpass" are not the same...
        else:
            if newpassword != renewpassword:
                flash(Markup("<img style=\"vertical-align: middle;\" src=\"static\pictures\Exclamation Point Icon.png\" height=\"18px\" width=\"18px\"/> <span style=\"color: red;\">New password and retyped new password do not match.</span>"))
                return render_template("change-password.html", user=current_user)
            else:
                user_info.password = newpassword
                db.session.commit()
                flash(Markup("<img style=\"vertical-align: middle;\" src=\"static\pictures\Checkmark Icon.png\" height=\"18px\" width=\"18px\"/> <span style=\"color: lime;\">Password successfully changed.</span>"))
                return redirect(url_for("logout"))
    else:
        return render_template("change-password.html", user=current_user)


def my_sql_post(sql_cmd):
    cursor = mysql.connection.cursor()
    cursor.execute(sql_cmd)
    mysql.connection.commit()
    cursor.close()


def my_sql_get_all(sql_cmd):
    cursor = mysql.connection.cursor()
    cursor.execute(sql_cmd)
    results = cursor.fetchall()
    cursor.close()
    return results


def my_sql_get_one(sql_cmd):
    cursor = mysql.connection.cursor()
    cursor.execute(sql_cmd)
    result = cursor.fetchone()
    cursor.close()
    return result


@app.route("/reset-password", methods=["POST", "GET"])
def reset_password():
    current_user = None
    print(request.referrer)
    if request.method == "POST":
        reset_decision = request.form["reset"]
        if reset_decision == "1":
            new_password = func.password_generator()
            sql_cmd = f"""UPDATE {database_name}.{database_table_name}
                        SET PASSWORD = '{new_password}'
                        WHERE ID = {session["id"]};
                        """
            my_sql_post(sql_cmd)

            # database_object.update_password(table_name=database_table_name, id=session["id"], password=new_password)
            del new_password
            # user_info = Users.query.filter(Users.id == session["id"]).first()
            # new_password = func.password_generator()
            # user_info.password = new_password
            # db.session.commit()
            sql_cmd = f"SELECT * from {database_name}.{database_table_name} WHERE ID = {session['id']};"
            print("Test:", my_sql_get_one(sql_cmd))
            func.send_password_email(
                "ryannguyen1029@gmail.com", my_sql_get_one(sql_cmd)[database_columns["PASSWORD"]])

            func.flash_green(
                "Password successfully changed. Password sent to email.")
            return redirect(url_for("logout"))
        elif reset_decision == "0":
            func.flash_red("Action canceled.")
            return redirect(url_for("user"))
        else:
            func.flash_red("Invalid input. No action was done.")
            return redirect(url_for("user"))

    if "id" in session:
        current_id = session["id"]

        user_info = Users.query.filter(Users.id == current_id).first()
        current_user = user_info.user
        return render_template("reset-password.html", user=current_user)
    else:
        func.flash_red("You must be logged into an account to reset password.")
    return redirect(url_for("login"))


# LOG OUT PAGE
@app.route("/logout")
def logout():
    if "id" in session:
        session.pop("id", None)
        func.flash_red("Successfully logged out.")
    return redirect(url_for("login"))

# VIEW PAGE - views the database (including password)


@app.route("/view", methods=["POST", "GET"])
def view():
    current_user = None
    if "id" in session:
        user_roles = func.dbroles_to_listroles(my_sql_get_one(
            f"SELECT ROLES from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
        is_admin = False
        for role in user_roles:
            if role in admin_roles:
                is_admin = True
                break
        if is_admin:
            if func.check_post("search"):
                search_text = request.form["search"]
                if search_text == "":
                    return render_template("view.html",
                                           user=my_sql_get_one(f"SELECT USERNAME from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                           values=my_sql_get_all(
                                               f"SELECT * from {database_name}.{database_table_name}"),
                                           search_text=None)
                else:
                    return render_template("view.html",
                                           user=my_sql_get_one(f"SELECT USERNAME from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                           values=my_sql_get_all(
                                               f"SELECT * from {database_name}.{database_table_name} WHERE USERNAME = '{search_text}' OR EMAIL = '{search_text}'"),
                                           search_text=search_text)
            if func.check_post("edit_user"):
                print("Test",request.form["edit_user"])
                session["user_to_edit_stack"] = [int(request.form["edit_user"])]
                return redirect(url_for("edit_user"))
            print("Test", my_sql_get_all(
                f"SELECT * from {database_name}.{database_table_name}"))
            return render_template("view.html",
                                   user=my_sql_get_one(
                                       f"SELECT USERNAME from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                   values=my_sql_get_all(f"SELECT * from {database_name}.{database_table_name}"))
        else:
            func.flash_red("You must be logged into an admin account.")
            return redirect(url_for("login"))
    else:
        func.flash_red("You must be logged into an admin account.")
        return redirect(url_for("login"))


@app.route("/edit-user", methods=["POST", "GET"])
def edit_user():
    if request.method == "POST":
        id = session["user_to_edit_stack"][0]
        session.pop("user_to_edit_stack", None)
        edit_user_info = {}
        edit_user_info_roles_checkboxes = {}
        editable_elements = []  # ["firstname", "lastname"]

        for element in editable_elements:
            edit_user_info[element] = request.form[element]

        for role in global_roles:
            is_checked = request.form.get(role)
            edit_user_info_roles_checkboxes[role] = True if is_checked else False

        pending_roles: str = ""
        for role in edit_user_info_roles_checkboxes:
            if role in global_roles and edit_user_info_roles_checkboxes[role] is True:
                pending_roles += role + ";"

        if id == session["id"]:
            user_info_original_roles = func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
            pending_roles += "{};".format(user_info_original_roles[-1])

        # Applying changes
        my_sql_post(f"""UPDATE {database_name}.{database_table_name}
                    SET FIRST_NAME = '{request.form["firstname"]}'
                    WHERE ID = {id};""")
        my_sql_post(f"""UPDATE {database_name}.{database_table_name}
                    SET FIRST_NAME = '{request.form["lastname"]}'
                    WHERE ID = {id};""")
        my_sql_post(f"""UPDATE {database_name}.{database_table_name}
                    SET ROLES = '{pending_roles}'
                    WHERE ID = {id};""")
        is_checked = request.form.get("active")
        if is_checked:
            my_sql_post(f""" UPDATE {database_name}.{database_table_name}
                        SET ACTIVE = 1
                        WHERE ID = {id};""")
        else:
            my_sql_post(f""" UPDATE {database_name}.{database_table_name}
                    SET ACTIVE = 0
                    WHERE ID = {id};""")
        func.flash_green(f"Successfully edited user #{id}!")
        return redirect(url_for("view"))

    if "id" in session:
        user_roles = func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
        for role in user_roles:
            if role in admin_roles:
                is_admin = True
                break
        if is_admin:
            try:
                if len(session["user_to_edit_stack"]) == 1:
                    edit_user_id = session["user_to_edit_stack"][0]
                    can_edit_roles = list()
                    for role in global_roles:
                        if len(user_roles) < 2:
                            can_edit_roles.append(role)
                            break
                        if role == user_roles[-1]:
                            break
                        else:
                            can_edit_roles.append(role)
                    return render_template("edit-user.html",
                                           user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                           id=my_sql_get_one(f"SELECT ID FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0],
                                           username=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0],
                                           email=my_sql_get_one(f"SELECT EMAIL FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0],
                                           firstname=my_sql_get_one(f"SELECT FIRST_NAME FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0],
                                           lastname=my_sql_get_one(f"SELECT LAST_NAME FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0],
                                           is_active=my_sql_get_one(f"SELECT ACTIVE FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0],
                                           roles=can_edit_roles,
                                           is_enabled_roles=func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0]))
            except KeyError:
                session.pop("user_to_edit_stack", None)
                func.flash_red("There was an error. Please try again.")
                return redirect(url_for("view"))
        else:
            func.flash_red("You must be logged into an admin account.")
            return redirect(url_for("login"))
    else:
        return redirect(url_for("view"))


@app.route("/add-user", methods=["POST", "GET"])
def add_user():
    if request.method == "POST":
        id = my_sql_get_one(f"SELECT COUNT(*) from {database_name}.{database_table_name}")[0] + 1

        username = request.form["username"]
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        email = request.form["email"]
        is_active_checkbox = request.form.get("active")
        is_active = True if is_active_checkbox else False
        if first_name == "" or last_name == "" or email == "":
            func.flash_red("Please fill all entries.")
            return render_template("add-user.html",
                                   user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                   next_id=id,
                                   username=username,
                                   first_name=first_name,
                                   last_name=last_name,
                                   email=email)
        else:
            check_email = my_sql_get_one(f"SELECT EMAIL FROM {database_name}.{database_table_name} WHERE EMAIL = '{email}'")
            check_username = my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE USERNAME = '{username}'")
            if check_email is not None and check_username is not None:
                func.flash_red(f"Email and username (Email: <i>{email}</i>, Username: <i>{username}</i>) already exist!")
                return render_template("add-user.html",
                                       user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                       next_id=id,
                                       username=username,
                                       first_name=first_name,
                                       last_name=last_name,
                                       email=email)
            elif check_email is not None:
                func.flash_red(f"Email (<i>{email}</i>) already exists!")
                return render_template("add-user.html",
                                       user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                       next_id=id,
                                       username=username,
                                       first_name=first_name,
                                       last_name=last_name,
                                       email=email)
            elif check_username is not None:
                func.flash_red(
                    f"Username (<i>{username}</i>) already exists!</span>")
                return render_template("add-user.html",
                                       user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                       next_id=id,
                                       username=username,
                                       first_name=first_name,
                                       last_name=last_name,
                                       email=email)
            else:
                password = func.password_generator()
                edit_user_info_roles_checkboxes = {}
                for role in global_roles:
                    is_checked = request.form.get(role)
                    edit_user_info_roles_checkboxes[role] = True if is_checked else False

                pending_roles: str = ""
                for role in edit_user_info_roles_checkboxes:
                    if role in global_roles and edit_user_info_roles_checkboxes[role] is True:
                        pending_roles += role + ";"
                my_sql_post(f"""INSERT INTO {database_name}.{database_table_name} (ID, USERNAME, EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, ROLES, IP, ACTIVE) VALUES
                        ({id}, "{username}", "{email}", "{first_name}", "{last_name}", "{password}", "user;", "", 0)""")
                
                # db.session.add(Users(username, email, first_name,
                #                last_name, password, "user", is_active))
                # db.session.commit()
                func.send_password_email(email, password)
                func.flash_red(f"Created user #{id} - <i>{email}</i>")
                return redirect(url_for("view"))

    if "id" in session:
        username = my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0]
        user_roles = func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
        next_id = int(my_sql_get_one(f"SELECT COUNT(*) FROM {database_name}.{database_table_name}")[0]) + 1
        for role in user_roles:
            if role in admin_roles:
                is_admin = True
                break
        if is_admin:
            can_edit_roles = list()
            for role in global_roles:
                if len(user_roles) < 2:
                    can_edit_roles.append(role)
                    break
                if role == user_roles[-1]:
                    break
                else:
                    can_edit_roles.append(role)
            return render_template("add-user.html",
                                   user=username,
                                   next_id=next_id,
                                   can_edit_roles=can_edit_roles)
        else:
            func.flash_red("You must be logged into a sysop account.")
            return redirect(url_for("user"))
    else:
        func.flash_red("You must be logged into an admin account.")
        return redirect(url_for("login"))

# USER PAGE


@app.route("/user")
def user():
    if "id" in session:  # checking if "id" in dictionary has a value
        user = my_sql_get_one(
            f"SELECT * from {database_name}.{database_table_name} WHERE ID = {session['id']}")
        return render_template("user.html",
                               user=user[database_columns["USERNAME"]],
                               email=user[database_columns["EMAIL"]],
                               id=user[database_columns["ID"]],
                               roles=user[database_columns["ROLES"]])
    else:
        return redirect(url_for("login"))


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error404.html'), 404


@app.route("/test")
def ryan():
    username = None
    if "id" in session:
        current_id = session["id"]
        user_info = Users.query.filter(Users.id == current_id).first()
        user_id = user_info.id
        username = user_info.user
        user_roles = user_info.roles
        # flashcard_all = Flashcards.query.filter(Flashcards.user_id == current_id).all()
        # print(Flashcards.user_id)
    return redirect(url_for("home"))
    # return render_template("test.html", user=username)


####### INACTIVE PAGES - redirects to "home.html" #######
@app.route("/purpose")
def page():
    return redirect(url_for("home"))


# Run Program
if __name__ == "__main__":
    with app.app_context():
        database_object.connect_database(
            password=database_pass, database_name=database_name)
        # # # database_object.create_non_existing_database(database_pass, database_name)
        database_object.create_table(database_table_name)
        # # database_object.show_all_databases()
        database_object.insert_into_table(table_name=database_table_name,
                                          id=1,
                                          username="ryannguyen1029",
                                          email="ryannguyen10292",
                                          first_name="Ryan",
                                          last_name="Nguyen",
                                          password="Test123",
                                          roles="user;sysop;")
        database_object.update_active_status(database_table_name, 1, True)
        # database_object.show_tables_from_database()
        columns = database_object.show_all_columns(
            database_name, database_table_name)
        print("columns", columns)
        for index, column_info in enumerate(columns):
            database_columns[column_info[0]] = index
        # print("database_columns", database_columns)
        database_object.show_contents_from_table(database_table_name)
        database_object.disconnect_database()
        app.run(debug=True, port=80)

    # with app.app_context():
    #     # db.create_all() # creates database - must be before app.run()
    #     found_email = Users.query.filter_by(email="sysop@sus.com").first()
    #     if not found_email:
    #         password = func.password_generator()
    #         # user, email, firstname, lastname, password, roles, ip, active
    #         identification = Users(
    #             "Sysop", "sysop@sus.com", "Test1", "Lol", password, "user;sysop;root;")
    #         db.session.add(identification)
    #         func.send_password_email("sysop@sus.com", password)
    #         print("Password:", password)
    #         identification = Users(
    #             "Sysop", "sys@sus.com", "Test2", "Lmao", password, "user;sysop;")
    #         db.session.add(identification)
    #         db.session.commit()
    #     # runs program. Every time you save any file, the new version will run.
    #     app.run(debug=True)
