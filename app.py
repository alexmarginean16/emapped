from functools import wraps
import sys
import os
import io
import json
from flask import Flask, render_template, flash, redirect, request, url_for, session, abort, \
    send_from_directory
#coming from pyrebase4
from werkzeug.utils import secure_filename
import pyrebase
import imghdr
import vision
import maps

#firebase config
jsonfile = open("firebaseconfig.json")
config = json.load(jsonfile)
jsonfile.close()

#init firebase
firebase = pyrebase.initialize_app(config)
#auth instance
auth = firebase.auth()
#real time database instance
db = firebase.database()

#new instance of Flask
app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
#secret key for the session
app.secret_key = os.urandom(24)

#decorator to protect routes
def isAuthenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #check for the variable that pyrebase creates
        if not auth.current_user != None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@isAuthenticated
def index():
    image_names = []
    posts = db.child("Posts").get()
    for post in posts.each():
      city = post.val()['city']
      colors = post.val()['colors']
      email = post.val()['email']
      lables = post.val()['lables']
      name = post.val()['name']
      coordinates = post.val()['coordinates']

      if session["email"] == email:
        image_names.append('photos/' + str(session["email"]) + '/' + name)
    print(image_names)
    return render_template("index.html", email=session["email"], image_names=image_names)

@app.route("/map")
@isAuthenticated
def map():
    try:
      coordinates = [];
      posts = db.child("Posts").get()
      for post in posts.each():
        c = post.val()['coordinates']
        coordinates.append(c)
        print(coordinates)
    except:
      print("Error")

    return render_template("map.html", email=session["email"], coordinates=coordinates)

@app.route("/profile/<email>")
@isAuthenticated
def profile(email):
  loginuser = 0
  if email == session["email"]:
    loginuser = 1
  return render_template('profile.html', email=email, loginuser=loginuser)

#signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
      #get the request form data
      email = request.form["email"]
      password = request.form["password"]
      try:
        #create the user
        auth.create_user_with_email_and_password(email, password)
        #login the user right away
        user = auth.sign_in_with_email_and_password(email, password)
        #session
        user_id = user['idToken']
        user_email = email
        session['usr'] = user_id
        session["email"] = user_email
        os.mkdir('photos/' + user_email)
        return redirect("/")
      except:
        return render_template("login.html", message="The email is already taken, try another one, please" )

    return render_template("signup.html")


#login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
      #get the request data
      email = request.form["email"]
      password = request.form["password"]
      try:
        #login the user
        user = auth.sign_in_with_email_and_password(email, password)
        #set the session
        user_id = user['idToken']
        user_email = email
        session['usr'] = user_id
        session["email"] = user_email
        return redirect("/")

      except:
        return render_template("login.html", message="Wrong Credentials" )


    return render_template("login.html")

#logout route
@app.route("/logout")
def logout():
    #remove the token setting the user to None
    auth.current_user = None
    #also remove the session
    #session['usr'] = ""
    #session["email"] = ""
    session.clear()
    return redirect("/")

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

#upload form
@app.route("/upload", methods=["GET", "POST"])
@isAuthenticated
def upload():
  if request.method == "POST":
    app.config['UPLOAD_PATH'] = 'photos/' + session["email"]
    uploaded_file = request.files["file"]

    filename = secure_filename(uploaded_file.filename)
    if filename != '':
      file_ext = os.path.splitext(filename)[1]
      if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
              file_ext != validate_image(uploaded_file.stream):
              abort(400)
      uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
      client, image = vision.getImage(app.config['UPLOAD_PATH'] + "/" + filename)
      try:
        coordinates = maps.getCoordinates(app.config['UPLOAD_PATH'] + "/" + filename)
        coordinates = tuple(coordinates)
        city = maps.reverseGeocode(coordinates)
      except:
        coordinates = []
        city = ""

      lables = vision.getLables(client, image)
      moods = vision.getMoods(client, image)
      colors = vision.getDominantColors(client, image)
      post = {
        "name": filename,
        "lables": lables,
        "moods": moods,
        "colors": colors,
        "city" : city,
        "coordinates": coordinates,
        "email": session["email"]
      }
      db.child("Posts").push(post)
  return render_template("upload.html")

@app.route("/upload/<filename>")
@isAuthenticated
def send_images(filename):
  return send_from_directory("photos/"+ session["email"], filename)


@app.route("/posts")
@isAuthenticated
def get_photos():
  image_names = os.listdir('photos/' + session["email"])
  # orderedDict = db.child("Posts").get()
  return render_template("post.html", image_names=image_names)



#run the main script
if __name__ == "__main__":
    app.run(debug=True)
