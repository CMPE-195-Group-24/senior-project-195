from flask import Flask, redirect, url_for, send_from_directory, render_template, request, session, flash, Markup
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

def send_password_email(email, password):
    # set your email and password
    # Use App Password, not your real password (https://support.google.com/accounts/answer/185833?hl=en)
    from_email_address = "ryannguyen1029@gmail.com"
    from_email_password = "elovctfqiozaejoi"

    # create email
    msg = EmailMessage()
    msg['From'] = from_email_address
    msg['To'] = "ryannguyen1029@gmail.com"
    # msg['CC'] = "ryannguyen1029@gmail.com"
    msg['Subject'] = "Test Notice - Password Generated"
    message = f"""
    This is a test email message from Wo-Tak Reader! Attached is the generated password for email {email}.
    Email: {email}
    Password: {password}
    
    Go to http://127.0.0.1:5000/login
    """
    msg.set_content(message)

    # send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email_address, from_email_password)
        smtp.send_message(msg)

def password_generator():
    length = 20
    password: str = ""
    lower_letters = string.ascii_lowercase
    upper_letters = string.ascii_uppercase
    numbers = string.digits
    symbols = string.punctuation

    all = lower_letters + upper_letters + numbers + symbols

    while True:
        password: str = ""
        for _ in range(length):
            password += "".join(secrets.choice(all))
        if (any(char in lower_letters for char in password) and
            any(char in upper_letters for char in password) and
            sum(char in symbols for char in password) > 2 and
            sum(char in numbers for char in password) > 2):
            break
    return password

def dbroles_to_listroles(roles: str) -> list:
    list_roles = roles.split(";")[:-1]
    return list_roles

def check_post(element_name: str) -> bool:
    if request.method == "POST":
        for form_request in request.form:
            if element_name in form_request:
                return True
    return False

def flash_red(html_message: str):
    return flash(Markup(f"<img style=\"vertical-align: middle;\" src=\"static\pictures\Exclamation Point Icon.png\" height=\"18px\" width=\"18px\"/> <span style=\"color: red;\">{html_message}</span>"))

def flash_green(html_message: str):
    return flash(Markup(f"<img style=\"vertical-align: middle;\" src=\"static\pictures\Checkmark Icon.png\" height=\"18px\" width=\"18px\"/> <span style=\"color: lime;\">{html_message}</span>"))