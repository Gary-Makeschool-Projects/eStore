import sys
import os
import socket

try:
    from flask import render_template, Flask, url_for, redirect, request, session, abort, jsonify, flash
    from flask_login import (
        LoginManager,
        current_user,
        login_required,
        login_user,
        logout_user,
    )
    import requests
    from oauthlib.oauth2 import WebApplicationClient
    from smtplib import SMTP_SSL as SMTP
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    from bson import json_util
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import bcrypt
    import json
    from datetime import datetime
    from models import User, Furniture
    from collections import defaultdict
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
    import re

# handle an import error
except ImportError as error:
    print(error, file=sys.stderr)
    print('\x1b[1;31m' + "run pipenv install 'moduleName' " + '\x1b[0m')

try:
    # check to see if the enviornment variable is set and catch the key error if not
    os.environ['FLASK_ENV']
except KeyError as error:
    sys.stdout.write(
        '\x1b[1;31m' + 'set enviornment variable:' + str(error) + '\x1b[0m' + '\n')
finally:
    if 'FLASK_ENV' in os.environ:
        sys.stdout.write('\n')
        sys.stdout.write(
            '\x1b[1;32m' + 'Flask enviornment variable set to: ' + os.environ.get('FLASK_ENV') + '\x1b[0m')
        sys.stdout.write('\n')

app = Flask(__name__)  # app name

# portnum = 8080  # custom port number
# set environment variable
# app.config['SESSION_COOKIE_SECURE'] = True THIS FUCKED ME OVER
# set default mongodb URI
os.environ['MONGO_URI'] = 'mongodb://localhost:27017/contractor'
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
app.config['MONGO_URI'] = host


# os.environ['MONGODB_URI'] = 'mongodb://localhost/contractor'
# host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
# app.config['MONGODB_URI'] = host
# Set the session cookie to be secure

app.config['SECRET_KEY'] = os.urandom(24)
app.secret_key = os.environ.get('SECRET_KEY')
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)
# OAuth 2 client setup
auth = WebApplicationClient(GOOGLE_CLIENT_ID)
# instantiate the database
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database('test')    # get default database name
user = db.user  # user collection
furniture = db.furniture  # furniture collection
base = ''
# hard code the furniture collection into the database
print(base)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    """ Cool index route.
    @GET:
        summary: index endpoint will render file 'index.html'
        description: Get
        responses:
            200:
                description: index.html returned
                schema: indexSchema
            404:
                description: index not found.
    @POST:
        summary:
        description:
        responses:
            200:
                description:
            400:
                description:
    """
    global base
    base = request.base_url

    if 'user' in session:
        if 'ammount' in session:
            # transfer the user session over to the home page
            user = session['user']
            cart = session['ammount']
            username = user['username']
            print(user)
            print(cart)
            return render_template('user_index.html', user=user, cart=cart, username=username)
        else:
            user = session['user']
            cart = user['cart_ammount']
            username = user['username']
            print(user)

            return render_template('user_index.html', user=user, cart=cart, username=username)
    elif 'google_auth' in session:
        google = session['google_auth']
        print(google)
        return "logged in using google"
    else:
        # if there isnt a session return index
        return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Cool register route.
        @GET:
        summary: index endpoint will render file 'index.html'
        description: Get
            responses:
                200:
                    description: index.html returned
                    schema: indexSchema
                404:
                    description: index not found.
        @POST:
            summary:
            description:
            responses:
                200:
                    description:
                400:
                    description:
    """
    if 'user' in session:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            # if we find a user in the database return that user exists and redirect the client to the register form with an error message
            if user.find_one({"email": request.form['email']}):

                return redirect(url_for('register'))

            else:
                if furniture.find_one({'src': 'static/img/bg-img/4.jpg'}):
                    print('not gonna be added')
                else:

                    html = urlopen('https://minimalstore.herokuapp.com/')
                    bs = BeautifulSoup(html, 'html.parser')
                    src = []
                    price = []
                    title = []
                    images = bs.find_all('img', {'src': re.compile('.jpg')})
                    for image in images:
                        price.append(image.get('alt'))
                        src.append(image['src'])
                    names = bs.find_all('h4')
                    for x in names:
                        title.append(x.string)

                    def add(name, price, src):
                        for x in range(len(name)):
                            furniture.insert_one(
                                Furniture(name[x], src[x], price[x]).json())
                    add(title, price, src)

                # if the user doesnt exist add to the user collection and return the users dashboard
                # create new user object with credetials
                new_user = User(
                    request.form['email'], request.form['password'])
                new_user.server_ip = request.remote_addr
                new_user.client_ip = request.environ.get(
                    'HTTP_X_FORWARDED_FOR')
                # insert new user collection to data base
                user_id = user.insert_one(new_user.json()).inserted_id
                # define current user as the new collection
                current_user = user.find_one({"email": request.form['email']})
                # model for persistent data
                data = {
                    'username': current_user['email'],
                    'id': current_user['_id'],
                    'items': current_user['cart'],
                    'created': current_user['created_at'],
                    'ip': current_user['client_ip'],
                    'cart_ammount': len(current_user['cart'])
                }
                # serialize and create the session with session model
                session['user'] = json.loads(json_util.dumps(data))

                # return user dashboard
                return redirect(url_for('index'))

        # if GET method retrun register HTML
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_user = user.find_one({'email': request.form['email']})
        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:

                data = {
                    'username': login_user['email'],
                    'id': login_user['_id'],
                    'created': login_user['created_at'],
                    'items': login_user['cart'],
                    'ip': login_user['client_ip'],
                    'cart_ammount': len(login_user['cart'])
                }

                session['user'] = json.loads(json_util.dumps(data))

                return redirect(url_for('index'))
            else:
                return render_template('login.html', fail='incorrect credentials')

        else:
            return render_template('login.html', fail='incorrect credentials')
    if request.method == 'GET':
        return render_template('login.html')
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():

    session.clear()
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add():
    if 'user' in session:

        username = session['user']['username']
        print(username)
        # find the user in the database
        current_user = user.find_one({'email': username})
        # user cart info
        cart = current_user['cart']
        # find the furniture object the user has clicked on
        current_furniture = furniture.find_one({'src': request.form['src']})

        furniture_id = {'cart': current_furniture['_id']}
        # search the db for the items src and add the id to the furniture_list

        # once the object is found insert this furnitures id into the database

        # update users furniture list with furniture id
        user.update_one(
            {'email': username}, {'$push': furniture_id})
        # structure the json object and create furniture object
        updated_cart = {
            'furniture_list': current_furniture['src']
        }

        updated_user = user.update_one(
            {'email': username}, {'$push': updated_cart})

        new_data = user.find_one({'email': username})
        ammount = len(new_data['cart'])
        session['ammount'] = ammount
        print(session['ammount'])
        return jsonify({'result': 'success', 'cart_ammount': ammount})
    else:
        return 'wtf you looking for'


@app.route('/delete', methods=['POST'])
def delete():
    if 'user' in session:
        # set the current user to the open session
        current_sesh = session['user']
        # find the current user from the session data
        username = current_seh['username']
        # find the user in the data base
        current_user = user.find_one({'email': username})
    else:
        return 'what are you looking for'


@app.route('/cart', methods=['GET'])
def cart():
    if 'user' in session:
        if 'ammount' in session:
            current_user = session['user']
            cart_ammount = session['ammount']

            return render_template('cart.html', cart=cart_ammount)
        else:
            current_user = session['user']
            cart_ammount = current_user['cart_ammount']
            return render_template('cart.html', cart=cart_ammount)
    else:
        return redirect(url_for('index'))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/google")
def google():
    # find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # scopes that let you retrieve user's profile from Google
    request_uri = auth.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/google/callback")
def callback():
    # Get authorization code Google sent back
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens
    token_url, headers, body = auth.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the fucking tokens!
    auth.parse_request_body_response(json.dumps(token_response.json()))
    # user's profile information, including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = auth.add_token(userinfo_endpoint)
    # lets grab that user infos
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # quick sanity check before accessing data
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        print(users_email)
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Doesn't exist? Add it to the database.
    new_user = User(users_email)
    data = {
            'username': str(new_user['email']),
            'id': new_user['_id'],
            'created': new_user['created_at'],
            'items': new_user['cart'],
            'ip': new_user['client_ip'],
            'cart_ammount': len(new_user['cart'])
            }
    # Begin user session by logging the user in

    session['google_auth'] = json.loads(json_util.dumps(data))
    # Send user back to homepage
    return redirect(url_for('index'))


@app.route('/email', methods=['POST'])
def email():
    """ Cool email route.
    @POST:
        summary:
        description:
        responses:
            200:
                description:
            400:
                description:
    """

    server = {
        'gmail': 'smtp.gmail.com',  # gmail smtp server
    }
    # SSL connection port numbers
    SSL_ports = {"lower_port": 465, "high_port": 25025}
    # log debug level
    debug_level = 3
    # generic email string
    mail_content = """Thank you for subscribing to our newsletter :) """

    try:
        server = SMTP(server['gmail'], SSL_ports['lower_port'])
        # set the debug level
        server.set_debuglevel(debug_level)
        # identify ourselves to smtp gmail client

        username = os.environ['email']
        password = os.environ['email_password']
        receiver = request.form['email']
        message = MIMEMultipart()
        message['From'] = username
        message['To'] = receiver
        # The subject line
        message['Subject'] = '(Important) E-store NewsLetter'
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        sys.stdout.write('\x1b[1;32m' + receiver + '\x1b[0m' + '\n')
        server.ehlo()
        server.login(username, password)
        text = message.as_string()
        sys.stdout.write(
            '\x1b[1;32m' + " [+] Connection successful" + '\x1b[0m' + '\n')

        server.sendmail(username, receiver, text)
        server.close()

    except:
        sys.stdout.write(" [x] Connection Failed")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True, host='127.0.0.1',
            port=os.environ.get('PORT', 5000))
