from reportlab.pdfgen import canvas as can
from reportlab.lib import pdfencrypt, colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os, subprocess, random, time, sqlite3, json, numpy as np, matplotlib, matplotlib.pyplot as plt; matplotlib.use('Agg')

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

    '''pieImgNames = pieChart(subjectsAttendance)
    barImgNames = barChart(subjectsAttendance)
    imgNames = [barImgNames[0]]
    for i in pieImgNames:
        imgNames.append(i)
    con.close()'''
    return subjects, dateAttendance    # render_template("attendanceSummary.html", type=type, data=data1, imgNames=imgNames)

def report():
    roll = '2302310111121' #session['RollNo']
    course = 'Bachelor Of Technology' #session['Course']
    department = 'Computer Science & Engineering' #session["Department"]
    year = '2' #session["Year"]
    semester = '4' #session["Semester"]
    section = 'B' #session["Section"]

    subjects, dateAttendance = reportSummary(roll, course, department, year, semester, section)

    # Set Page-Width And Height
    page_width, page_height = A4

    # Set Margins
    margin = 0.5 * inch           # For setting margin in all sides
    right_margin = 1 * inch     # For setting margin in right side

    # Set Passwords in PDF
    password = pdfencrypt.StandardEncryption(userPassword="Shahzada", ownerPassword="Shahzada", canPrint=0, canModify=0, canCopy=0, canAnnotate=0)

    # Create PDF And Its Object
    #pdf = can.Canvas("Test.pdf", bottomup=0) # pdf = can.Canvas("Test.pdf", bottomup=0, encrypt=password)
    pdf = SimpleDocTemplate("Documents/Test.pdf", page_size=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)

    # Set Starting Position of First Word
    #pdf.translate(10, 10)

    # Calculate the starting x-coordinate for right-aligned text
    x = page_width - right_margin

    '''
    # Set-Up Text Object
    textObj = pdf.beginText(x, page_height - (1 * inch))
    
    # Get Available Fonts
    fonts = pdf.getAvailableFonts()
    print(fonts)
    
    # Set Font
    textObj.setFont(psfontname="Courier", size=25)
    textObj.setTextOrigin(1 * inch, 1 * inch)
    
    # Defines Lines to Write
    lines = ["Hello, its me 'Shahzada Moon' !", "This method is particularly useful when you want to create margins or adjust the layout of your content without manually calculating the new coordinates for each drawing operation."]
    
    # Add Lines To Text Object
    for line in lines:
        textObj.textLine(line)
    
    # Write Lines in PDF
    pdf.drawText(textObj)
    '''


    #Get Available Fonts
    fonts = pdfmetrics.getRegisteredFontNames()
    #print(fonts)

    # Register the custom font
    #pdfmetrics.registerFont(TTFont('CustomFont', '/path/to/your/font.ttf'))


    # Define Styles For Paragraph
    styles = getSampleStyleSheet()
    style = styles["Normal"]

    # Define a custom paragraph style with the desired font and size
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

    text3 = f""" <strong> Date -  {date}</strong>"""
    para.append(Paragraph(text3, textStyle2))
    para.append(Spacer(width=0, height=1*inch))

    text4 = f"""<strong> Student Details </strong>"""
    para.append(Paragraph(text4, textStyle3))
    para.append(Spacer(width=0, height=0.25*inch))

    text5 = f"""Student Name : <font color="#2B65EC">Shahzada Shan</font> <br/>Father's Name : <font color="#2B65EC">Mohammad Ilyas Shah</font> <br/>Mother's Name : <font color="#2B65EC">Shahjahan</font> <br/>Course : <font color="#2B65EC">Bachelor Of Technology</font> <br/>Department : <font color="#2B65EC">Computer Science & Engineering</font> <br/>Year & Semester : <font color="#2B65EC">2 & 4</font> <br/>Contact Number : <font color="#2B65EC">8126524809</font> <br/>Email ID : <font color="#2B65EC">shahzadashan.87@gmail.com</font>"""
    para.append(Paragraph(text5, textStyle4))
    para.append(Spacer(width=0, height=1*inch))

    text6 = f"""<strong> Attendance Details </strong>"""
    para.append(Paragraph(text6, textStyle3))
    para.append(Spacer(width=0, height=0.15*inch))

    text7 = f"""The current attendance details are given below :"""
    para.append(Paragraph(text7, textStyle4))
    para.append(Spacer(width=0, height=0.5*inch))

    text8 = f"""<strong>1. Overall Attendance of All Subjects </strong>"""
    para.append(Paragraph(text8, textStyle5))
    para.append(Spacer(width=0, height=0.5*inch))

    tableData = [["Subjects", "Attendance"],
                 ["Data Structures & Algorithms", "42.9 %"],
                 ["Database Management Systems", "42.9 %"],
                 ["Modern Application Develeopment-1", "28.6 %"],
                 ["Programming Concepts Using Java", "33.3 %"],
                 ["System Commands", "50.0 %"],
                 ["Machine Learning Foundation", "28.6 %"],
                 ["Business Data Management", "40.0 %"],
                 ["Tools In Data Science", "16.7 %"]]
    t = Table(tableData, style=[
        ('BACKGROUND', (0,0), (1,0), colors.lightgrey),
        ('FONTSIZE', (0,0), (1,0), 15),
        ('LEADING', (0,0), (1,0), 20),
        ('TEXTCOLOR',(1,1),(1,9), colors.royalblue),
        ('ALIGN',(1,1),(1,9), 'CENTER'),
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

    text8 = f"""<strong>2. Data Structures & Algorithms </strong>"""
    para.append(Paragraph(text8, textStyle5))
    para.append(Spacer(width=0, height=0.5*inch))

    tableData = [["Attendance", "Frequency"],
                 ["Present", "3"],
                 ["Late", "4"],
                 ["Leave", "0"],
                 ["Absent", "0"]
    ]
    t = Table(tableData, style=[
        ('BACKGROUND', (0,0), (1,0), colors.lightgrey),
        ('FONTSIZE', (0,0), (1,0), 15),
        ('LEADING', (0,0), (1,0), 20),
        ('TEXTCOLOR',(1,1),(1,9), colors.royalblue),
        ('ALIGN',(1,1),(1,9), 'CENTER'),
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
    para.append(Spacer(width=0, height=1*inch))

    img1 = "static/images/Data Structures and Algorithms Attendance_bar.png"
    img1 = Image(img1, width=3*inch, height=3*inch)
    img2 = "static/images/Data Structures and Algorithms Attendance_pie.png"
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
            for l in range(1, len(head)-1):
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
        ('ALIGN', (0,0), (len(sub),31), 'CENTER')
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

    # pdf.save()

if __name__ == "__main__":
    report()