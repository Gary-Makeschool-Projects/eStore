import sys
import os
import socket

try:
    from flask import render_template, Flask, url_for, redirect, request, session, abort, jsonify, flash
    from requests import ReadTimeout, RequestException
    from flask_mongoengine import MongoEngine
    from smtplib import SMTP_SSL as SMTP
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import bcrypt
    import json
    from datetime import datetime
    from models import User

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
    portnum = 8080  # custom port number
    # set environment variable
    os.environ['MONGODB_URI'] = 'mongodb://localhost/contractor'
    host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    app.config['MONGODB_URI'] = host
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
    furniture = db.furniture

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
        if not session.get('logged_in'):
            return render_template('index.html')
        else:
            return render_template('dashboard.html')

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
            new_user = User(request.form['email'], request.form['password'])
            new_user.server_ip = request.environ['REMOTE_ADDR']
            new_user.client_ip = request.environ.get(
                'HTTP_X_REAL_IP', request.remote_addr)
            # if we find a user in the database return that user exists and redirect the client to the register form with an error message
            if user.find_one({"email": request.form['email']}):
                user_exists = True
                flash('user already exists')
                return redirect(url_for('register', user_exists=user_exists))
            else:
               # if the user doesnt exist add to the user collection and return the id of the user
                user.insert_one(new_user.json())
                user_id = user.find_one({"email": new_user.get_email})

                return str(user_id)

        return render_template('register.html')

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
        app.run(debug=True, port=portnum)
    except NameError:
        pass
