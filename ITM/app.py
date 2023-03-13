import numpy as np
from flask import Flask, request, render_template, Response , jsonify, Blueprint , session, redirect, flash
import jwt
import re
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
    global courseSelect,nowCourse
    setDefault()
    if(courseName == "AB"):
        courseSelect = 0
        nowCourse = course[courseSelect][status]
    elif (courseName == "CD"):
        courseSelect = 1
        nowCourse = course[courseSelect][status]
    return render_template('play.html',courseName=courseName,count = count) 

@app.route('/exercise',methods=['POST','GET'])
def exercise():
    return render_template('count.html',count=count)


modelHandUp=pickle.load(open("model/handup_model.pkl", 'rb'))
modelstompingAndBent=pickle.load(open("model/stompingAndBent.pkl", 'rb'))
modelfistAndStride=pickle.load(open("model/fistAndStride.pkl", 'rb'))

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
#     if(elapsed_time<=360):
#         score = 3
#     elif(elapsed_time>360 and elapsed_time<=600):
#         score = 2
#     else: 
#         score = 1
    if(score==0):
        if(elapsed_time<=20):
            score = 3
        elif(elapsed_time>20 and elapsed_time<=25):
            score = 2
        else: 
            score = 1

def setZero():
    global stage,step,count,status
    stage = 1
    step = 1
    status+=1
    count=0

def setDefault():
    global course,courseSelect,status,stage,step,count,countGoal,start_time,elapsed_time,restStage,nowCourse,score
    status = 0
    stage = 1
    step = 1
    count = 0
    elapsed_time = 0
    score = 0
    restStage = True
    start_time = time.time()


# Course
courseA = ["stompingAndBent","rest","fistAndStride","end"]
courseB = ["handUpA","rest","handUpB","end"]
course = [courseA,courseB]

# initialize the golbal value
status = 0
stage = 1
step = 1
count = 0
elapsed_time = 0
score = 0
restStage = True
mpModel=[modelstompingAndBent,modelfistAndStride,modelHandUp,modelHandUp]
countGoal = [2,10,15]
start_time = time.time()

courseSelect = 1

# set course
nowCourse = course[courseSelect][status]

def gen():
     # model global variable
    global mp_holistic,holistic_model,mp_drawing,mp_drawing_styles,mpModel
    
    # global variable
    global course,courseSelect,status,stage,step,count,countGoal,start_time,elapsed_time,restStage,nowCourse,score
    
    # (0) in VideoCapture is used to connect to your computer's default camera
    capture = cv2.VideoCapture(0)

    while capture.isOpened():
        # capture frame by frame
        ret, frame = capture.read()

        elapsed_time = time.time() - start_time

        # resizing the frame
        frame = cv2.resize(frame, (860,645))

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

        # drawing skeleton
        mp_drawing.draw_landmarks(
            image, 
            results.pose_landmarks, 
            mp_holistic.POSE_CONNECTIONS,   
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )

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
                stop_watch = int(3-sw_time)
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
                if(count==countGoal[0]):
                    setZero()
                    nowCourse=course[courseSelect][status]
                if(stage == 1 and predict_class=="sab1" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.55):
                    stage = 2
                elif(stage == 2 and predict_class=="sab2" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.55):
                    count+=1
                    stage = 1
            elif(nowCourse==course[0][2]):
                if(count==countGoal[0]):
                    # End here
                    nowCourse=course[courseSelect][status]
                if(stage == 1 and predict_class=="fas1" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.7):
                    if(step==1):
                        stage = 2
                    if(step==2):
                        stage = 3
                    if(step==3):
                        count+=1
                        step = 1
                elif(stage == 2 and predict_class=="fas2" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.4):
                    stage = 1
                    step = 2
                elif(stage == 3 and predict_class=="fas3" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.4):
                    step = 3
                    stage = 1 
            # B course
            elif(nowCourse==course[1][0]):
                if(count==countGoal[0]):
                    setZero()
                    nowCourse = course[courseSelect][status]
                if(stage == 1 and predict_class=="left_hand" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.75):
                    stage = 2
                elif(stage == 2 and predict_class=="right_hand" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.75):
                    count+=1
                    stage = 1
            elif(nowCourse==course[1][2]):
                if(count==countGoal[0]):
                    # ending here
                    setZero()
                    nowCourse=course[courseSelect][status]
                if(stage == 1 and predict_class=="right_hand" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.75):
                    stage = 2
                elif(stage == 2 and predict_class=="left_hand" and round(predict_prob[np.argmax(predict_prob)],2) >= 0.75):
                    count+=1
                    stage = 1


            # personal box
            # represents the top left corner of rectangle 
            start_point = (200, 10)

            # represents the bottom right corner of rectangle
            end_point = (680, 630)

            # Blue color in BGR
            color = (0,255,255)

            # Line thickness of 2 px
            thickness = 4

            # Using cv2.rectangle() method
            # Draw a rectangle with blue line borders of thickness of 2 px
            cv2.rectangle(image, start_point, end_point, color, thickness)


            # if you don't want to show any status comment from here ----------
            str_count = f"{nowCourse} + {count}"
            # Get status box
            cv2.rectangle(image, (0,0), (400, 60), (255, 255, 255), -1)

            # Display Count Sign
            cv2.putText(image, "[ Status ]"
                        , (48,500), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)

            # Display Count
            cv2.putText(image, str_count
                        , (48,570), cv2.FONT_HERSHEY_SIMPLEX, 2, (123, 45, 222), 5, cv2.LINE_AA)

            # Display Class
            cv2.putText(image, 'CLASS'
                        , (95,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, predict_class.split(' ')[0]
                        , (90,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Display Probability
            cv2.putText(image, 'PROB'
                        , (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(round(predict_prob[np.argmax(predict_prob)],2))
                        , (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Display Timer
            cv2.putText(image, 'TIME'
                        , (300,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, f"{int(elapsed_time)} Sec"
                        , (250,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # to here ------

        except:
            cv2.putText(image, str('Out Of Frame')
                        , (210,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        frame = cv2.imencode('.jpeg', image)[1].tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
@app.route('/video_feed',methods=['POST','GET'])
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__=="__main__":
    app.run(host='localhost', port=5000, debug=True)
