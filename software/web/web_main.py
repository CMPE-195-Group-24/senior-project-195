####### IMPORTS #######
from flask import Flask, redirect, url_for, send_from_directory, render_template, request, session, flash
from markupsafe import Markup
from flask_mysqldb import MySQL
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
import uuid
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
app.secret_key = "Test"  # Make key complicated at one point

database_info = func.database_info("./software/web/database_config.yaml")

database_name = database_info['database']['database_name']
database_table_name = database_info['database_tables']['personnels']
database_audit_table = database_info['database_tables']['audit']['database']
audit_access_log = database_info['database_tables']['audit']['access_history']
database_pass = database_info['database']['password']

app.config['MYSQL_HOST'] = database_info['database']['host']
app.config['MYSQL_USER'] = database_info['database']['user']
app.config['MYSQL_PASSWORD'] = database_pass
app.config['MYSQL_DB'] = database_name
mysql = MySQL(app)

database_columns = {'ID': 0, 'USERNAME': 1, 'EMAIL': 2, 'FIRST_NAME': 3, 'LAST_NAME': 4, 'PASSWORD': 5, 'ROLES': 6, 'EVER_ADMIN': 7, 'ACTIVE': 8}

database_object = dbsql.Database(user="root",
                                 host="senior-project.cqpzjknbrdd2.us-west-2.rds.amazonaws.com",
                                 database_name=database_name)

# db = SQLAlchemy(app)
global_roles = ["user", "sysop", "root"]
admin_roles = global_roles[1:]


####### ACTIVE PAGES #######
# HOME PAGE
@app.route("/")  # "/" means default page. In this case, the homepage.
@app.route("/home")
def home():
    return redirect(url_for("view"))


# LOG IN PAGE
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True  # enable/disable permanent session
        email = request.form["email"]
        password = request.form["password"]

        if (email == "") or (password == ""):
            func.flash_red("Please fill all entries.")
            return render_template("login.html", email=email, password=password)
        else:
            user = my_sql_get_one(f"SELECT * from {database_name}.{database_table_name} WHERE EMAIL = '{email}' AND PASSWORD = '{password}'")
            if user is not None:
                user_roles = my_sql_get_one(f"SELECT ROLES from {database_name}.{database_table_name} WHERE EMAIL = '{email}' AND PASSWORD = '{password}'")[0]
                if any(role in user_roles for role in global_roles):
                    # storing value of email in the dictionary.
                    session["id"] = my_sql_get_one(
                        f"SELECT ID from {database_name}.{database_table_name} WHERE EMAIL = '{email}' AND PASSWORD = '{password}'")[0]
                    func.flash_green("Logged in successfully!")
                    return redirect(url_for("user"))
                else:
                    func.flash_red("User does not exist or password is incorrect. Please check your entries or <a href=\"signup\">sign up</a>.")
                    return render_template("login.html", email=email, password=password)
            else:
                func.flash_red("User does not exist or password is incorrect. Please check your entries or <a href=\"signup\">sign up</a>.")
                return render_template("login.html", email=email, password=password)
    
    if "id" in session:
        func.flash_red("You are currently logged in. <a href=\"logout\">Sign out</a> to log in on another account.")
        return redirect(url_for("user"))
    else:
        return render_template("login.html")


# CHANGE PASSWORD PAGE
@app.route("/change-password", methods=["POST", "GET"])
def change_password():    
    if "id" in session:
        current_user = my_sql_get_one(f"SELECT USERNAME from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0]
        if request.method == "POST":
            current_password = my_sql_get_one(f"SELECT PASSWORD from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0]
            oldpass = request.form["oldpass"]
            newpassword = request.form["newpass"]
            renewpassword = request.form["renewpass"]

            # If either of the 3 inputs are blank...
            if (oldpass == "") or (newpassword == "") or (renewpassword == ""):
                func.flash_red("Please fill all entries.")
                return render_template("change-password.html",
                                       user=current_user)

            # If the password typed in "oldpass" does not match with the current password in the database
            elif current_password != oldpass:
                func.flash_red("Old Password does not match with account's current password. Enter correct current password.")
                return render_template("change-password.html",
                                       user=current_user)

            # If the input typed in the "newpass" and "renewpass" are not the same...
            else:
                if newpassword != renewpassword:
                    func.flash_red("New password and retyped new password do not match.")
                    return render_template("change-password.html",
                                           user=current_user)
                else:
                    if func.password_change_check(newpassword)[0] is True:
                        my_sql_post(f"""UPDATE {database_name}.{database_table_name}
                                SET PASSWORD = '{newpassword}'
                                WHERE ID = {session['id']};""")
                        func.flash_green("Password successfully changed.")
                        return redirect(url_for("logout"))
                    else:
                        func.flash_red("Old Password does not match with account's current password. Enter correct current password.")
                        return render_template("change-password.html",
                                               user=current_user)
        else:
            return render_template("change-password.html",
                                user=my_sql_get_one(f"SELECT USERNAME from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
    else:
        return redirect(url_for("logout"))

def log_post(sql_cmd):
    print('sql_cmd:', sql_cmd)
    update_inspect = re.search(r"(UPDATE)[\s|\S|\n]+SET ([A-Za-z0-9_]+) = (\'?.*\'?)(?:[\s|\S|\n]+WHERE ID = ([0-9]+))?", sql_cmd)
    delete_inspect = re.search(r"(DELETE) FROM[\s|\S|\n]+WHERE ID = ([0-9]+)", sql_cmd)
    insert_inspect = re.search(r"(INSERT).*\((.*)\)[\s|\S|\n]+\((.*)\)", sql_cmd)
    if update_inspect is not None:
        post_action = update_inspect[1]
        column_name = update_inspect[2]
        new_content = update_inspect[3]
        user_id = update_inspect[4]
        old_content = my_sql_get_one(f"SELECT {column_name} FROM {database_name}.{database_table_name} WHERE ID = {user_id}")[0]
        log_database_audit(post_action, user_id, column_name, new_content, old_content)
    if delete_inspect is not None:
        post_action = delete_inspect[1]
        user_id = delete_inspect[2]
        log_database_audit(post_action, user_id, "", "")
    if insert_inspect is not None:
        user_id = int(my_sql_get_one(f"SELECT MAX(ID) from {database_name}.{database_table_name}")[0]) + 1
        post_action = insert_inspect[1]
        columns = insert_inspect[2].split(", ")
        new_data = insert_inspect[3].split(", ")
        log_database_audit(post_action, user_id, columns, new_data)

def log_database_audit(post_action, user_id, column_name, new_content, old_content=""):
    cursor = mysql.connection.cursor()
    # For adding new user (INSERT)
    timestamp = func.get_current_time_iso().split('.')[0] + "Z"
    if type(column_name) is list and type(new_content) is list:
        match_columns = {}
        sql_cmd = f"""INSERT INTO {database_name}.{database_audit_table} (TIMESTAMP, ACTION, USER_ID, COLUMN_NAME, OLD_CONTENT, NEW_CONTENT, PERFORMED_BY_USER_ID) VALUES
                    ("{timestamp}", "{post_action}", {user_id}, "", "", "", {session['id']})"""
        cursor.execute(sql_cmd)
        mysql.connection.commit()
        for i in range(len(column_name)):
            if column_name[i] == "PASSWORD":
                match_columns[column_name[i]] = "[redacted]"
            else:
                match_columns[column_name[i]] = new_content[i]
        for column, new_content in match_columns.items():
            current_content = my_sql_get_one(f"SELECT NEW_CONTENT FROM {database_name}.{database_audit_table} WHERE USER_ID = {user_id} AND TIMESTAMP = '{timestamp}'")[0]
            current_content += f"{column}: {new_content}\\n"
            sql_cmd = f"""UPDATE {database_name}.{database_audit_table}
                            SET NEW_CONTENT = '{current_content}'
                            WHERE USER_ID = {user_id} AND TIMESTAMP = '{timestamp}';
                            """
            cursor.execute(sql_cmd)
            mysql.connection.commit()
        cursor.close()
    # For updating or removing user (UPDATE or DELETE)
    else:
        sql_cmd = ""
        if column_name == "PASSWORD":
            sql_cmd = f"""INSERT INTO {database_name}.{database_audit_table} (TIMESTAMP, ACTION, USER_ID, COLUMN_NAME, OLD_CONTENT, NEW_CONTENT, PERFORMED_BY_USER_ID) VALUES
                    ("{timestamp}", "{post_action}", {user_id}, "{column_name}", "[redacted]", "[redacted]", {session['id']})"""
        else:
            sql_cmd = f"""INSERT INTO {database_name}.{database_audit_table} (TIMESTAMP, ACTION, USER_ID, COLUMN_NAME, OLD_CONTENT, NEW_CONTENT, PERFORMED_BY_USER_ID) VALUES
                        ("{timestamp}", "{post_action}", {user_id}, "{column_name}", "{old_content}", "{new_content}", {session['id']})"""
        cursor.execute(sql_cmd)
        mysql.connection.commit()
        cursor.close()

@app.route("/remove-user", methods=["POST", "GET"])
def remove_user():
    if request.method == "POST":
        reset_decision = request.form["remove_user"]
        user_remove_id = session.pop("user_to_remove", None)[0]
        print('user_remove_id', user_remove_id)
        if reset_decision == "1":
            my_sql_post(f"DELETE FROM {database_name}.{database_table_name} WHERE ID = {user_remove_id}")
            func.flash_green(f"Successfully removed User ID #{user_remove_id}")
        elif reset_decision == "0":
            func.flash_red(f"Action canceled. User #{user_remove_id} not removed.")
        else:
            func.flash_red("Invalid input. No action was done.")
        return redirect(url_for("view"))

    if "id" in session:
        if 'user_to_remove' in session:
            return render_template("remove-user.html",
                                user=my_sql_get_one(f"SELECT USERNAME from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                user_to_delete=my_sql_get_one(f"SELECT * from {database_name}.{database_table_name} WHERE ID = {session['user_to_remove'][0]}"))
        else:
            func.flash_red("No user was selected to be deleted.")
            return redirect(url_for("view"))
    else:
        func.flash_red("You must be logged into an account to reset password.")
        return redirect(url_for("logout"))
            

@app.route("/reset-password", methods=["POST", "GET"])
def reset_password():
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
            del new_password
            
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
        return render_template("reset-password.html",
                               user=my_sql_get_one(f"SELECT USERNAME from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
    else:
        func.flash_red("You must be logged into an account to reset password.")
        return redirect(url_for("logout"))


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
    if "id" in session:
        user_roles = func.dbroles_to_listroles(my_sql_get_one(
            f"SELECT ROLES from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
        print("user_roles", user_roles)
        if len(user_roles) > 0:
            if any(role in admin_roles for role in user_roles):
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
                    session["user_to_edit_stack"] = [int(request.form["edit_user"])]
                    return redirect(url_for("edit_user"))
                if func.check_post("remove_user"):
                    session["user_to_remove"] = [int(request.form["remove_user"])]
                    print('session["user_to_remove"]', session["user_to_remove"])
                    return redirect(url_for("remove_user"))
                    
                return render_template("view.html",
                                        user=my_sql_get_one(f"SELECT USERNAME from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                        is_root="root" in my_sql_get_one(f"SELECT ROLES from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                        values=my_sql_get_all(f"SELECT * from {database_name}.{database_table_name}"))
            else:
                func.flash_red("You must be logged into an admin account.")
                return redirect(url_for("user"))
        else:
            return redirect(url_for("logout"))
    else:
        func.flash_red("You must be logged into an admin account.")
        return redirect(url_for("login"))


@app.route("/edit-user", methods=["POST", "GET"])
def edit_user():    
    if request.method == "POST":
        id = session["user_to_edit_stack"][0]
        session.pop("user_to_edit_stack", None)
        
        if func.check_post("assign_new_uuid"):
            my_sql_post(f"""UPDATE {database_name}.{database_table_name}
                        SET UUID = '{str(uuid.uuid4()).replace("-", "")}'
                        WHERE ID = {id};""")
            func.flash_green(f"Assigned new UUID to user #{id}!")
        elif func.check_post("remove_uuid"):
            my_sql_post(f""" UPDATE {database_name}.{database_table_name}
                            SET UUID = ''
                            WHERE ID = {id};""")
            my_sql_post(f""" UPDATE {database_name}.{database_table_name}
                        SET ACTIVE = 0
                        WHERE ID = {id};""")
            func.flash_green(f"Removed UUID to user #{id}.")
        else:
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
            current_first_name = my_sql_get_one(f"SELECT FIRST_NAME FROM {database_name}.{database_table_name} WHERE ID = {id}")[0]
            current_last_name = my_sql_get_one(f"SELECT LAST_NAME FROM {database_name}.{database_table_name} WHERE ID = {id}")[0]
            current_roles = my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {id}")[0]
            current_active = my_sql_get_one(f"SELECT ACTIVE FROM {database_name}.{database_table_name} WHERE ID = {id}")[0]
            if request.form["firstname"] != current_first_name:
                my_sql_post(f"""UPDATE {database_name}.{database_table_name}
                            SET FIRST_NAME = '{request.form["firstname"]}'
                            WHERE ID = {id};""")
            if request.form["lastname"] != current_last_name:
                my_sql_post(f"""UPDATE {database_name}.{database_table_name}
                            SET LAST_NAME = '{request.form["lastname"]}'
                            WHERE ID = {id};""")
            if pending_roles != current_roles:
                my_sql_post(f"""UPDATE {database_name}.{database_table_name}
                            SET ROLES = '{pending_roles}'
                            WHERE ID = {id};""")
                ever_admin = my_sql_get_one(f"SELECT EVER_ADMIN FROM {database_name}.{database_table_name} WHERE ID = {id}")[0]
                if (ever_admin == 0) and ("sysop" in pending_roles or "root" in pending_roles):
                    my_sql_post(f""" UPDATE {database_name}.{database_table_name}
                                SET EVER_ADMIN = 1
                                WHERE ID = {id};""")
            is_checked = request.form.get("active")
            if is_checked and not bool(current_active):
                uuid_str = my_sql_get_one(f"SELECT UUID FROM {database_name}.{database_table_name} WHERE ID = {id}")[0]
                if uuid_str == "":
                    my_sql_post(f""" UPDATE {database_name}.{database_table_name}
                                SET UUID = '{str(uuid.uuid4()).replace("-", "")}'
                                WHERE ID = {id};""")
                my_sql_post(f""" UPDATE {database_name}.{database_table_name}
                            SET ACTIVE = 1
                            WHERE ID = {id};""")
            elif not is_checked and bool(current_active):
                my_sql_post(f""" UPDATE {database_name}.{database_table_name}
                        SET ACTIVE = 0
                        WHERE ID = {id};""")
            func.flash_green(f"Successfully edited user #{id}!")
        return redirect(url_for("view"))

    if "id" in session:
        user_roles = func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
        if len(user_roles) > 0:
            if any(role in admin_roles for role in user_roles):
                try:
                    if len(session["user_to_edit_stack"]) == 1:
                        edit_user_id = session["user_to_edit_stack"][0]
                        print("edit_user_id", edit_user_id)
                        can_edit_roles = list()
                        highest_user_role = user_roles[-1]
                        for role in global_roles[:global_roles.index(highest_user_role)]:
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
                                            is_enabled_roles=func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0]),
                                            ever_admin=my_sql_get_one(f"SELECT EVER_ADMIN FROM {database_name}.{database_table_name} WHERE ID = {edit_user_id}")[0])
                except KeyError as e:
                    session.pop("user_to_edit_stack", None)
                    func.flash_red(f"There was an error. Please try again.")
                    return redirect(url_for("view"))
            else:
                func.flash_red("You must be logged into an admin account.")
                return redirect(url_for("login"))
        else:
            return redirect(url_for("logout"))
    else:
        return redirect(url_for("view"))


@app.route("/add-user", methods=["POST", "GET"])
def add_user():
    if request.method == "POST":
        id = my_sql_get_one(f"SELECT MAX(ID) from {database_name}.{database_table_name}")[0] + 1

        username = request.form["username"]
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        email = request.form["email"]
        is_active_checkbox = request.form.get("active")
        is_active = True if is_active_checkbox else False
        
        user_roles = func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
        can_edit_roles = list()
        highest_user_role = user_roles[-1]
        for role in global_roles[:global_roles.index(highest_user_role)]:
            can_edit_roles.append(role)
        
        if first_name == "" or last_name == "" or email == "":
            func.flash_red("Please fill all entries.")
            return render_template("add-user.html",
                                   user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                   next_id=id,
                                   username=username,
                                   first_name=first_name,
                                   last_name=last_name,
                                   email=email,
                                   can_edit_roles=can_edit_roles)
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
                                       email=email,
                                       can_edit_roles=can_edit_roles)
            elif check_email is not None:
                func.flash_red(f"Email (<i>{email}</i>) already exists!")
                return render_template("add-user.html",
                                       user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                       next_id=id,
                                       username=username,
                                       first_name=first_name,
                                       last_name=last_name,
                                       email=email,
                                       roles=can_edit_roles)
            elif check_username is not None:
                func.flash_red(
                    f"Username (<i>{username}</i>) already exists!</span>")
                return render_template("add-user.html",
                                       user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                       next_id=id,
                                       username=username,
                                       first_name=first_name,
                                       last_name=last_name,
                                       email=email,
                                       can_edit_roles=can_edit_roles)
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
                if is_active is True:
                    my_sql_post(f"""INSERT INTO {database_name}.{database_table_name} (ID, USERNAME, EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, ROLES, EVER_ADMIN, ACTIVE, UUID) VALUES
                            ({id}, "{username}", "{email}", "{first_name}", "{last_name}", "{password}", "{pending_roles}", {1 if "sysop" in pending_roles or "root" in pending_roles else 0}, 1, "{str(uuid.uuid4()).replace("-", "")}")""")
                else:
                    my_sql_post(f"""INSERT INTO {database_name}.{database_table_name} (ID, USERNAME, EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, ROLES, EVER_ADMIN, ACTIVE, UUID) VALUES
                            ({id}, "{username}", "{email}", "{first_name}", "{last_name}", "{password}", "{pending_roles}", {1 if "sysop" in pending_roles or "root" in pending_roles else 0}, 0, '')""")
                func.send_password_email(email, password)
                del password
                
                func.flash_green(f"Created user #{id} - <i>{email}</i>")
                return redirect(url_for("view"))

    if "id" in session:
        username = my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0]
        user_roles = func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
        next_id = int(my_sql_get_one(f"SELECT MAX(ID) FROM {database_name}.{database_table_name}")[0]) + 1
        
        if len(user_roles) > 0:
            if any(role in admin_roles for role in user_roles):
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
            return redirect(url_for("logout"))
    else:
        func.flash_red("You must be logged into an admin account.")
        return redirect(url_for("login"))

# USER PAGE
@app.route("/user")
def user():
    if "id" in session:  # checking if "id" in dictionary has a value
        user_roles = func.dbroles_to_listroles(my_sql_get_one(f"SELECT ROLES FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
        if len(user_roles) > 0:
            user = my_sql_get_one(
                f"SELECT * from {database_name}.{database_table_name} WHERE ID = {session['id']}")
            return render_template("user.html",
                                first_name=user[database_columns["FIRST_NAME"]],
                                last_name=user[database_columns["LAST_NAME"]],
                                user=user[database_columns["USERNAME"]],
                                email=user[database_columns["EMAIL"]],
                                id=user[database_columns["ID"]],
                                roles=user[database_columns["ROLES"]])
        else:
            return redirect(url_for("logout"))
    else:
        return redirect(url_for("login"))

@app.route("/audit-access", methods=["POST", "GET"])
def audit_log_access():
    user_roles = func.dbroles_to_listroles(my_sql_get_one(
            f"SELECT ROLES from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
    if "id" in session:
        if len(user_roles) > 0:
            if any(role in admin_roles for role in user_roles):
                return render_template("audit-access.html",
                                        user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                        audit_log=my_sql_get_all(f"SELECT * FROM {database_name}.{audit_access_log} ORDER BY TIMESTAMP DESC"))
            else:
                func.flash_red("You must be logged into an admin account.")
                return redirect(url_for("login"))
        else:
            return redirect(url_for("logout"))
    else:
        return redirect(url_for("login"))

@app.route("/audit-database", methods=["POST", "GET"])
def audit_log_database():
    user_roles = func.dbroles_to_listroles(my_sql_get_one(
            f"SELECT ROLES from {database_name}.{database_table_name} WHERE ID = {session['id']}")[0])
    if "id" in session:
        if len(user_roles) > 0:
            if any(role in admin_roles for role in user_roles):
                return render_template("audit-database.html",
                                        user=my_sql_get_one(f"SELECT USERNAME FROM {database_name}.{database_table_name} WHERE ID = {session['id']}")[0],
                                        audit_log=my_sql_get_all(f"SELECT * FROM {database_name}.{database_audit_table} ORDER BY TIMESTAMP DESC"))
            else:
                func.flash_red("You must be logged into an admin account.")
                return redirect(url_for("login"))
        else:
            return redirect(url_for("logout"))
    else:
        return redirect(url_for("login"))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error404.html'), 404


####### INACTIVE PAGES - redirects to "home.html" #######
@app.route("/purpose")
def page():
    return redirect(url_for("home"))


def my_sql_post(sql_cmd):
    cursor = mysql.connection.cursor()
    log_post(sql_cmd)
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


# Run Program
if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True, port=5000)
