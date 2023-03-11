import numpy as np
from flask import Flask, request, render_template, Response , jsonify, make_response , session, redirect, flash
import jwt
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from functools import wraps
import pickle
import cv2

app = Flask(__name__)

app.config['SECRET_KEY'] = 'x123'
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=20)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)

@app.route('/')
def index():
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

# User Database Route
# this route sends back list of users
@app.route('/user', methods =['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    cur = mysql.connection.cursor()
    cur.execute("select u.userIdu.name,u.email from users u")
    fetchdata = cur.fetchall()
    cur.close()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'public_id': user.public_id,
            'name' : user.name,
            'email' : user.email
        })
  
    return jsonify({'users': output})

@app.route('/login', methods=['POST'])
def login():
    error = None
    cur = mysql.connection.cursor()
    cur.execute("select u.username,u.password,u.email from users u")
    fetchdata = cur.fetchall()
    cur.close()
    for data in fetchdata:      
        if request.form['username'] == data[0] and request.form['password'] == data[1]:
            session['logged_in'] = True
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
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
        

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

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    if(checkUsername(username)):
        return 'username exist'
    password = request.form['password']
    email = request.form['email']
    confirmPassword = request.form['confirmPassword']
    if (password != confirmPassword):
        return 'not match password'
    name = request.form['name']
    surname = request.form['surname']
    age = request.form['age']
    values = (email,username,password,name,surname,age)
    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO users(email,username,password,name,surname,age) VALUES(%s,%s,%s,%s,%s,%s)", values)
    mysql.connection.commit()
    cur.close()
    return redirect("/", code=302)


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in',False)
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
    cur.execute("select u.name,u.surname from users u")
    fetchdata = cur.fetchall()
    cur.close()
    #return render_template('profile.html')
    return jsonify(session)

@app.route("/select")
def select():
    return render_template('select.html')

@app.route("/preview")
def preview():
    return render_template('preview.html')

@app.route("/play",methods=['POST','GET'])
def play():
    return render_template('play.html')

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
