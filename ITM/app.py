import numpy as np
from flask import Flask, request, render_template, Response , jsonify, Blueprint , session, redirect, flash
import jwt
import re
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from functools import wraps
from datetime import datetime, date
import pickle
import cv2

app = Flask(__name__)

app.config['SECRET_KEY'] = 'x123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test' #name DB

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

mysql = MySQL(app)

@app.route('/')
def index():
    error = None
    session.clear();
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
       return 'Logged in currently'

#Authenticate
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!' : 'Token is missing!'}),403
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Alert!' : 'Invalid Token!'}),403
    return decorated

@app.route('/login', methods=['POST'])
def login():
    error = None
    cur = mysql.connection.cursor()
    cur.execute("select u.username,u.password,u.email,u.userID from users u")
    fetchdata = cur.fetchall()
    cur.close()
    for data in fetchdata:      
        if request.form['username'] == data[0] and request.form['password'] == data[1]:
            session['logged_in'] = True
            session['userID'] = data[3]
            token = jwt.encode({
                'user':data[0],
                'email':data[2],
                'expiration': f"{datetime.utcnow() + timedelta(seconds=20)}"
            },
            app.config['SECRET_KEY'], algorithm='HS256')
            #return jsonify({'token' : token})
            return redirect("/index", code=302)
        else: 
            #return jsonify({'token' : 'Invalid credentials'})
            flash(u'Invalid password provided', 'error')
            return render_template('login.html')
        

@app.route('/registerForm')
def registerForm():
    return render_template('register.html')

def checkUsername(username):
    try:
        cur = mysql.connection.cursor()
        cur.execute("select u.username from users u where u.username ="+username)
        fetchdata = cur.fetchall()
        cur.close()
        return True
    except Exception:
        return False

@app.route('/register', methods=['POST','GET'])
def register():
    mesage = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'name' in request.form and 'surname' in request.form and 'age' in request.form and 'height' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        surname = request.form['surname']
        age = request.form['age']
        height = request.form['height']
        confirmPassword = request.form['password_confirm']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if not age.isnumeric():
            mesage = 'age is not number'
        elif not height.isnumeric():
            mesage = 'height is not number'
        elif account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif len(password) < 8:
            mesage = 'password length less than 8 character'
        elif len(confirmPassword) < 8:
            mesage = 'confirmpassword length less than 8 character'
        elif password != confirmPassword:
            mesage = 'password not match'
        else:
            values = (email,username,password,name,surname,age,height)
            cursor.execute("INSERT INTO users(email,username,password,name,surname,age,height) VALUES(%s,%s,%s,%s,%s,%s,%s)", values)
            mysql.connection.commit()
            return redirect('/')
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in',None)
        session.pop('userID',None)
    return redirect("/", code=302)

#Authen
@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified. Welcome to your dashboard'


@app.route("/tutorial")
def tutorial():
    return render_template('howto.html')

@app.route("/index")
def home():
    return render_template('index.html')

@app.route("/profile")
def profile():
    cur = mysql.connection.cursor()
    cur.execute("select u.name,u.surname,u.age,u.height from users u where u.userID ="+str(session['userID']))
    fetchdata = cur.fetchall()
    cur.execute("SELECT huc.score,huc.date from usercourse uc INNER join historyusercourse huc on huc.userCourseID=uc.userCourseID WHERE uc.userID=%s AND huc.date >= (SELECT ADDDATE(Current_date, INTERVAL -8 DAY)) AND huc.date <  (SELECT ADDDATE(Current_date, INTERVAL 1 DAY))order by huc.date;",str(session['userID']))
    data = cur.fetchall()
    cur.close()
    labels  = [row[1].strftime('%m/%d/%Y') for row in data]
    data = [row[0] for row in data]
    
    return render_template('profile.html',user=fetchdata , labels = labels , data = data)

@app.route("/editProfile")
def editProfile():
    cur = mysql.connection.cursor()
    cur.execute("select u.name,u.surname,u.age,u.height from users u where u.userID ="+str(session['userID']))
    fetchdata = cur.fetchall()
    cur.close()
    return render_template('editProfile.html',user=fetchdata)

@app.route("/save",methods=['POST','GET'])
def saveProfile():
    mesage = ''
    if 'name' in request.form and 'surname' in request.form and 'age' in request.form and 'height' in request.form:
        name = request.form['name']
        surname = request.form['surname']
        age = request.form['age']
        height = request.form['height']
        cur = mysql.connection.cursor()
        if not age.isnumeric():
            mesage = 'age is not number'
        elif not height.isnumeric():
            mesage = 'height is not number'
        else:
            values = (name,surname,int(age),int(height),int(session['userID']))
            cur.execute("Update users set name=%s,surname =%s,age=%s,height=%s where users.userID = %s",values)
            mysql.connection.commit()
            return redirect('/profile')
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return redirect('/editProfile')

@app.route("/select",methods=['POST','GET'])
def select():
    courseId = 1
    cur = mysql.connection.cursor()
    cur.execute("select distinct c.name from course c inner join posture p on p.postureID=c.posture1ID or p.postureID=c.posture2ID")
    fetchdata = cur.fetchall()
    cur.execute("select distinct c.name,c.posture1ID,c.posture2ID,c.courseID from course c inner join posture p on p.postureID=c.posture1ID or p.postureID=c.posture2ID where c.courseID="+str(courseId))
    courseSelected = cur.fetchall()
    cur.execute("select p.name from posture p where p.postureID="+str(courseSelected[0][1]))
    course1 = cur.fetchall()
    cur.execute("select p.name from posture p where p.postureID="+str(courseSelected[0][2]))
    course2 = cur.fetchall()
    # value = (str(session['userID']),str(courseSelected[0][3]))
    # cur.execute("INSERT INTO usercourse(userID,courseID) VALUES(%s,%s)", value)
    # mysql.connection.commit()
    cur.close()
    courseNameSelected = [course1[0],course2[0]]
    return render_template('select.html',course = fetchdata,courseSelected = courseSelected,courseNameSelected = courseNameSelected)

@app.route("/select/<courseName>",methods=['POST','GET'])
def seletedCourse(courseName):
    cur = mysql.connection.cursor()
    cur.execute("select distinct c.name from course c inner join posture p on p.postureID=c.posture1ID or p.postureID=c.posture2ID")
    fetchdata = cur.fetchall()
    cur.execute("select distinct c.name,c.posture1ID,c.posture2ID,c.courseID from course c inner join posture p on p.postureID=c.posture1ID or p.postureID=c.posture2ID where c.name='"+str(courseName)+"'")
    courseSelected = cur.fetchall()
    cur.execute("select p.name from posture p where p.postureID="+str(courseSelected[0][1]))
    course1 = cur.fetchall()
    cur.execute("select p.name from posture p where p.postureID="+str(courseSelected[0][2]))
    course2 = cur.fetchall()
    courseNameSelected = [course1[0],course2[0]]
    # value = (str(session['userID']),str(courseSelected[0][3]))
    # cur.execute("INSERT INTO usercourse(userID,courseID) VALUES(%s,%s)", value)
    # mysql.connection.commit()
    cur.close()
    return render_template('selectedCourse.html',courseSelected = courseSelected,courseNameSelected = courseNameSelected)

# @app.route("/preview/<courseName>",methods=['POST','GET'])
# def preview(courseName):
#     cur = mysql.connection.cursor()
#     cur.execute("select distinct c.name,c.posture1ID,c.posture2ID from course c inner join posture p on p.postureID=c.posture1ID or p.postureID=c.posture2ID where c.name='"+str(courseName)+"'")
#     courseSelected = cur.fetchall()
#     cur.execute("select p.name from posture p where p.postureID="+str(courseSelected[0][1]))
#     course1 = cur.fetchall()
#     cur.execute("select p.name from posture p where p.postureID="+str(courseSelected[0][2]))
#     course2 = cur.fetchall()
#     cur.close()
#     courseNameSelected = [course1[0],course2[0]]
#     return render_template('preview.html',courseSelected = courseSelected,courseNameSelected = courseNameSelected)

@app.route("/playtask1/<courseName>",methods=['POST','GET'])
def playtask1(courseName):
    return render_template('play.html',courseName=courseName)

@app.route("/playtask2/<courseName>",methods=['POST','GET'])
def playtask2(courseName):
    return render_template('play2.html')

def gen():
    
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        rat, frame = cap.read()

        # resizing the frame for better view
        frame = cv2.resize(frame, (640,480))
    
        # Converting the from BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image.flags.writeable = False
        image.flags.writeable = True
    
        # Converting back the RGB image to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        frame = cv2.imencode('.jpeg', image)[1].tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__=="__main__":
    app.run(host='localhost', port=5000, debug=True)
