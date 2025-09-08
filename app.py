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

# Defining Database Tables

class UserDetails(db.Model):
    # It is used to naming table 'UserDetails' as by default it names the table 'user_details'
    __tablename__ = "UserDetails"  # Using __table_args__ for Dynamic Table Names
    SrNo = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Type = db.Column(db.String(20))
    Name = db.Column(db.String(50))
    FatherName = db.Column(db.String(50))
    MotherName = db.Column(db.String(50))
    Gender = db.Column(db.String(30))
    DOB = db.Column(db.String(10))
    Course = db.Column(db.String(50))
    Department = db.Column(db.String(50))
    Year = db.Column(db.String(20))
    Semester = db.Column(db.String(20))
    Section = db.Column(db.String(20))
    RollNo = db.Column(db.String(20))
    Mobile = db.Column(db.String(15), unique=True)
    Email = db.Column(db.String(50), unique=True)
    Password = db.Column(db.String(100))
    Date = db.Column(db.String(10))
    Day = db.Column(db.String(10))
    Time = db.Column(db.String(10))

class AttendanceDetails(db.Model):
    # It is used to naming table 'UserDetails' as by default it names the table 'user_details'
    __tablename__ = "AttendanceDetails"  # Using __table_args__ for Dynamic Table Names
    SrNo = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Name = db.Column(db.String(50))
    Course = db.Column(db.String(50))
    Department = db.Column(db.String(50))
    Year = db.Column(db.String(20))
    Semester = db.Column(db.String(20))
    Section = db.Column(db.String(20))
    Subject = db.Column(db.String(100))
    RollNo = db.Column(db.String(20))
    Date = db.Column(db.String(20))
    Time = db.Column(db.String(20))
    SubmittedAttendance = db.Column(db.String(20))
    Action = db.Column(db.String(20))
    Attendance = db.Column(db.String(20))

class Alerts(db.Model):
    # It is used to naming table 'UserDetails' as by default it names the table 'user_details'
    __tablename__ = "Alerts"  # Using __table_args__ for Dynamic Table Names
    SrNo = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Subject = db.Column(db.String(200))
    Content = db.Column(db.String(5000))
    Course = db.Column(db.String(50))
    Department = db.Column(db.String(50))
    Year = db.Column(db.Integer)
    Semester = db.Column(db.Integer)
    Section = db.Column(db.String(20))
    Sender = db.Column(db.String(50))
    Receiver = db.Column(db.String(1000000))
    Date = db.Column(db.String(20))

# Creating Defined Tables
@app.before_request
def createTable():
    db.create_all()

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Mail Provider
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '23f2002668@ds.study.iitm.ac.in'
app.config['MAIL_PASSWORD'] = 'eodq jcco gpjg vohz'  # Gmail App Password
mail = Mail(app)




# ************************************************************* Basic Functions For All Users **************************************************************************




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user_type")
def user_type():
    return render_template("userType.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = str(request.form["email"])
        password = str(request.form["password"])
        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()

        try :
            query = """SELECT Type, Name, FatherName, MotherName, Gender, DOB, Course, Department, Year, Semester, Section, RollNo, Mobile, Email, Password FROM UserDetails WHERE Email = ?"""
            res = cur.execute(query, (email, ))
            res = res.fetchone()
            con.close()

            if res is None:
                return "Incorrect Username / Email"

            hashed_password = res[14]

            if check_password_hash(hashed_password, password):

                session["Type"] = res[0]
                session["Name"] = res[1]
                session["FatherName"] = res[2]
                session["MotherName"] = res[3]
                session["Gender"] = res[4]
                session["DOB"] = res[5]
                session["Course"] = res[6]
                session["Department"] = res[7]
                session["Year"] = res[8]
                session["Semester"] = res[9]
                session["Section"] = res[10]
                session["RollNo"] = res[11]
                session["Mobile"] = res[12]
                session["Email"] = res[13]
                session["Day"] = datetime.now().strftime('%A')

                if session["Type"] == "Admin":
                    return student_dashboard()
                elif session["Type"] == "Teacher":
                    return teacher_dashboard()
                else:
                    return student_dashboard()
            else:
                return "Incorrect Password"
        except :
            return "Incorrect Username / Email"

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgotPassword.html")
    else:
        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()
        if request.is_json:
            data = request.get_json()
            email = data.get("Email")
            email = email.lower()
            try :
                query = """SELECT Name FROM UserDetails WHERE Email = ?"""
                res = cur.execute(query, (email, ))
                res = res.fetchone()
                con.close()

                if res is None:
                    return jsonify({"Message" : "Incorrect Email ! \nNo record found corresponding to your Email-ID."}), 200
                else:
                    session["Email"] = email
                    otp = send_otp(email)
                    return jsonify({"Message" : "OTP sent successfully !"}), 200
            except Exception as e:
                return jsonify({"Message" : "Incorrect Email ! \nNo record found corresponding to your Email-ID."}), 200
        else:
            user_otp = request.form.get("otp")
            otp = session.get("OTP")
            if otp == user_otp:
                query = """SELECT Type, Name, FatherName, MotherName, Gender, DOB, Course, Department, Year, Semester, Section, RollNo, Mobile, Email, Password FROM UserDetails WHERE Email = ?"""
                res = cur.execute(query, (session["Email"], ))
                res = res.fetchone()
                con.close()
                session["Type"] = res[0]
                session["Name"] = res[1]
                session["FatherName"] = res[2]
                session["MotherName"] = res[3]
                session["Gender"] = res[4]
                session["DOB"] = res[5]
                session["Course"] = res[6]
                session["Department"] = res[7]
                session["Year"] = res[8]
                session["Semester"] = res[9]
                session["Section"] = res[10]
                session["RollNo"] = res[11]
                session["Mobile"] = res[12]
                session["Email"] = res[13]
                session["Day"] = datetime.now().strftime('%A')

                if session["Type"] == "Admin":
                    return student_dashboard()
                elif session["Type"] == "Teacher":
                    return teacher_dashboard()
                else:
                    return student_dashboard()
                return jsonify({"Message" : "Your OTP has been verified successfully !"}), 200
            else:
                return jsonify({"Message" : "Your OTP has not been verified !"}), 200

def send_otp(user_email):
    msg = Message('Your OTP Code For Reseting Password',
                  sender='23f2002668@ds.study.iitm.ac.in',
                  recipients=[user_email])
    otp = ""
    num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    alp = list(ascii_letters)
    l = num+alp
    random.shuffle(l)
    l = random.choices(l, k=8)
    for i in l:
        otp += i
    session["OTP"] = otp
    msg.body = f"Your OTP for reseting password is {otp} !"
    mail.send(msg)
    flash('OTP sent to your email.')
    return otp

def attendance_email(roll):

    con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
    cur = con.cursor()

    query1 = """SELECT Name, FatherName, MotherName, Gender, DOB, Course, Department, Year, Semester, Section, RollNo, Mobile, Email FROM UserDetails WHERE RollNo==?"""
    res = cur.execute(query1, (roll, ))
    data = res.fetchone()

    query2 = """SELECT Name FROM UserDetails WHERE Type=?"""
    res = cur.execute(query2, ("Admin", ))
    admin = res.fetchone()[0]

    query3 = """SELECT Subject, SubmittedAttendance FROM AttendanceDetails WHERE RollNo = ?"""

    cur.execute(query3, (roll, ))
    data1 = cur.fetchall()
    max_att = len(data1)
    con.close()

    total = 0
    for i in data1:
        if i[1] == "Present":
            total += 1

    d = {}
    file = f"{data[5]} - {data[6]} - {data[7]} - {data[8]} - {data[9]}.json"
    with open(f"jsonFiles/{file}") as f:
        d = json.load(f)
    r, data2 = [], []

    current_day = datetime.now().strftime('%A')

    for i in d:
        if i == current_day:
            r = d[i]

    subjectsAttendance = {}  # {Subject : [TotalSubjectAttendance, Present, Absent, Late, Leave]}
    for i in r:
        if i[0] != "Interval":
            data2.append(i)
            subjectsAttendance[i[0]] = [0, 0, 0, 0, 0]

    for i in data1:
        subjectsAttendance[i[0]][0] += 1
        if i[1] == "Present":
            subjectsAttendance[i[0]][1] += 1
        elif i[1] == "Absent":
            subjectsAttendance[i[0]][2] += 1
        elif i[1] == "Late":
            subjectsAttendance[i[0]][3] += 1
        elif i[1] == "Leave":
            subjectsAttendance[i[0]][4] += 1
        else:
            subjectsAttendance[i[0]][2] += 1

    attendance = {}

    for i in subjectsAttendance:
        if subjectsAttendance[i][0] != 0:
            a = round((subjectsAttendance[i][1] * 100 / subjectsAttendance[i][0]), 3)
            if (a < 75):
                attendance[i] = a

    subjects = ""
    for i in attendance:
        subjects += i + ", "
    subjects = subjects[ : len(subjects)-2]

    if attendance != {}:

        msg = Message('Information Regarding Less Attendance',
                  sender='23f2002668@ds.study.iitm.ac.in',
                  recipients=[data[12]])
        msg.body = f"Dear {data[0]} S/O {data[1]}, \n\nWe hope this message finds you well. \n\nThis is to inform you that your current attendance record ( for {subjects} ) stands at below 75%, which is below the minimum requirement as per academic regulations. \n\nRegular attendance is crucial for academic success and is a mandatory criterion for eligibility in examinations and other academic activities. We kindly request you to take necessary steps to improve attendance in the coming weeks. \n\nIf you believe there has been a discrepancy or have a valid reason for the shortfall, please contact the concerned department or submit appropriate documentation. \n\nThank you for your attention to this matter. \n\nBest regards, \n{admin} \nDirector \nSober Shah Institute of Technical Education \nMuradnagar, Ghaziabad - 201206, \nUttar Pradesh, India"

        mail.send(msg)
        print("Mail sent successfully !")
        return "Mail Sent Successfully !"
    print("Attendance maintained, no need to send email !")
    return "Attendance maintained, no need to send email !"

def report_email(name, fname, email, file):

    msg = Message('Regarding Attendance Report',
                  sender='23f2002668@ds.study.iitm.ac.in',
                  recipients=[email])
    msg.body = f"Dear {name} S/O {fname}, your attendance report is attanched with this email. Please read it carefully and contact to your relevant teachers / faculties in case of any discrepancy. \n\nPassword : The password is the first four capital letters of your name and year of your date of birth (YYYY). \n\nLet your name is 'Abcdefghij' and date of birth is 'DD/MM/YYYY' then \n\nPassword = 'ABCDYYYY'"

    file_add = f"Documents/{file}"
    with current_app.open_resource(file_add) as pdf:
        msg.attach(
            filename=file,
            content_type="application/pdf",
            data=pdf.read()
        )

    mail.send(msg)
    subprocess.run(f"rm -f 'Documents/{file}'", shell=True)
    print("Mail sent successfully !")
    return "Mail Sent Successfully !"

    # ************************************************ Bar Chart *******************************************************

def barChart(subjectsAttendance):
    imgNames = []

    # 1. Overall Attendance Chart
    overall_labels = []
    overall_subjects = []
    for subject, values in subjectsAttendance.items():
        total = values[0]
        present = values[1]
        if total != 0:
            percentage = round((present * 100 / total), 3)
        else:
            percentage = 0
        overall_labels.append(percentage)
        overall_subjects.append(subject)

    plt.figure(figsize=(12, 8))
    x_pos = np.arange(len(overall_labels))
    colors = plt.cm.viridis(np.linspace(0.0, 1.0, len(overall_labels)))
    bar_width = max(0.3, min(0.6, 6 / len(overall_labels)))

    plt.title("Overall Subjects Attendance At Glance", fontsize=35, fontweight='bold', color='maroon', fontfamily='Courier New', pad=50)
    plt.xlabel("Subjects", fontsize=30, fontweight='bold', labelpad=10, color='maroon', fontfamily='Courier New')
    plt.ylabel("Attendance Rate", fontsize=30, fontweight='bold', labelpad=10, color='maroon', fontfamily='Courier New')
    plt.xticks(ticks=x_pos, labels=overall_subjects, rotation=45, fontsize=15, fontweight='bold', color='blue', fontfamily='Courier New')
    plt.gca().spines[['top', 'right']].set_visible(False)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    bars = plt.bar(x_pos, overall_labels, width=bar_width, color=colors, edgecolor='black', linewidth=0.25)
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 1, f'{height:.1f}', ha='center', fontsize=15,
                 fontweight='bold', color='blue', fontfamily='Courier New')

    plt.savefig("static/images/Overall Subjects Attendance_bar.png", transparent=True, bbox_inches='tight', dpi=300)
    imgNames.append("Overall Subjects")

    plt.clf()  # Clear figure for next plots



    # 2. Detailed Charts per Subject
    for subject, values in subjectsAttendance.items():
        total, present, absent, late, leave, date = values

        plt.figure(figsize=(10, 6))
        data = [present, absent, late, leave]
        labels = ["Present", "Absent", "Late", "Leave"]
        x_pos = np.arange(len(data))
        colors = plt.cm.viridis(np.linspace(0.0, 1.0, len(data)))
        bar_width = 0.5

        plt.title(f"{subject} Bar Chart", fontsize=27, fontweight='bold', color='maroon', fontfamily='Courier New', pad=30)
        plt.xlabel("Attendance", fontsize=24, fontweight='bold', labelpad=10, color='maroon', fontfamily='Courier New')
        plt.ylabel("Frequency", fontsize=24, fontweight='bold', labelpad=20, color='maroon', fontfamily='Courier New')
        plt.xticks(ticks=x_pos, labels=labels, rotation=45, fontsize=14, fontweight='bold', color='blue', fontfamily='Courier New')
        plt.gca().spines[['top', 'right']].set_visible(False)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        bars = plt.bar(x_pos, data, width=bar_width, color=colors, edgecolor='black', linewidth=0.25)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height + 0.1, f'{height:.1f}', ha='center', fontsize=12,
                     fontweight='bold', color='blue', fontfamily='Courier New')

        filename = f"static/images/{subject} Attendance_bar.png"
        plt.savefig(filename, transparent=True, bbox_inches='tight', dpi=300)
        imgNames.append(f"{subject}")
        plt.clf()
        plt.close()

    return imgNames


    # ************************************************ Pie Chart *******************************************************

def pieChart(subjectsAttendance):
    # subjectsAttendance = {Subject : [TotalSubjectAttendance, Present, Absent, Late, Leave]}
    subjects = [i for i in subjectsAttendance]
    total, present, absent, late, leave = [], [], [], [], []
    for i in subjectsAttendance:
        if subjectsAttendance[i][0] != 0:
            pre = round((subjectsAttendance[i][1] * 100 / subjectsAttendance[i][0]), 3)
            abs = round((subjectsAttendance[i][2] * 100 / subjectsAttendance[i][0]), 3)
            lat = round((subjectsAttendance[i][3] * 100 / subjectsAttendance[i][0]), 3)
            lea = round((subjectsAttendance[i][4] * 100 / subjectsAttendance[i][0]), 3)
            total.append(subjectsAttendance[i][0])
            present.append(pre)
            absent.append(abs)
            late.append(lat)
            leave.append(lea)
        else:
            total.append(0)
            present.append(0)
            absent.append(0)
            late.append(0)
            leave.append(0)

    imgNames = []

    for i in range(len(present)):
        if total[i] != 0:
            labels = ["Present", "Late", "Absent", "Leave"]
            values = [present[i], late[i], absent[i], leave[i]]
            colors = ['#66B032', '#FFA500', '#FF6F61', '#3399FF']
            explode = (0.1, 0.1, 0.1, 0.1)  # Slightly explode the "Present" slice as well

            # Plotting the pie chart
            plt.figure(figsize=(12, 8))  # Set figure size

            wedges, texts, autotexts = plt.pie(values, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                                               wedgeprops={'linewidth': 2, 'edgecolor': 'white'}, shadow=True, startangle=45,
                                               textprops={'color': 'black', 'fontsize': 20, 'fontfamily': 'Chalkboard'})  # Optional: add boldness to text

            for j, text in enumerate(texts):
                text.set_color(colors[j])  # Set label ("Present"/"Absent/Late/Leave") color

            # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.axis('equal')

            # Title
            plt.title(f"{subjects[i]} Pie Chart", pad=35, fontdict={'fontweight': 'bold', 'fontsize': 30, 'fontfamily': 'Courier New', 'color': 'Maroon'})

            # Save the chart with transparent background
            plt.savefig(f"static/images/{subjects[i]} Attendance_pie.png", transparent=True) # Here, we have not used f"{subjects[i]}_pie" because '_pie' will show in the chart name in Attendance Summary Page
            plt.close()
            imgNames.append(subjects[i]) # Here, we have not used f"{subjects[i]}_pie" because '_pie' will show in the chart name in Attendance Summary Page
        else:
            imgNames.append("")

    return imgNames

def summary(type, roll, course, department, year, semester, section):
    con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
    cur = con.cursor()

    query = "SELECT Name, RollNo, Subject, Date, Time, Attendance FROM AttendanceDetails WHERE RollNo = ? GROUP BY Date"

    cur.execute(query, (roll, ))
    max_att = cur.fetchall()
    max_att = len(max_att)

    query = "SELECT Name, RollNo, Subject, Date, Time, Attendance FROM AttendanceDetails WHERE RollNo = ?"

    cur.execute(query, (roll, ))
    data1 = cur.fetchall()

    total = 0
    for i in data1:
        if i[5] == "Present":
            total += 1

    d = {}
    file = f"{course} - {department} - {year} - {semester} - {section}.json"
    with open(f"jsonFiles/{file}") as f:
        d = json.load(f)
    r, data2 = [], []

    current_day = datetime.now().strftime('%A')

    for i in d:
        if i == current_day:
            r = d[i]

    subjectsAttendance = {}  # {Subject : [TotalSubjectAttendance, Present, Absent, Late, Leave, Date]}
    for i in r:
        if i[0] != "Interval":
            data2.append(i)
            subjectsAttendance[i[0]] = [0, 0, 0, 0, 0, ""]

    for i in data1:
        if i[2] in subjectsAttendance.keys():
            subjectsAttendance[i[2]][0] += 1
        else:
            subjectsAttendance[i[2]] = [0, 0, 0, 0, 0, ""]
            subjectsAttendance[i[2]][0] += 1
        subjectsAttendance[i[2]][5] = i[3]
        if i[5] == "Present":
            subjectsAttendance[i[2]][1] += 1
        elif i[5] == "Absent":
            subjectsAttendance[i[2]][2] += 1
        elif i[5] == "Late":
            subjectsAttendance[i[2]][3] += 1
        elif i[5] == "Leave":
            subjectsAttendance[i[2]][4] += 1
        else:
            subjectsAttendance[i[2]][2] += 1

    pieImgNames = pieChart(subjectsAttendance)
    barImgNames = barChart(subjectsAttendance)
    imgNames = [barImgNames[0]]
    for i in pieImgNames:
        imgNames.append(i)
    con.close()
    return render_template("attendanceSummary.html", type=type, data=data1, imgNames=imgNames)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

'''
@app.route('/location', methods=['POST'])
def get_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    print(f"User location: {latitude}, {longitude}")
    return jsonify(status="success", message="Location received")
'''




# **************************************************************** Student's Routes And Functions ***************************************************************#




@app.route("/student_registration")
def studentRegistration():
    return render_template("studentRegistration.html")

@app.route("/student_dashboard", methods=["GET", "POST"])
def student_dashboard():
    gender = session.get("Gender")
    img = "static/images/maleProfile-01.jpg"
    if gender == "Female":
        img = "static/images/femaleProfile-01.jpg"
    return render_template("studentDashboard.html", img=img)

@app.route("/student_profile", methods=["GET", "POST"])
def student_profile():
    if request.method == "GET":
        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()
        email = session.get("Email")
        query = """SELECT Name, FatherName, MotherName, Gender, DOB, Course, Department, Year, Semester, Section, RollNo, Mobile, Email FROM UserDetails WHERE Email==?"""
        res = cur.execute(query, (email, ))
        data = res.fetchone()
        con.close()
        return render_template("studentProfile.html", data=data)
    else:
        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()
        email = session["Email"]
        email = email.lower()
        roll = session["RollNo"]
        roll = roll.upper()
        name = request.form["name"]
        name = name.title()
        fname = request.form["fname"]
        fname = fname.title()
        mname = request.form["mname"]
        mname = mname.title()
        gender = request.form["gender"]
        gender = gender.title()
        dob = request.form["dob"]
        course = request.form["course"]
        course = course.title()
        dept = request.form["dept"]
        dept = dept.title()
        year = request.form["year"]
        sem = request.form["sem"]
        sec = request.form["sec"]
        sec = sec.upper()
        mob = request.form["cont"]
        date = datetime.now().strftime("%Y-%m-%d")
        day = datetime.now().strftime("%A")
        time = datetime.now().strftime("%H:%M:%S")

        if dob != session["DOB"] and dob != "":
            query1 = """UPDATE UserDetails SET Name=?, FatherName=?, MotherName=?, Gender=?, DOB=?, Course=?, Department=?, Year=?, Semester=?, Section=?, Mobile=?, Date=?, Day=?, Time=? WHERE Email = ?"""
            query2 = """UPDATE AttendanceDetails SET Name=?, Course=?, Department=?, Year=?, Semester=?, Section=? WHERE RollNo = ?"""
            cur.execute(query1, (name, fname, mname, gender, dob, course, dept, year, sem, sec, mob, date, day, time, email, ))
            cur.execute(query2, (name, course, dept, year, sem, sec, roll, ))
        else:
            query1 = """UPDATE UserDetails SET Name=?, FatherName=?, MotherName=?, Gender=?, Course=?, Department=?, Year=?, Semester=?, Section=?, Mobile=?, Date=?, Day=?, Time=? WHERE Email = ?"""
            query2 = """UPDATE AttendanceDetails SET Name=?, Course=?, Department=?, Year=?, Semester=?, Section=? WHERE RollNo = ?"""
            cur.execute(query1, (name, fname, mname, gender, course, dept, year, sem, sec, mob, date, day, time, email, ))
            cur.execute(query2, (name, course, dept, year, sem, sec, roll, ))
        con.commit()
        con.close()
        return redirect(url_for("student_profile"))

@app.route("/submit_attendance", methods=['GET', 'POST'])
def submit_attendance():
    if request.method == "GET":
        d = {}
        file = f"{session['Course']} - {session['Department']} - {session['Year']} - {session['Semester']} - {session['Section']}.json"
        with open(f"jsonFiles/{file}") as f:
            d = json.load(f)
        r, data = [], []

        current_day = datetime.now().strftime('%A')

        for i in d:
            if i == current_day:
                r = d[i]

        for i in r:
            if i[0] != "Interval":
                data.append(i)

        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()
        roll = session["RollNo"]
        date = datetime.now().strftime("%Y-%m-%d")

        atten = {}
        for i in data:
            atten[i[0]] = ""

        for i in data:
            query = """SELECT SubmittedAttendance, Action, Date FROM AttendanceDetails WHERE RollNo = ? AND Subject = ? AND Date = ? ORDER BY Time DESC LIMIT 1"""
            cur.execute(query, (roll, i[0], date))
            res = cur.fetchone()
            if res is not None:
                if res[0] is not None:
                    atten[i[0]] = res
                    if res[1] is None:
                        atten[i[0]] = (res[0], "Waiting")
                else:
                    atten[i[0]] = (None, None)
            else:
                atten[i[0]] = (None, None)

        for i in data:
            i.append(atten[i[0]][0])
            i.append(atten[i[0]][1])

        return render_template("submitAttendance.html", data=data)

    else:
        if request.is_json:
            data = request.get_json()
            sub = data.get("subject")
            attendance = data.get("attendance")
            date = datetime.now().strftime("%Y-%m-%d")
            time = datetime.now().strftime("%H:%M:%S")
            name = session["Name"]
            course = session['Course']
            dept = session["Department"]
            year = session["Year"]
            sem = session["Semester"]
            sec = session["Section"]
            roll = session['RollNo']
            con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
            cur = con.cursor()
            query = "INSERT INTO AttendanceDetails (Name, Course, Department, Year, Semester, Section, Subject, RollNo, Date, Time, SubmittedAttendance) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cur.execute(query, (name, course, dept, year, sem, sec, sub, roll, date, time, attendance, ))
            con.commit()
            con.close()
            return jsonify({"message": "Success"}), 200

        else:
            d = {}
            file = f"{session['Course']} - {session['Department']} - {session['Year']} - {session['Semester']} - {session['Section']}.json"
            with open(f"jsonFiles/{file}") as f:
                d = json.load(f)
            r, data = [], []

            current_day = datetime.now().strftime('%A')

            for i in d:
                if i == current_day:
                    r = d[i]

            for i in r:
                if i[0] != "Interval":
                    data.append(i)

            con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
            cur = con.cursor()
            roll = session["RollNo"]
            date = datetime.now().strftime("%Y-%m-%d")

            atten = {}
            for i in data:
                atten[i[0]] = ""

            for i in data:
                query = """SELECT SubmittedAttendance, Action, Date FROM AttendanceDetails WHERE RollNo = ? AND Subject = ? AND Date = ? ORDER BY Time DESC LIMIT 1"""
                cur.execute(query, (roll, i[0], date))
                res = cur.fetchone()
                if res is not None:
                    if res[0] is not None:
                        atten[i[0]] = res
                        if res[1] is None:
                            atten[i[0]] = (res[0], "Waiting")
                    else:
                        atten[i[0]] = (None, None)
                else:
                    atten[i[0]] = (None, None)

            for i in data:
                i.append(atten[i[0]][0])
                i.append(atten[i[0]][1])

            return render_template("submitAttendance.html", data=data)

@app.route("/attendance_details")
def attendance_details():
    roll = session["RollNo"]
    con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
    cur = con.cursor()

    query = "SELECT Name, RollNo, Subject, Date, Time, Attendance FROM AttendanceDetails WHERE RollNo = ? ORDER BY TIME DESC"

    cur.execute(query, (roll, ))
    data1 = cur.fetchall()
    con.close()

    data = []
    for i in data1:
        if i[5] == None:
            data.append([i[0], i[1], i[2], i[3], i[4], "Waiting"])
        else:
            data.append([i[0], i[1], i[2], i[3], i[4], i[5]])

    return render_template("attendanceDetails.html", data=data)

@app.route("/attendance_summary")
def attendance_summary():
    roll = session['RollNo']
    course = session['Course']
    department = session["Department"]
    year = session["Year"]
    semester = session["Semester"]
    section = session["Section"]
    return summary("student", roll, course, department, year, semester, section)

@app.route("/time_table")
def time_table():
    d = {}
    file = f"{session['Course']} - {session['Department']} - {session['Year']} - {session['Semester']} - {session['Section']}.json"
    with open(f"jsonFiles/{file}") as f:
        d = json.load(f)
    r = []
    for i in d:
        r.append(d[i])

    data = []

    for i in range(len(r[0])):
        l = []
        for j in r:
            l.append(j[i])
        data.append(l)

    return render_template("timeTable.html", data=data) #jsonify(data)   render_template("timeTable.html", data=r)

@app.route("/alert")
def alert():
    con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
    cur = con.cursor()

    query = """SELECT Subject, Content, Course, Department, Year, Semester, Section, Sender, Receiver, Date FROM Alerts"""
    cur.execute(query)
    d = cur.fetchall()
    data = []
    course, dept, year, sem, sec, roll = "Bachelor Of Technology", "Computer Science & Engineering", 2, 4, "B", "2302310111101"
    for i in d:
        if roll in i[8]:
            if (i[2]==course and i[3]==dept and i[4]==year and i[5]==sem and i[6]==sec):
                data.append(i)
    data.reverse()
    con.close()

    return render_template("alert.html", data=data);

@app.route("/report", methods=["GET", "POST"])
def report():
    # Get the actual Flask app instance
    appObj = current_app._get_current_object()

    name = session["Name"]
    fname = session["FatherName"]
    mname = session["MotherName"]
    dob = session["DOB"]
    dob = datetime.strptime(dob, "%Y-%m-%d")
    dob = dob.strftime("%d-%m-%Y")
    gender = session["Gender"]
    roll = session['RollNo']
    course = session['Course']
    department = session["Department"]
    year = session["Year"]
    semester = session["Semester"]
    section = session["Section"]
    mob = session["Mobile"]
    email = session["Email"]

    def makeReport(name, fname, mname, dob, gender, roll, course, department, year, semester, section, mob, email):
        with appObj.app_context():
            createReport(name, fname, mname, dob, gender, roll, course, department, year, semester, section, mob, email)

    mess = {
        "Message" : "Report Created Successfully ! Report will be shared on your email.",
        "Date" : datetime.now().strftime("%d-%m-%Y"),
        "Time" : datetime.now().strftime("%H:%M:%S")}

    Thread(
        target=makeReport,
        args=(name, fname, mname, dob, gender, roll, course, department, year, semester, section, mob, email)
    ).start()

    file = f"{roll} - Attendance Report.pdf"

    def emailReport(name, fname, email, file):
        with appObj.app_context():
            report_email(name, fname, email, file)

#    Thread(
#        target=emailReport,
#        args=(name, fname, email, file)
#    ).start()

    return Response(json.dumps(mess, indent=4, sort_keys=False), mimetype="application/json")

def createReport(name, fname, mname, dob, gender, roll, course, department, year, semester, section, mob, email):
    print("Report creating ...")
    subjects, dateAttendance, subjectsAttendance, imgNames = reportSummary(roll, course, department, year, semester, section)

    # Set Page-Width And Height
    page_width, page_height = A4

    # Set Margins
    margin = 0.5 * inch           # For setting margin in all sides
    right_margin = 1 * inch     # For setting margin in right side

    # Set Passwords in PDF
    password = pdfencrypt.StandardEncryption(userPassword="Xc845#bfFGT%jbdhsl0a8j3h4%#ndndhfkcmd$*&nd34$", ownerPassword=f"{(name[ : 4]).upper() + dob[-4 : ]}", canPrint=0, canModify=0, canCopy=0, canAnnotate=0)

    # Create PDF Object
    pdf = SimpleDocTemplate(f"Documents/{roll} - Attendance Report.pdf", page_size=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch, encrypt=password)

    # Calculate the starting x-coordinate for right-aligned text
    x = page_width - right_margin

    # Define Styles For Paragraph
    styles = getSampleStyleSheet()
    style = styles["Normal"]

    # Define a Custom Paragraph Style With The Desired Font And Size
    textStyle1 = ParagraphStyle(name='CustomStyle', fontName='Courier', fontSize=20, leading=20, alignment=TA_CENTER, textColor=colors.HexColor('#C11B17'))  # Orange color
    textStyle2 = ParagraphStyle(name='CustomStyle', fontName='Courier', fontSize=14, leading=20, alignment=TA_CENTER, textColor=colors.HexColor('#C11B17'))
    textStyle3 = ParagraphStyle(name='CustomStyle', fontName='Courier', fontSize=14, leading=20, alignment=TA_LEFT)
    textStyle4 = ParagraphStyle(name='CustomStyle', fontName='Courier', fontSize=12, leading=20, alignment=TA_LEFT)
    textStyle5 = ParagraphStyle(name='CustomStyle', fontName='Courier', fontSize=12, leading=20, alignment=TA_LEFT, textColor=colors.HexColor('#C11B17'))
    textStyle6 = ParagraphStyle(name='CustomStyle', fontName='Courier', fontSize=10, leading=20, alignment=TA_LEFT)
    textStyle7 = ParagraphStyle(name='CustomStyle', fontName='Courier', fontSize=8, leading=20, alignment=TA_CENTER, textColor=colors.HexColor('#C11B17'))

    # Define a Paragraph
    para = []

    # Define the Paragraph Text And Append Text in Paragraph
    date, time = datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M:%S")
    text1 = """ <strong> Monthly Attendance Report </strong>"""
    para.append(Paragraph(text1, textStyle1))
    para.append(Spacer(width=0, height=0.15*inch))     # Spacer = Provide space between the current para and next para   &   width = Horizontal space to insert   &   height = Vertical space to insert

    text2 = f""" <strong> Month -  {datetime.now().strftime('%B')}</strong>"""
    para.append(Paragraph(text2, textStyle2))
    para.append(Spacer(width=0, height=0.01*inch))

    text3 = f""" <strong> Date -  {date}</strong> """
    para.append(Paragraph(text3, textStyle2))
    para.append(Spacer(width=0, height=1*inch))

    text4 = f""" <strong> Student Details </strong> """
    para.append(Paragraph(text4, textStyle3))
    para.append(Spacer(width=0, height=0.25*inch))

    text5 = f"""Student Name : <font color="#2B65EC">{name}</font> <br/>Father's Name : <font color="#2B65EC">{fname}</font> <br/>Mother's Name : <font color="#2B65EC">{mname}</font> <br/>Date Of Birth : <font color="#2B65EC">{dob}</font> <br/>Gender : <font color="#2B65EC">{gender}</font> <br/>Course : <font color="#2B65EC">{course}</font> <br/>Department : <font color="#2B65EC">{department}</font> <br/>Year & Semester : <font color="#2B65EC">{year} & {semester}</font> <br/>Contact Number : <font color="#2B65EC">{mob}</font> <br/>Email ID : <font color="#2B65EC">{email}</font>"""
    para.append(Paragraph(text5, textStyle4))
    para.append(Spacer(width=0, height=1*inch))

    text6 = f"""<strong> Attendance Details </strong>"""
    para.append(Paragraph(text6, textStyle3))
    para.append(Spacer(width=0, height=0.15*inch))

    text7 = f"""The attendance details are given below :"""
    para.append(Paragraph(text7, textStyle4))
    para.append(Spacer(width=0, height=0.5*inch))

    subjects = [i for i in subjectsAttendance]
    total, present, absent, late, leave = [], {}, {}, {}, {}
    for i in subjectsAttendance:
        if subjectsAttendance[i][0] != 0:
            pre = round((subjectsAttendance[i][1] * 100 / subjectsAttendance[i][0]), 3)
            abs = round((subjectsAttendance[i][2] * 100 / subjectsAttendance[i][0]), 3)
            lat = round((subjectsAttendance[i][3] * 100 / subjectsAttendance[i][0]), 3)
            lea = round((subjectsAttendance[i][4] * 100 / subjectsAttendance[i][0]), 3)
            total.append(subjectsAttendance[i][0])
            present[i] = pre
            absent[i] = abs
            late[i] = lat
            leave[i] = lea
        else:
            total.append(0)
            present[i] = 0
            absent[i] = 0
            late[i] = 0
            leave[i] = 0

    text8 = f"""<strong>Overall Attendance of All Subjects Till Now </strong>"""
    para.append(Paragraph(text8, textStyle5))
    para.append(Spacer(width=0, height=0.5*inch))

    tableData = [["Subjects", "Attendance Rate"]]
    for i in present:
        tableData.append([i, str(present[i]) + " %"])

    t = Table(tableData, style=[
        ('BACKGROUND', (0,0), (1,0), colors.lightgrey),
        ('FONTSIZE', (0,0), (1,0), 15),
        ('LEADING', (0,0), (1,0), 20),
        ('TEXTCOLOR',(1,1),(1,9), colors.royalblue),
        ('ALIGN',(1,1),(1,9), 'CENTER'),
        ('FONTNAME', (0,0), (1,9), "Courier"),
        ('BOX',(0,0),(0,9), 1, colors.grey),
        ('BOX',(1,0),(1,9), 1, colors.grey),
        ('BOX',(0,0),(1,0), 1, colors.grey),
        ('BOX',(0,1),(1,1), 1, colors.grey),
        ('BOX',(0,2),(1,2), 1, colors.grey),
        ('BOX',(0,3),(1,3), 1, colors.grey),
        ('BOX',(0,4),(1,4), 1, colors.grey),
        ('BOX',(0,5),(1,5), 1, colors.grey),
        ('BOX',(0,6),(1,6), 1, colors.grey),
        ('BOX',(0,7),(1,7), 1, colors.grey),

    ])
    para.append(t)
    para.append(Spacer(width=0, height=0.5*inch))

    # Append Image in PDF Paragraph
    img = "static/images/Overall Subjects Attendance_bar.png"
    img = Image(img, width=5*inch, height=5*inch)
    para.append(img)
    para.append(Spacer(width=0, height=1*inch))

    n = 1
    for i in subjectsAttendance:
        text8 = f"""<strong>{n}. {i} </strong>"""
        para.append(Paragraph(text8, textStyle5))
        para.append(Spacer(width=0, height=0.5*inch))

        tableData = [["Attendance", "Frequency", "Rate"],
                     ["Present", subjectsAttendance[i][1], str(present[i]) + " %"],
                     ["Late", subjectsAttendance[i][3], str(late[i]) + " %"],
                     ["Leave", subjectsAttendance[i][4], str(leave[i]) + " %"],
                     ["Absent", subjectsAttendance[i][2], str(absent[i]) + " %"]
                     ]
        t = Table(tableData, style=[
            ('BACKGROUND', (0,0), (2,0), colors.lightgrey),
            ('FONTSIZE', (0,0), (2,0), 15),
            ('LEADING', (0,0), (2,0), 20),
            ('TEXTCOLOR',(1,1),(2,9), colors.royalblue),
            ('ALIGN',(1,1),(2,9), 'CENTER'),
            ('FONTNAME', (0,0), (3,5), "Courier"),
            ('BOX',(0,0),(0,9), 1, colors.grey),
            ('BOX',(1,0),(1,9), 1, colors.grey),
            ('BOX',(2,0),(2,9), 1, colors.grey),
            ('BOX',(0,0),(2,0), 1, colors.grey),
            ('BOX',(0,1),(2,1), 1, colors.grey),
            ('BOX',(0,2),(2,2), 1, colors.grey),
            ('BOX',(0,3),(2,3), 1, colors.grey),
            ('BOX',(0,4),(2,4), 1, colors.grey),
            ('BOX',(0,5),(2,5), 1, colors.grey),
            ('BOX',(0,6),(2,6), 1, colors.grey),
            ('BOX',(0,7),(2,7), 1, colors.grey),

        ])
        para.append(t)
        para.append(Spacer(width=0, height=1*inch))

        img1 = f"static/images/{i} Attendance_bar.png"
        img1 = Image(img1, width=3*inch, height=3*inch)
        img2 = f"static/images/{i} Attendance_pie.png"
        img2 = Image(img2, width=4.5*inch, height=3*inch)

        imgTable = Table(
            [[img1, "", img2]],
            colWidths=[3*inch, 0.5*inch, 3*inch],
            style=[
                ('ALIGN', (0,0), (2,0), 'CENTER')
            ]
        )
        para.append(imgTable)
        para.append(Spacer(width=0, height=1*inch))

        n += 1

    text9 = f"""<strong> Current Month Attendance </strong>"""
    para.append(Paragraph(text9, textStyle3))
    para.append(Spacer(width=1*inch, height=0.15*inch))

    head, sub = [""], {}
    for i in subjects:
        j = i.split(" ")
        x = ""
        for j in i:
            if j[0].isupper() or j[0]=="-":
                x += j[0]
        head.append(x)
        sub[i] = x
    head.sort()
    head[0] = 'Date'

    d = datetime.now().strftime("%Y-%m")
    dates = {}
    for i in range(1, 32):
        if i <= 9:
            dates[f"{d}-0{i}"] = [0]*(len(sub)+1)
            dates[f"{d}-0{i}"][0] = f"{d}-0{i}"
        else:
            dates[f"{d}-{i}"] = [0]*(len(sub)+1)
            dates[f"{d}-{i}"][0] = f"{d}-{i}"

    attendance = []
    for i in dateAttendance:
        j = dateAttendance[i]
        j.sort()
        for k in j:
            #dates[i].append([sub[k[0]], k[1], k[2]])
            for l in range(1, len(head)):
                if head[l] == sub[k[0]]:
                    dates[i][l] = (k[2] if k[2] is not None else "Waiting")

    for i in dates:
        x = []
        for j in dates[i]:
            if j==0 or j=="":
                x.append("")
            else:
                x.append(j)
        attendance.append(x)

    st = []
    for i in range(0, 32):
        for j in range(0, len(sub)+1):
            st.append(('BOX', (j,0), (j,i), 0.5, colors.black))
            st.append(('BOX', (0,i), (j,1), 0.5, colors.black))
    st1 = [
        ('BACKGROUND', (0,0), (len(sub),0), colors.lightgrey),
        ('FONTSIZE', (0,0), (len(sub),0), 14),
        ('LEADING', (0,0), (len(sub),0), 20),
        ('TEXTCOLOR', (1,1), (len(sub),31), colors.royalblue),
        ('ALIGN', (0,0), (len(sub),31), 'CENTER'),
        ('FONTNAME', (0,0), (len(sub), 31), 'Courier'),
    ]

    st = st1 + st

    style = TableStyle(st)

    tableData = [head] + attendance
    table = Table(tableData)

    for rowIndex, row in enumerate(tableData[1:], start=1):
        for colIndex, cell in enumerate(row[1:], start=1):
            if cell=="Present":
                style.add('BACKGROUND', (colIndex, rowIndex), (colIndex, rowIndex), colors.forestgreen)
                style.add('TEXTCOLOR', (colIndex, rowIndex), (colIndex, rowIndex), colors.whitesmoke)
            elif cell=="Absent":
                style.add('BACKGROUND', (colIndex, rowIndex), (colIndex, rowIndex), colors.red)
                style.add('TEXTCOLOR', (colIndex, rowIndex), (colIndex, rowIndex), colors.whitesmoke)
            elif cell=="Late":
                style.add('BACKGROUND', (colIndex, rowIndex), (colIndex, rowIndex), colors.orange)
                style.add('TEXTCOLOR', (colIndex, rowIndex), (colIndex, rowIndex), colors.whitesmoke)
            elif cell=="Leave":
                style.add('BACKGROUND', (colIndex, rowIndex), (colIndex, rowIndex), colors.royalblue)
                style.add('TEXTCOLOR', (colIndex, rowIndex), (colIndex, rowIndex), colors.whitesmoke)

    table.setStyle(style)
    para.append(table)
    para.append(Spacer(width=1*inch, height=1*inch))

    text10 = """<strong>Note : </strong>In case of any discrepancy in attendance, don't hesitate ! Contact to your teachers."""
    para.append(Paragraph(text10, textStyle6))
    para.append(Spacer(width=1*inch, height=1*inch))

    text11 = """******************************************** Finished *********************************************"""
    para.append(Paragraph(text11, textStyle7))
    para.append(Spacer(width=1*inch, height=1*inch))

    # Build The PDF With Paragraph
    pdf.build(para)

    createHtmlReport()

    print("Report created successfully !")

    return 200

def createHtmlReport():
    code = """<!DOCTYPE html>\n<html lang="en">\n<head>\n\t<meta charset="UTF-8">\n\t<title>Attendance Report</title>\n\t<style>\n\t\th1, h2 {\n\t\t\tcolor: maroon;\n\t\t\ttext-align: center;\n\t\t\tfont-family: Courier;\n\t\t}\n\t\t#studentDetails, #attendanceDetails, #subjectsAttendance {\n\t\t\tmargin-top: 10vh;\n\t\t\tmargin-left: 3vw;\n\t\t\tmargin-right: 3vw;\n\t\t}\n\t\tstrong {\n\t\t\tfont-size: 1.45em;\n\t\t\tcolor: maroon;\n\t\t\tfont-family: Courier;\n\t\t}\n\t\tp {\n\t\t\tfont-size: 1.2em;\n\t\t\tfont-family: Courier;\n\t\t}\n\t\tspan {\n\t\t\tcolor: blue;\n\t\t}\n\t\ttable {\n\t\t\tborder: 1px solid black;\n\t\t\tborder-collapse: collapse;\n\t\t\twidth: 70vw;\n\t\t\tmargin-top: 5vh;\n\t\t}\n\t\ttr {\n\t\t\twidth: 50%;\n\t\t\tborder: 1px solid black;\n\t\t\tpadding: 8px;\n\t\t\ttext-align: center;\n\t\t\tfont-family: Courier;\n\t\t}\n\t\tth {\n\t\t\twidth: 50%;\n\t\t\tborder: 1px solid black;\n\t\t\tpadding: 8px;\n\t\t\ttext-align: center;\n\t\t\tfont-size: 1.35em;\n\t\t\tbackground-color: lightgray;\n\t\t}\n\t\ttd {\n\t\t\twidth: 50%;\n\t\t\tborder: 1px solid black;\n\t\t\tpadding: 8px;\n\t\t\ttext-align: justify;\n\t\t\tfont-size: 1.25em;\n\t\t}\n\t\ttr:nth-child(odd) {\n\t\t\tbackground-color: lightgray;\n\t\t}\n\t\t.heading {\n\t\t\tmargin-top: 15vh;\n\t\t}\n\t\t.subjectsTable {\n\t\t\twidth: 33.33%;\n\t\t}\n\t</style>
        \n</head>\n<body>\n\t<h1> Monthly Attendance Report </h1>\n\t<h2> Month - May </h2>\n\t<h2> Date - 28/05/2025 </h2>
        \n\t<div id="studentDetails">\n\t\t<p><strong> Student Details </strong></p>\n\t\t<p> Student Name : <span>Shahzada Shan</span> </p>\n\t\t<p> Father's Name : <span>Mohammad Ilyas Shah</span> </p>\n\t\t<p> Mother's Name : <span>Shahjahan</span> </p>\n\t\t<p> Date Of Birth : <span>13-01-2006</span> </p>\n\t\t<p> Gender : <span>Male</span> </p>\n\t\t<p> Course : <span>Bachelor Of Technology</span> </p>\n\t\t<p> Department : <span>Computer Science & Engineering</span> </p>\n\t\t<p> Year & Semester : <span>2 & 4</span> </p>\n\t\t<p> Contact Number : <span>0009000801</span> </p>\n\t\t<p> Email ID : <span>shahzadashan87@gmail.com</span> </p>\n\t</div>
        \n\t<div id="attendanceDetails">\n\t\t<p class="heading"><strong> Attendance Details </strong></p>\n\t\t<p> The attendance details are given below : </p><br><br>\n\t\t<strong class="heading" style="color: maroon;"> Overall Attendance of All Subjects Till Now </strong>\n\t\t<table align="center">\n\t\t\t<tr>\n\t\t\t\t<th> Subjects </th>\n\t\t\t\t<th> Attendance Rate </th>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td> Data Structures and Algorithms </td>\n\t\t\t\t<td style="text-align: center; color: blue;"> 44.444 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td> Database Management Systems </td>\n\t\t\t\t<td style="text-align: center; color: blue;"> 62.5 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td> Modern Application Development - I </td>\n\t\t\t\t<td style="text-align: center; color: blue;"> 33.333 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td> Programming Concepts Using Java </td>\n\t\t\t\t<td style="text-align: center; color: blue;"> 36.364 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td> System Commands </td>\n\t\t\t\t<td style="text-align: center; color: blue;"> 50.0 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td> Machine Learning Foundations </td>\n\t\t\t\t<td style="text-align: center; color: blue;"> 33.333 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td> Business Data Management </td>\n\t\t\t\t<td style="text-align: center; color: blue;"> 60.0 % </td>\n\t\t\t</tr>\n\t\t</table>\n\t\t<img src="../static/images/Overall Subjects Attendance_bar.png" style="width: 55%; height: 55%; margin-top: 15vh; margin-left: 25%; margin-right: 25%;">\n\t</div>
        \n\t<div id="subjectsAttendance">\n\t\t<p class="heading"><strong> 1. Modern Application Development - I </strong></p><br>\n\t\t<table align="center">\n\t\t\t<tr>\n\t\t\t\t<th class="subjectsTable"> Attendance </th>\n\t\t\t\t<th class="subjectsTable"> Frequency </th>\n\t\t\t\t<th class="subjectsTable"> Rate </th>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td class="subjectsTable"> Present </td>\n\t\t\t\t<td class="subjectsTable" style="text-align: center; color: blue;"> 4 </td>\n\t\t\t\t<td class="subjectsTable" style="text-align: center; color: blue;"> 44.444 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td class="subjectsTable"> Late </td>\n\t\t\t\t<td class="subjectsTable" style="text-align: center; color: blue;"> 4 </td>\n\t\t\t\t<td class="subjectsTable" style="text-align: center; color: blue;"> 62.5 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td class="subjectsTable"> Leave </td>\n\t\t\t\t<td class="subjectsTable" style="text-align: center; color: blue;"> 3 </td>\n\t\t\t\t<td class="subjectsTable" style="text-align: center; color: blue;"> 62.5 % </td>\n\t\t\t</tr>\n\t\t\t<tr>\n\t\t\t\t<td class="subjectsTable"> Absent </td>\n\t\t\t\t<td class="subjectsTable" style="text-align: center; color: blue;"> 1 </td>\n\t\t\t\t<td class="subjectsTable" style="text-align: center; color: blue;"> 62.5 % </td>\n\t\t\t</tr>\n\t\t</table>\n\t\t<img src="../static/images/Modern Application Development - I Attendance_bar.png" style="width: 40%; height: 40%; margin-top: 15vh; margin-left: 4.5%; margin-right: 5%;">\n\t\t<img src="../static/images/Modern Application Development - I Attendance_pie.png" style="width: 40%; height: 40%; margin-top: 15vh; margin-left: 5%; margin-right: 4.5%;">\n\t</div>\n</body>\n</html>
    """

    print(code)

    with open("Documents/Report.html", 'w') as f:
        f.write(code)

def reportSummary(roll, course, department, year, semester, section):
    con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
    cur = con.cursor()

    query = "SELECT Name, RollNo, Subject, Date, Time, Attendance FROM AttendanceDetails WHERE RollNo = ? ORDER BY Date ASC"

    cur.execute(query, (roll, ))
    data = cur.fetchall()
    max_att = len(data)
    data1 = []
    d = datetime.now().strftime("%Y-%m-%d")
    d = d[ : len(d)-3]
    for i in data:
        if i[3][ : len(i[3])-3] == d:
            data1.append(i)
    subjects, dates, dateAttendance = set(), [], {}
    for i in data1:
        subjects.add(i[2])
        dates.append(i[3])
    dates.sort()
    for i in dates:
        dateAttendance[i] = []
    for i in data1:
        dateAttendance[i[3]].append([i[2], i[3], i[5] if i[5] is not None else "Absent"])

    total = 0
    for i in data1:
        if i[5] == "Present":
            total += 1

    d = {}
    file = f"{course} - {department} - {year} - {semester} - {section}.json"
    with open(f"jsonFiles/{file}") as f:
        d = json.load(f)
    r, data2 = [], []

    current_day = datetime.now().strftime('%A')

    for i in d:
        if i == current_day:
            r = d[i]

    subjectsAttendance = {}  # {Subject : [TotalSubjectAttendance, Present, Absent, Late, Leave, Date]}
    for i in r:
        if i[0] != "Interval":
            data2.append(i)
            subjectsAttendance[i[0]] = [0, 0, 0, 0, 0, ""]

    for i in data:
        if i[2] in subjectsAttendance.keys():
            subjectsAttendance[i[2]][0] += 1
        else:
            subjectsAttendance[i[2]] = [0, 0, 0, 0, 0, ""]
            subjectsAttendance[i[2]][0] += 1
        subjectsAttendance[i[2]][5] = i[3]
        if i[5] == "Present":
            subjectsAttendance[i[2]][1] += 1
        elif i[5] == "Absent":
            subjectsAttendance[i[2]][2] += 1
        elif i[5] == "Late":
            subjectsAttendance[i[2]][3] += 1
        elif i[5] == "Leave":
            subjectsAttendance[i[2]][4] += 1
        else:
            subjectsAttendance[i[2]][2] += 1

    pieImgNames = pieChart(subjectsAttendance)
    barImgNames = barChart(subjectsAttendance)
    imgNames = [barImgNames[0]]
    for i in pieImgNames:
        imgNames.append(i)
    con.close()
    return subjects, dateAttendance, subjectsAttendance, imgNames




# **************************************************************** Teacher's Routes And Functions ***************************************************************#




@app.route("/teacherRegistration")
def teacherRegistration():
    return render_template("teacherRegistration.html")

@app.route("/teacher_dashboard")
def teacher_dashboard():
    gender = session.get("Gender")
    img = "static/images/maleProfile-01.jpg"
    if gender == "Female":
        img = "static/images/femaleProfile-01.jpg"
    return render_template("teacherDashboard.html", img=img)

@app.route("/teacher_profile", methods=["GET", "POST"])
def teacher_profile():
    if request.method == "GET":
        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()
        email = session.get("Email")
        query = """SELECT Name, FatherName, MotherName, Gender, DOB, Mobile, Email FROM UserDetails WHERE Email==?"""
        res = cur.execute(query, (email, ))
        data = res.fetchone()
        con.close()
        return render_template("teacherProfile.html", data=data)
    else:
        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()
        email = session["Email"]
        roll = session["RollNo"]
        name = request.form["name"]
        name = name.title()
        fname = request.form["fname"]
        fname = fname.title()
        mname = request.form["mname"]
        mname = mname.title()
        gender = request.form["gender"]
        gender = gender.title()
        dob = request.form["dob"]
        mob = request.form["cont"]
        date = datetime.now().strftime("%Y-%m-%d")
        day = datetime.now().strftime("%A")
        time = datetime.now().strftime("%H:%M:%S")

        if dob != session["DOB"] and dob != "":
            query1 = """UPDATE UserDetails SET Name=?, FatherName=?, MotherName=?, Gender=?, DOB=?, Mobile=?, Date=?, Day=?, Time=? WHERE Email = ?"""
            cur.execute(query1, (name, fname, mname, gender, dob, mob, date, day, time, email, ))
        else:
            query1 = """UPDATE UserDetails SET Name=?, FatherName=?, MotherName=?, Gender=?, Mobile=?, Date=?, Day=?, Time=? WHERE Email = ?"""
            cur.execute(query1, (name, fname, mname, gender, mob, date, day, time, email, ))
        con.commit()
        con.close()
        return redirect(url_for("teacher_profile"))

@app.route("/take_attendance", methods=['GET', 'POST'])
def take_attendance():
    if request.method == "GET":
        d = {}
        file = f"jsonFiles/{session['Email']}.json"
        with open(file) as f:
            d = json.load(f)

        cours, depts, years, sems, secs, subs = [], [], [], [], [], []
        for i in d.values():
            for j in i:
                if j[1] not in cours and j[1] != "":
                    cours.append(j[1])
                if j[2] not in depts and j[2] != "":
                    depts.append(j[2])
                if j[3] not in years and j[3] != "":
                    years.append(j[3])
                if j[4] not in sems and j[4] != "":
                    sems.append(j[4])
                if j[5] not in secs and j[5] != "":
                    secs.append(j[5])
                if j[0] not in subs and j[0] != "":
                    subs.append(j[0])
        subs.remove("Interval")
        cours.sort();
        depts.sort();
        years.sort();
        sems.sort();
        secs.sort();
        subs.sort()

        date = datetime.now().strftime("%Y-%m-%d")
        data = []

        return render_template("takeAttendance.html", courses=cours, departments=depts, years=years, semesters=sems, sections=secs, subjects=subs, data=data), 200

    else:
        if request.is_json:
            d = request.get_json()
            data = d.get("attendance")
            act = d.get("action")
            att = data[4]
            if act == "Rejected":
                att = "Absent"
            con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
            cur = con.cursor()
            query = """UPDATE AttendanceDetails SET Action=? , Attendance=? WHERE Name=? AND RollNo=? AND Date=? AND Time=?"""
            cur.execute(query, (act, att, data[0], data[1], data[2], data[3], ))
            con.commit()
            con.close()

            # Get the actual Flask app instance
            appObj = current_app._get_current_object()

            def sentEmail():
                with appObj.app_context():
                    attendance_email(data[1])

            Thread(target=sentEmail).start()

            return jsonify({
                "message": "Attendance accepted successfully !",
                "Attendance": att
            }), 200
        course = str(request.form["Course"])
        dept = str(request.form["Department"])
        year = str(request.form["Year"])
        sem = str(request.form["Semester"])
        sec = str(request.form["Section"])
        sub = str(request.form["Subject"])

        data = []

        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()

        query = """SELECT Name, RollNo, Date, Time, SubmittedAttendance, Action FROM AttendanceDetails WHERE Course = ? AND Department = ? AND Year = ? AND Semester = ? AND Section = ? AND Subject = ? AND Date = ? GROUP BY RollNo ORDER BY Time DESC"""
        d = datetime.today().strftime('%Y-%m-%d')
        cur.execute(query, (course, dept, year, sem, sec, sub, d, ))
        d = cur.fetchall()
        d = list(d)
        data = []
        for i in d:
            i = list(i)
            if i[5] is None:
                i[5] = ""
                data.append(list(i))
            else:
                data.append(list(i))
        con.close()

        d = {}
        file = f"jsonFiles/{session['Email']}.json"
        with open(file) as f:
            d = json.load(f)

        cours, depts, years, sems, secs, subs = [], [], [], [], [], []
        for i in d.values():
            for j in i:
                if j[1] not in cours and j[1] != "":
                    cours.append(j[1])
                if j[2] not in depts and j[2] != "":
                    depts.append(j[2])
                if j[3] not in years and j[3] != "":
                    years.append(j[3])
                if j[4] not in sems and j[4] != "":
                    sems.append(j[4])
                if j[5] not in secs and j[5] != "":
                    secs.append(j[5])
                if j[0] not in subs and j[0] != "":
                    subs.append(j[0])
        subs.remove("Interval")
        cours.sort();
        depts.sort();
        years.sort();
        sems.sort();
        secs.sort();
        subs.sort()
        return render_template("takeAttendance.html", courses=cours, departments=depts, years=years, semesters=sems, sections=secs, subjects=subs, data=data), 200

@app.route("/teacher_attendance_summary", methods=["GET", "POST"])
def teacher_attendance_summary():
    if request.method=="GET":
        d = {}
        file = f"jsonFiles/{session['Email']}.json"
        with open(file) as f:
            d = json.load(f)

        cours, depts, years, sems, secs, subs = [], [], [], [], [], []
        for i in d.values():
            for j in i:
                if j[1] not in cours and j[1] != "":
                    cours.append(j[1])
                if j[2] not in depts and j[2] != "":
                    depts.append(j[2])
                if j[3] not in years and j[3] != "":
                    years.append(j[3])
                if j[4] not in sems and j[4] != "":
                    sems.append(j[4])
                if j[5] not in secs and j[5] != "":
                    secs.append(j[5])
                if j[0] not in subs and j[0] != "":
                    subs.append(j[0])
        subs.remove("Interval")

        cours.sort();
        depts.sort();
        years.sort();
        sems.sort();
        secs.sort();
        subs.sort()
        return render_template("teacherAttendanceSummary.html", courses=cours, departments=depts, years=years, semesters=sems, sections=secs, subjects=subs)
    else:
        course = request.form["Course"]
        dept = request.form["Department"]
        year = request.form["Year"]
        sem = request.form["Semester"]
        sec = request.form["Section"]
        roll = request.form["roll"]
        try :
            return summary("teacher", roll, course, dept, year, sem, sec)
        except :
            return "Incorrect Credentials !"

@app.route("/teacher_attendance_details", methods=["GET", "POST"])
def teacher_attendance_details():
    if request.method == "GET":
        d = {}
        file = f"jsonFiles/{session['Email']}.json"
        with open(file) as f:
            d = json.load(f)

        cours, depts, years, sems, secs, subs = [], [], [], [], [], []
        for i in d.values():
            for j in i:
                if j[1] not in cours and j[1] != "":
                    cours.append(j[1])
                if j[2] not in depts and j[2] != "":
                    depts.append(j[2])
                if j[3] not in years and j[3] != "":
                    years.append(j[3])
                if j[4] not in sems and j[4] != "":
                    sems.append(j[4])
                if j[5] not in secs and j[5] != "":
                    secs.append(j[5])
                if j[0] not in subs and j[0] != "":
                    subs.append(j[0])
        subs.remove("Interval")

        cours.sort();
        depts.sort();
        years.sort();
        sems.sort();
        secs.sort();
        subs.sort()

        return render_template("teacherAttendanceDetails.html", courses=cours, departments=depts, years=years, semesters=sems, sections=secs, subjects=subs)

    else:
        course = str(request.form["Course"])
        dept = str(request.form["Department"])
        year = str(request.form["Year"])
        sem = str(request.form["Semester"])
        sec = str(request.form["Section"])
        sub = str(request.form["Subject"])
        Date = str(request.form["Date"])

        data = []

        con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
        cur = con.cursor()

        if Date:
            query = """SELECT Name, RollNo, Subject, Date, Time, Attendance FROM AttendanceDetails WHERE Course = ? AND Department = ? AND Year = ? AND Semester = ? AND Section = ? AND Subject = ? AND Date = ? ORDER BY Date DESC"""
            cur.execute(query, (course, dept, year, sem, sec, sub, Date, ))
        else:
            query = """SELECT Name, RollNo, Subject, Date, Time, Attendance FROM AttendanceDetails WHERE Course = ? AND Department = ? AND Year = ? AND Semester = ? AND Section = ? AND Subject = ? ORDER BY Date DESC"""
            cur.execute(query, (course, dept, year, sem, sec, sub, ))
        data = cur.fetchall()
        con.close()

        d = {}
        file = f"jsonFiles/{session['Email']}.json"
        with open(file) as f:
            d = json.load(f)

        cours, depts, years, sems, secs, subs = [], [], [], [], [], []
        for i in d.values():
            for j in i:
                if j[1] not in cours and j[1] != "":
                    cours.append(j[1])
                if j[2] not in depts and j[2] != "":
                    depts.append(j[2])
                if j[3] not in years and j[3] != "":
                    years.append(j[3])
                if j[4] not in sems and j[4] != "":
                    sems.append(j[4])
                if j[5] not in secs and j[5] != "":
                    secs.append(j[5])
                if j[0] not in subs and j[0] != "":
                    subs.append(j[0])
        subs.remove("Interval")
        cours.sort();
        depts.sort();
        years.sort();
        sems.sort();
        secs.sort();
        subs.sort()
        return render_template("teacherAttendanceDetails.html", courses=cours, departments=depts, years=years, semesters=sems, sections=secs, subjects=subs, data=data)

@app.route("/teacher_time_table", methods=["GET"])
def teacher_time_table():
    d = {}
    file = f"jsonFiles/{session['Email']}.json"
    with open(file) as f:
        d = json.load(f)
    mon, tue, wed, thu, fri, sat = d["Monday"], d["Tuesday"], d["Wednesday"], d["Thursday"], d["Friday"], d["Saturday"]
    day = datetime.now().strftime("%A")
    return render_template("teacherTimeTable.html", mon=mon, tue=tue, wed=wed, thu=thu, fri=fri, sat=sat, day=day)

@app.route("/teacher_alert")
def teacher_alert():
    con = sqlite3.connect("instance/AttendanceMaster.sqlite3")
    cur = con.cursor()

    query = """SELECT Subject, Content, Course, Department, Year, Semester, Section, Sender, Receiver, Date FROM Alerts"""
    cur.execute(query)
    d = cur.fetchall()
    data = []
    course, dept, year, sem, sec, roll = "Bachelor Of Technology", "Computer Science & Engineering", 2, 4, "B", "2302310111101"
    for i in d:
        if roll in i[8]:
            if (i[2]==course and i[3]==dept and i[4]==year and i[5]==sem and i[6]==sec):
                data.append(i)
    data.reverse()
    con.close()

    return render_template("teacherAlert.html", data=data);

if __name__ == "__main__":
    app.debug=True
    app.run(host="0.0.0.0", port=5000)