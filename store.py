import sys
import os
import socket

try:
    from flask import render_template, Flask, url_for, redirect, request, session
    from requests import ReadTimeout, RequestException
    from smtplib import SMTP_SSL as SMTP
    # from pymongo import MongoClient
    # from bson.objectid import ObjectId
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

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

    else:
        sys.stdout.write('\n')
        sys.stdout.write(
            '\x1b[1;32m' + 'FLASK_ENV is set to: ' + os.environ.get('FLASK_ENV') + '\x1b[0m' + '\n')
        sys.stdout.write('\n')


portnum = 8080
app = Flask(__name__)  # app name
# db = MongoClient(app)  # db


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def login():
    user = {
        'email': request.form.get('email'),
        'password': request.form.get('password'),
    }

    return render_template('register.html')


@app.route('/email', methods=['POST'])
def email():

    server = {
        'gmail': 'smtp.gmail.com',  # gmail smtp server
    }
    # SSL connection port numbers
    SSL_ports = {"lower_port": 465, "high_port": 25025}
    # TLS connection port numbers
    TLS_ports = {"lower_port": 25, "mid_port": 587,
                 "high_port": 2525}
    debug_level = 3
    mail_content = """Hello,
        This is a simple mail. There is only text, no attachments are there The mail is sent using Python SMTP library.
        Thank You"""

    try:
        server = SMTP(server['gmail'], SSL_ports['lower_port'])
        # set the debug level
        server.set_debuglevel(debug_level)
        # identify ourselves to smtp gmail client

        username = 'gary.frederick@smash.lpfi.org'
        password = os.environ['email_password']
        receiver = request.form['email']
        message = MIMEMultipart()
        message['From'] = username
        message['To'] = receiver
        # The subject line
        message['Subject'] = 'A test mail sent by Python. It has an attachment.'
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
    app.run(debug=True, port=portnum)
