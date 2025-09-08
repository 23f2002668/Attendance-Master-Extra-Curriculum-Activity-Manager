import random
from flask_cors import CORS
from flask import Flask, render_template, session, redirect, url_for, jsonify, flash, request, Response, send_file, current_app # current_app for sending pdf in email
from flask_login import login_required, LoginManager
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import os, subprocess, random, time, sqlite3, json, numpy as np, matplotlib, matplotlib.pyplot as plt; matplotlib.use('Agg')
from string import ascii_letters
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from threading import Thread
from reportlab.lib import pdfencrypt, colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT, TA_LEFT

# Object for Flask Application
app=Flask(__name__)

# Enabling CORS Globally
CORS(app)

# Secret Key for Flask Application
app.secret_key="x34Er5TTHD6789#D67fgxeuo9@djngkcl%*9#D67fgxeuo9@djngkcl%dbT356"

# Sqlite Database File for Attendance Master Application
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///AttendanceMaster.sqlite3"

# Enable Sqlalchemy to Track Changes/Modifications to Object
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# Initialising Sqlalchemy
db = SQLAlchemy(app)

con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
cur = con.cursor()
email = input()
p = "foo"

try :
    query = f"SELECT * FROM UserDetails WHERE Email = '{email}' AND password = '{p}'"
    res = cur.execute(query)
    res = res.fetchone()
    print(res)
    con.close()
except:
    print("Something went wrong !")

if __name__ == "__main__":
    app.run(debug=True)