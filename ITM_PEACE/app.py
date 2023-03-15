import numpy as np
from flask import Flask, request, render_template, Response , jsonify, Blueprint , session, redirect, flash
import jwt
import re
import math
from flask_mysqldb import MySQL
from datetime import datetime, timedelta , date
from functools import wraps
import pickle
import cv2
import mediapipe as mp
import pandas as pd
import pickle 
import joblib
import time

app = Flask(__name__)

app.config['SECRET_KEY'] = 'x123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'itmdb' #name DB

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
    try:
        cur = mysql.connection.cursor()
        cur.execute("select u.username,u.password,u.email,u.userID from users u where u.username = '"+str(request.form['username'])+"' and u.password ='"+str(request.form['password'])+"'")
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
                return redirect("/index", code=302)
            else: 
                flash(u'Invalid password provided', 'error')
                return render_template("login.html")
    except:
        flash(u'Invalid password provided', 'error')
        return render_template("login.html")
        

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
    #return jsonify('logged_in' in session)
    return redirect("/", code=302)

#Authen
@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified. Welcome to your dashboard'


@app.route("/tutorial")
def tutorial():
    if 'logged_in' in session:
        return render_template('howto.html')
    else:
        return redirect('/')

@app.route("/index")
def home():
    if 'logged_in' in session:
        return render_template('index.html')
    else:
        return redirect('/')

@app.route("/profile")
def profile():
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("select u.name,u.surname,u.age,u.height from users u where u.userID ="+str(session['userID']))
        fetchdata = cur.fetchall()
        cur.execute("SELECT sum(huc.timer)/60,huc.date from usercourse uc INNER join historyusercourse huc on huc.userCourseID=uc.userCourseID WHERE uc.userID=%s AND huc.date >= (SELECT ADDDATE(Current_date, INTERVAL -8 DAY)) AND huc.date <  (SELECT ADDDATE(Current_date, INTERVAL 1 DAY)) group by huc.date  order by huc.date;",str(session['userID']))
        data = cur.fetchall()
        cur.close()
        labels  = [row[1].strftime('%m/%d/%Y') for row in data]
        data = [row[0] for row in data]
        # return jsonify(type(data))
        return render_template('profile.html',user=fetchdata , labels = labels , data = data)
    else:
        return redirect('/')

@app.route("/editProfile")
def editProfile():
    if 'logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("select u.name,u.surname,u.age,u.height from users u where u.userID ="+str(session['userID']))
        fetchdata = cur.fetchall()
        cur.close()
        return render_template('editProfile.html',user=fetchdata)
    else:
        return redirect('/')

@app.route("/save",methods=['POST','GET'])
def saveProfile():
    if 'logged_in' in session:
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
    else:
        return redirect('/')

@app.route("/select",methods=['POST','GET'])
def select():
    if 'logged_in' in session:
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
        value = (str(session['userID']),str(courseSelected[0][3]))
        cur.execute("INSERT INTO usercourse(userID,courseID) VALUES(%s,%s)", value)
        mysql.connection.commit()
        cur.close()
        courseNameSelected = [course1[0],course2[0]]
        return render_template('select.html',course = fetchdata,courseSelected = courseSelected,courseNameSelected = courseNameSelected)
    else:
        return redirect('/')

@app.route("/select/<courseName>",methods=['POST','GET'])
def seletedCourse(courseName):
    if 'logged_in' in session:
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
        value = (str(session['userID']),str(courseSelected[0][3]))
        cur.execute("INSERT INTO usercourse(userID,courseID) VALUES(%s,%s)", value)
        mysql.connection.commit()
        cur.close()
        return render_template('selectedCourse.html',courseSelected = courseSelected,courseNameSelected = courseNameSelected)
    else:
        return redirect('/')

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
    if 'logged_in' in session:
        global courseSelect,nowCourse,stage
        setDefault()
        setNumCountGoal()
        if(courseName == "เบาสบายกายขยับ"):
            courseSelect = 0
            nowCourse = course[courseSelect][status]
        elif (courseName == "กำหมัดสลัดเหงื่อ"):
            courseSelect = 1
            nowCourse = course[courseSelect][status]
        return render_template('play.html',courseName=courseName,count = count,nowCourse = nowCourse,stage = stage) 
    else:
        return redirect('/')

@app.route('/exercise',methods=['POST','GET'])
def exercise():
    if 'logged_in' in session:
        global count,stage
        return render_template('count.html',count=count,nowCourse = nowCourse,stage = stage)
    else:
        return redirect('/')
    


@app.route('/result/<courseName>',methods=['POST','GET'])
def result(courseName):
    if 'logged_in' in session:
        min = 0
        sec = elapsed_time
        if elapsed_time >=60 :
            min = math.floor(elapsed_time/60)
            sec = elapsed_time - math.floor(60*min)
        cur = mysql.connection.cursor()
        cur.execute("select distinct c.courseID from course c inner join posture p on p.postureID=c.posture1ID or p.postureID=c.posture2ID where c.name='"+str(courseName)+"'")
        courseSelected = cur.fetchall()
        cur.execute("select max(uc.userCourseID) from usercourse uc where uc.userID='"+str(session['userID'])+"' and uc.courseID='"+str(courseSelected[0][0])+"'")
        userCourse = cur.fetchall()
        value = (str(userCourse[0][0]),score,elapsed_time)
        cur.execute("INSERT INTO historyusercourse(userCourseID,score,timer) VALUES(%s,%s,%s)", value)
        mysql.connection.commit()
        cur.close()
        return render_template('result.html',score = score,min = min,sec = math.floor(sec))
    else:
        return redirect('/')


modelHandUp=pickle.load(open(r"model/handup_model.pkl", 'rb'))
modelWaistFeetAndLegRaises=pickle.load(open(r"model/waistFeetAndLegRaises.pkl", 'rb'))
modelStompingAndBent=pickle.load(open(r"model/stompingAndBent.pkl", 'rb'))
modelStretchOutAndStepBack=pickle.load(open(r"model/stretchOutAndStepBack.pkl", 'rb'))
modelFistAndStride=pickle.load(open(r"model/fistAndStride.pkl", 'rb'))

# Grabbing the Holistic Model from Mediapipe and
mp_holistic = mp.solutions.holistic

# Initializing the Model
holistic_model = mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
 
# Initializing the drawing utils for drawing the facial landmarks on image
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def calculateScore():
    global elapsed_time,score
    if(elapsed_time<=360):
        score = 100
    elif(elapsed_time>360 and elapsed_time<=600):
        score = 70
    else: 
        score = 50

def setZero():
    global stage,step,count,status
    stage = 1
    step = 0
    status+=1
    count=0

def setNumCountGoal():
    global numCountGoal
    cur = mysql.connection.cursor()
    cur.execute("select u.age from users u where u.userID ="+str(session['userID']))
    fetchdata = cur.fetchall()
    cur.close()
    age = int(fetchdata[0][0])
    if(age >=60 and age <65):
        numCountGoal = 0
    elif (age >=65 and age <70):
        numCountGoal = 1
    elif (age >=70):
        numCountGoal = 2
    else:
        numCountGoal = 3

def setDefault():
    global course,courseSelect,status,stage,step,count,countGoal,start_time,elapsed_time,restStage,nowCourse,score
    status = 0
    stage = 1
    step = 0
    count = 0
    elapsed_time = 0
    score = 0
    restStage = True
    start_time = time.time()


# Course
#courseA = ["LagRaises","rest","StompingAndBent","end"]
courseA = ["waistRaises","rest","stompingAndBent","end"]
courseB = ["fistAndStride","rest","stretchAndBack","end"]
course = [courseA,courseB]

# initialize the golbal value
courseSelect = 0
status = 0
stage = 1
step = 0
count = 0
elapsed_time = 0
score = 0
restStage = True
#mpModel=[modelLagRaises,modelStompingAndBent,modelHandUp,modelHandUp]
mpModel=[modelWaistFeetAndLegRaises,modelStompingAndBent,modelFistAndStride,modelStretchOutAndStepBack]
countGoal = [15,10,5,30]
numCountGoal = 0
start_time = time.time()

# set course
nowCourse = course[courseSelect][status]

def gen():
    # model global variable
    global mp_holistic,holistic_model,mp_drawing,mp_drawing_styles,mpModel
    
    # global variable
    global course,courseSelect,status,stage,step,count,countGoal,start_time,elapsed_time,restStage,nowCourse,score,numCountGoal
    
    # (0) in VideoCapture is used to connect to your computer's default camera
    capture = cv2.VideoCapture(0)

    while capture.isOpened():
        # capture frame by frame
        ret, frame = capture.read()

        elapsed_time = time.time() - start_time

        # resizing the frame
        frame = cv2.resize(frame, (860,645))
        
        frame = cv2.flip(frame, 1)

        # Converting the from BGR to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Making predictions using holistic model
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False

        results = holistic_model.process(image)

        image.flags.writeable = True

        # Converting back the RGB image to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # # drawing skeleton
        # mp_drawing.draw_landmarks(
        #     image, 
        #     results.pose_landmarks, 
        #     mp_holistic.POSE_CONNECTIONS,   
        #     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        # )

        # model loader
        if(nowCourse==course[0][0]):
            model = mpModel[0]
        elif(nowCourse==course[0][2]):
            model = mpModel[1]
        elif(nowCourse==course[1][0]):
            model = mpModel[2]
        elif(nowCourse==course[1][2]):
            model = mpModel[3]
        else:
            pass
        
        # personal box
        # represents the top left corner of rectangle 
        start_point = (200, 10)

        # represents the bottom right corner of rectangle
        end_point = (680, 630)

        # Line thickness of 2 px
        thickness = 4

        try:
            pose = results.pose_landmarks.landmark
            pose_row = list(np.array([[landmark.x,landmark.y,landmark.z,landmark.visibility] for landmark in pose]).flatten())

            # Make Detections
            X = pd.DataFrame([pose_row])
            predict_class = model.predict(X)[0]
            predict_prob = model.predict_proba(X)[0]

            # rest stage
            if(nowCourse=="rest"):
                if(restStage):
                    start_sw = time.time()
                    stop_watch = 0
                    restStage = False

                # calculate elapsed time
                sw_time = time.time() - start_sw
                stop_watch = int(30-sw_time)
                if(stop_watch>=0):
                    if(stop_watch>=10):
                        cv2.putText(image, f"{stop_watch}"
                            , (270,400), cv2.FONT_HERSHEY_SIMPLEX, 8, (0, 0, 255), 8, cv2.LINE_AA)
                    else:
                        cv2.putText(image, f"{stop_watch}"
                            , (340,400), cv2.FONT_HERSHEY_SIMPLEX, 8, (0, 0, 255), 8, cv2.LINE_AA)
                else:
                    setZero()
                    nowCourse=course[courseSelect][status]
                    
            elif(nowCourse=="end"):
                calculateScore()
                # comemnt ----
                if(score==3):
                    str_medal = "SO FIT"
                elif(score==2):
                    str_medal = "SO STRONG"
                elif(score==1):
                    str_medal = "SO GOOD"
                cv2.putText(image, str_medal
                        , (270,250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8, cv2.LINE_AA)
                # -----
                
            # A Course
            elif(nowCourse==course[0][0]):
                if(count==countGoal[numCountGoal]):
                    setZero()
                    nowCourse=course[courseSelect][status]
                if(stage == 1 and predict_class=="wflr1" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    if(step==0):
                        step = 1
                    elif(step==1):
                        stage = 2
                    elif(step==2):
                        stage = 3
                elif(stage == 2 and predict_class=="wflr2" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    step=2
                    stage = 1
                elif(stage == 3 and predict_class=="wflr3" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    count+=1
                    step = 0
                    stage = 1
            elif(nowCourse==course[0][2]):
                if(count==countGoal[numCountGoal]):
                    # End here
                    setZero()
                    nowCourse=course[courseSelect][status]
                if(stage == 1 and predict_class=="sab1" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    stage = 2
                elif(stage == 2 and predict_class=="sab2" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    count+=1
                    stage = 1 
            # B course
            elif(nowCourse==course[1][0]):
                if(count==countGoal[numCountGoal]):
                    setZero()
                    nowCourse = course[courseSelect][status]
                if(stage == 1 and predict_class=="fas1" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    if(step==0):
                        step = 1
                    elif(step==1):
                        stage = 2
                    elif(step==2):
                        stage = 3
                elif(stage == 2 and predict_class=="fas2" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    step=2
                    stage = 1
                elif(stage == 3 and predict_class=="fas3" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    count+=1
                    step = 0
                    stage = 1
            elif(nowCourse==course[1][2]):
                if(count==countGoal[numCountGoal]):
                    # ending here
                    setZero()
                    nowCourse=course[courseSelect][status]
                if(stage == 1 and predict_class=="ss1" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    if(step==0):
                        step = 1
                    elif(step==1):
                        stage = 2
                    elif(step==2):
                        stage = 3
                elif(stage == 2 and predict_class=="ss2" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    step=2
                    stage = 1
                elif(stage == 3 and predict_class=="ss3" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.30):
                    count+=1
                    step = 0
                    stage = 1
                    
            # Using cv2.rectangle() method
            # Draw a rectangle with blue line borders of thickness of 2 px
            cv2.rectangle(image, start_point, end_point, (0,255,0), 5)


            # # if you don't want to show any status comment from here ----------
            # str_count = f"{nowCourse} + {count}"
            # # Get status box
            # cv2.rectangle(image, (0,0), (500, 60), (255, 255, 255), -1)

            # # Display Count Sign
            # cv2.putText(image, "[ Status ]"
            #             , (48,500), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)

            # # Display Count
            # cv2.putText(image, str_count
            #             , (48,570), cv2.FONT_HERSHEY_SIMPLEX, 2, (123, 45, 222), 5, cv2.LINE_AA)

            # # Display Class
            # cv2.putText(image, 'CLASS'
            #             , (95,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (123, 45, 222), 1, cv2.LINE_AA)
            # cv2.putText(image, predict_class.split(' ')[0]
            #             , (90,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (123, 45, 222), 2, cv2.LINE_AA)

            # # Display Probability
            # cv2.putText(image, 'PROB'
            #             , (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (123, 45, 222), 1, cv2.LINE_AA)
            # cv2.putText(image, str(round(predict_prob[np.argmax(predict_prob)],2))
            #             , (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (123, 45, 222), 2, cv2.LINE_AA)

            # # Display Timer
            # cv2.putText(image, 'TIME'
            #             , (300,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (123, 45, 222), 1, cv2.LINE_AA)
            # cv2.putText(image, f"{int(elapsed_time)} Sec"
            #             , (350,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (123, 45, 222), 2, cv2.LINE_AA)

            # # to here ------

        except:
            # Using cv2.rectangle() method
            # Draw a rectangle with blue line borders of thickness of 2 px
            cv2.rectangle(image, start_point, end_point, (0,0,255), thickness)

        frame = cv2.imencode('.jpeg', image)[1].tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
@app.route('/video_feed',methods=['POST','GET'])
def video_feed():
    if 'logged_in' in session:
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return redirect('/')


if __name__=="__main__":
    app.run(host='localhost', port=5000, debug=True)
