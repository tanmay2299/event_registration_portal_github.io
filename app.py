from flask import Flask, render_template, request ,redirect ,url_for
import mysql.connector
from mysql.connector import Error
import datetime
import os

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
mydb = mysql.connector.connect(host='localhost', database='pythonprogramming',user='root',password='Password@123') 

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form['submit'] == 'index_page':
            return redirect('index')
        elif request.form['submit'] == 'admin_page':
            return redirect('pie')
        else:
            return('success')
    
    return render_template('home.html')
 
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error=''
    if request.method == 'POST':
        userDetails = request.form
        if userDetails['uname'] != 'admin' or userDetails['psw'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('admin.html', error=error)
    
@app.route('/pie', methods=['GET', 'POST'])
def pie():
    #cur = mydb.cursor()
    cur1 = mydb.cursor()
    cur2 = mydb.cursor()
    cur3 = mydb.cursor()
    cur4 = mydb.cursor()
    cur5 = mydb.cursor()
    cur1.execute("select SUM(NO_OF_TICKET) from event1 where REG_TYPE='Self'")
    valuef=cur1.fetchone()
    for a in valuef:
        print("--------------------",a)
    
    cur2.execute("select SUM(NO_OF_TICKET) from event1 where REG_TYPE='Group'")
    valueg=cur2.fetchone()
    for b in valueg:
        print("--------------------",b)    
   
    cur3.execute("select SUM(NO_OF_TICKET) from event1 where REG_TYPE='Corporate'")
    valuec=cur3.fetchone()
    for c in valuec:
        print("--------------------",c)   

    cur4.execute("select SUM(NO_OF_TICKET) from event1 where REG_TYPE='Others'")
    valueo=cur4.fetchone()
    for d in valueo:
        print("--------------------",d)

    cur5 = mydb.cursor()
    cur5.execute("select REG_NO from event1")
    records = cur5.fetchall()
    #return render_template('chart.html',row=records)      
    return render_template('chart.html', title='Count of registration types',row=records, max=17000, valuef=str(a),valueg=str(b),valuec=str(c),valueo=str(d)) 

@app.route('/show_entry', methods=['GET', 'POST'])
def show_entry(REG_NO):
    x=''
    for character in REG_NO:
        if character.isalnum():
            x += character
    print("-------------------------",x)
    cur = mydb.cursor()
    cur.execute("select * from event1 where REG_NO='" + x + "';")
    entries = cur.fetchall()
    for row in entries:
        print(row[0])
    return render_template('show_entry.html', name=str(row[1]) ,mob_no=str(row[2]) ,email=str(row[3]) ,upload_id=str(row[4]) ,reg_type=str(row[5]),no_of_tickets=str(row[6]),metadata=str(row[7]),reg_no=str(row[8]))

@app.route('/index', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        userDetails = request.form
        FULLNAME = userDetails['name']
        MOBILE = userDetails['phn']
        EMAIL = userDetails['email']
        REG_TYPE=userDetails['reg']
        if REG_TYPE=='Self':
            code = 'S'
            NO_OF_TICKET=1
            qnt = '00' + str(NO_OF_TICKET)
        else:  
            if REG_TYPE=='Group':
                code = 'G'
            if REG_TYPE=='Others':
                code = 'O'  
            if REG_TYPE=='Corporate':
                code = 'C'
            NO_OF_TICKET=userDetails['tic']

            if int(NO_OF_TICKET)<10:
                qnt = '00' + str(NO_OF_TICKET)
            if int(NO_OF_TICKET)<100:
                qnt = '0' + NO_OF_TICKET
            if int(NO_OF_TICKET)>100:
                qnt = NO_OF_TICKET

        METADATA = datetime.datetime.now()
        reg_date = (METADATA.strftime("%D"))
        date_code=''
        for character in reg_date:
            if character.isalnum():
                date_code += character
        REG_NO = "ER" + date_code + (METADATA.strftime("%H")) + (METADATA.strftime("%M")) + (METADATA.strftime("%S")) +  qnt
        print ("--------------------------",REG_NO)
        cur= mydb.cursor()
        cur.execute("INSERT INTO buffer(FULLNAME,MOBILE,EMAIL,REG_TYPE,NO_OF_TICKET,METADATA,REG_NO) VALUES (%s,%s,%s,%s,%s,%s,%s)",(FULLNAME,MOBILE,EMAIL,REG_TYPE,NO_OF_TICKET,METADATA.strftime("%c"),REG_NO))
        mydb.commit()
        cur.close()
        return redirect('upload')
    return render_template('hackathon.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')
    
@app.route('/display', methods=['GET', 'POST'])
def display():
    cur1 = mydb.cursor()
    cur1.execute("select * from buffer")
    records = cur1.fetchall()
    for row in records:
        print("FULLNAME = ", row[0])
        print("MOBILE  = ", row[1])
        print("EMAIL = ", row[2])
        print("REG_TYPE = ", row[4])
        print("NO_OF_TICKETS = ", row[5])
    target=os.path.join(APP_ROOT, 'static/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    else:
       print('Could not create upload directory: {}'.format(target))
    print("------",request.files.getlist("file"))
    print("##############################",APP_ROOT)
    for upload in request.files.getlist("file"):
        print(upload)
        print("{}is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target,filename])
        print("Accept incoming file:",filename)
        print("Save it to:",destination)
        upload.save(destination)
        cur1.execute("UPDATE buffer SET UPLOAD_ID = '/" + filename + "' WHERE FULLNAME= '" + row[0] + "';")
        mydb.commit()
        cur1.close()
        #file.save(destination)
        print("---------------------------------------",filename)
    #return render_template('display.html',image_name=filename)
    cur1 = mydb.cursor()
    cur1.execute("select * from buffer")
    records = cur1.fetchall()
        
    return render_template('display.html',value=str(row[0]) ,value1=str(row[1]) ,value2=str(row[2]) ,value3=str(row[4]) ,value4=str(row[5]),image_name=filename)


@app.route('/idcard',methods=['GET','POST'])
def idcard():
    cur1 = mydb.cursor()
    cur2 = mydb.cursor()
    cur1.execute("select * from buffer")
    records = cur1.fetchall()
    
    for row in records:
        print("FULLNAME = ", row[0])
        print("MOBILE  = ", row[1])
        print("EMAIL = ", row[2])
        print("REG_TYPE = ", row[4])
        print("NO_OF_TICKETS = ", row[5])

    cur2.execute("INSERT INTO event1(FULLNAME,MOBILE,EMAIL,REG_TYPE,NO_OF_TICKET,METADATA,REG_NO,UPLOAD_ID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(row[0],row[1],row[2],row[4],row[5],row[6],row[7],row[3]))
    cur1.execute("delete from buffer")   
    mydb.commit()
    return render_template('idcard.html',value=str(row[0]) ,value1=str(row[1]) ,value2=str(row[2]) ,value3=str(row[4]) ,value4=str(row[5]),value5=str(row[7]))



if __name__ == '__main__':
     app.run(debug=True)