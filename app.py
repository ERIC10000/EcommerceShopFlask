# Client-server
# Framework
# Flask
# request-response

# Client -> Listen to server response, send request to the server (webbrowser)
# Server -> Process client requests, sends response to the client (flask application)

# Framewok, make development easy, by utilizing reusable code...., flask, django

from flask import Flask, render_template, sessions, request

# start
app = Flask(__name__)


# decorators (@)
# flask routing
# method-> route()
# to bind the method route to our app object, then we use decorator @
@app.route('/home')
def home_page():
    return "Hello Welcome to Flask"


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def sign_up():
    return "This is the signup page"


@app.route('/')
def index():
    return "View index Page Here!"


@app.route('/add')
def add():
    fruits = ['mango', 'orange']
    return fruits


app.run(debug=True)
# End
