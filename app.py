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


except ImportError as error:
    print(error, file=sys.stderr)
    print('\x1b[1;31m' + "run pipenv install 'moduleName' " + '\x1b[0m')

try:
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

try:
    app = Flask(__name__)  # app name
except NameError as error:
    pass

try:

    # portnum = 8080  # custom port number
    # set environment variable
    os.environ['MONGODB_URI'] = 'mongodb://localhost/contractor'
    host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    app.config['MONGODB_URI'] = host
    # Set the session cookie to be secure
    app.config['SESSION_COOKIE_SECURE'] = True
    # app.config['secret_key'] = os.urandom(24)
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


except NameError:
    pass

try:
    os.environ['MONGODB_URI']
except KeyError as error:
    print(error)
try:
    # instantiate the database
    client = MongoClient(host=f'{host}?retryWrites=false')
    db = client.get_default_database()    # get default database name
    user = db.user  # user collection
    furniture = db.furniture  # furniture collection

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
        userdata = session.get('user', None)
        if userdata:
            return render_template('user_index.html')
        else:
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
        if request.method == 'POST':
            # if we find a user in the database return that user exists and redirect the client to the register form with an error message
            if user.find_one({"email": request.form['email']}):
                user_exists = True
                return redirect(url_for('register'))
            else:
               # if the user doesnt exist add to the user collection and return the users dashboard
                # create new user object with credetials

                new_user = User(
                    request.form['email'], request.form['password'])
                # new_user.server_ip = request.environ['REMOTE_ADDR']
                # new_user.client_ip = request.environ.get(
                #     'HTTP_X_REAL_IP', request.remote_addr)

                # insert new user collection to data base
                user_id = user.insert_one(new_user.json()).inserted_id
                # define current user as the new collection
                current_user = user.find_one({"email": request.form['email']})

                # model for persistent data
                data = {
                    'username': current_user['email'],
                    'id': current_user['_id'],
                    'created': current_user['created_at'],
                    'furniture': current_user['cart'],
                    'ip': current_user['client_ip'],
                    'cart_ammount': len(current_user['cart'])
                }
                # serialize and create the session with session model
                session['user'] = json.loads(json_util.dumps(data))
                # return user dashboard
                return render_template('user_index.html', cart_ammount=session['user']['cart_amount'], username=session['user']['username'])

        # if GET method retrun register HTML
        return render_template('register.html')

    @app.route('/logout', methods=['GET'])
    def logout():

        session.clear()
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            login_user = user.find_one({'email': request.form['email']})
            if login_user:
                if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
                    data = {
                        'id': login_user['_id'],
                        'created': login_user['created_at'],
                        'items': login_user['cart'],
                        'ip': login_user['client_ip'],
                        'cart_ammount': len(login_user['cart'])
                    }

                    session['user'] = json.loads(json_util.dumps(data))

                    return render_template('user_index.html', id=login_user['_id'], ip=session['user']['ip'], cartammount=session['user']['cart_ammount'], items=session['user']['items'])
                else:
                    return render_template('login.html', fail='incorrect credentials')

            else:
                return render_template('login.html', fail='incorrect credentials')
        if request.method == 'GET':
            return render_template('login.html')
        return render_template('login.html')

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
        # Find out what URL to hit to get tokens that allow you to ask for
        # things on behalf of a user
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        # Prepare and send a request to get tokens! Yay tokens!
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

        # Parse the tokens!
        auth.parse_request_body_response(json.dumps(token_response.json()))
        # user's profile information, including their Google profile image and email
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = auth.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]
        else:
            return "User email not available or not verified by Google.", 400

        # Doesn't exist? Add it to the database.
        new_user = User(email=users_email, password='test')

        # Begin user session by logging the user in
        login_user(new_user)

        # Send user back to homepage
        return render_template('user_index.html')

    @app.route('/add', methods=['POST'])
    def add():
        print(request.form['id'])
        updated_user_id = user.find_one({'_id': request.form['id']})
        updated_data_items = Furniture(
            request.form["name"], request.form["src"], request.form["cost"]).json()
        db.user.update_one({"_id": updated_user_id}, {
                           '$set': updated_data_items})

        return jsonify({'result': 'success'})

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
        debug_level = 3
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


except NameError:
    pass


if __name__ == "__main__":
    try:
        app.secret_key = os.urandom(24)
        app.run(debug=True, host='0.0.0.0',
                port=os.environ.get('PORT', 5000))
    except NameError:
        pass
