from functools import wraps
import sys
import os
import io
from flask import Flask, render_template, redirect, request, url_for, session, abort, \
    send_from_directory
#coming from pyrebase4
from werkzeug.utils import secure_filename
import pyrebase
import imghdr
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "emapped-8b4be6305e9a.json"

client = vision.ImageAnnotatorClient()

#firebase config
config = {

}

#init firebase
firebase = pyrebase.initialize_app(config)
#auth instance
auth = firebase.auth()
#real time database instance
db = firebase.database();


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
    return render_template("index.html", email=session["email"])

@app.route("/map")
@isAuthenticated
def map():
    return render_template("map.html", email=session["email"])

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
        auth.create_user_with_email_and_password(email, password);
        #login the user right away
        user = auth.sign_in_with_email_and_password(email, password)
        #session
        user_id = user['idToken']
        user_email = email
        session['usr'] = user_id
        session["email"] = user_email
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
    return redirect("/");

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

#create form
@app.route("/upload", methods=["GET", "POST"])
@isAuthenticated
def upload():
  if request.method == "POST":
    if os.path.isdir('photos/' + session["email"]):
      app.config['UPLOAD_PATH'] = 'photos/' + session["email"]
      #get the request data
      uploaded_file = request.files["upload"]
      filename = secure_filename(uploaded_file.filename)
      path = "photos/" + session["email"] + "/" + filename
      # file_name = os.path.abspath('/photos/' + session["email"] + "/" + uploaded_file.filename)
      with io.open(path, 'rb') as image_file:
        content = image_file.read();

      image = vision.Image(content=content)

      # Performs label detection on the image file
      response = client.label_detection(image=image)
      labels = response.label_annotations

      tags = []
      for label in labels:
          tags.append(str(label.description))

      print(tags)

      # Performs face detection on the image file
      response = client.face_detection(image=image)
      faces = response.face_annotations

      likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY')

      moods = []

      for face in faces:
        mood = []
        mood.append('Joy')
        mood.append(likelihood_name.index(likelihood_name[face.joy_likelihood]))
        moods.append(mood)

        mood = []
        mood.append('Sorrow')
        mood.append(likelihood_name.index(likelihood_name[face.sorrow_likelihood]))
        moods.append(mood)

        mood = []
        mood.append('Anger')
        mood.append(likelihood_name.index(likelihood_name[face.anger_likelihood]))
        moods.append(mood)

        mood = []
        mood.append('Surprise')
        mood.append(likelihood_name.index(likelihood_name[face.surprise_likelihood]))
        moods.append(mood)

     # filename = secure_filename(uploaded_file.filename)
      if filename != '':
          file_ext = os.path.splitext(filename)[1]
          if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                  file_ext != validate_image(uploaded_file.stream):
              abort(400)
          uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    else:
      os.makedirs('photos/' + session["email"])

  return render_template("upload.html", email = session["email"])

@app.route("/post")
@isAuthenticated
def post():
    pics = os.listdir('photos/' + session["email"])
    for photo in pics:
      image = Image.open('photos/' + session["email"]+ "/" + photo)
      for (tag,value) in image._getexif().iteritems():
        print (TAGS.get(tag), value)
    return render_template("post.html", pics = pics)


#run the main script
if __name__ == "__main__":
    app.run(debug=True)
