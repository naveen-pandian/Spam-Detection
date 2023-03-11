import joblib
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')
from inputScript import FeatureExtraction
model2 = pickle.load(open('Phishing_website.pkl', 'rb'))
from sklearn.feature_extraction.text import TfidfVectorizer

model1=joblib.load('mail.pkl')
feature_extraction=joblib.load('feature_extraction.pkl')

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import smtplib
import re

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'okgoogle'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests

@app.route('/')
@app.route('/spamDetection')
def spamDetection():
    return render_template('spamDetection.html')

@app.route('/spamDetection/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/spamDetection/logout')
def logout():
    # Check if user is loggedin
    if 'loggedin' in session:
        # redirect to confirm page
        return render_template('confirm.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/spamDetection/logout/confirm')
def confirm():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('spamDetection'))


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/spamDetection/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            #send gmail
            gmail_user = 'naveenpandianp5@gmail.com'
            gmail_app_password = 'vqnb putb pfgi ypzi'

            sent_from = gmail_user
            sent_to = email
            sent_subject = "You Get Registered Successfully"
            sent_body = ("Welcome!! New User!!\n\n"+
                         "You Successfully registered to our website SPAM DETECTION !!\n"+
                         "\n"+
                         "Username : {}".format(username)+
                         "\n"+
                         "Password : {}".format(password)+
                         "\n\n"
                         "IV Year CSE,\n"+
                         "NCT\n")

            email_text = """\
            From: %s\nTo: %s\nSubject: %s\n%s
            """ % (sent_from, sent_to, sent_subject, sent_body)
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(gmail_user, gmail_app_password)
                server.sendmail(sent_from, sent_to, email_text)
                server.close()
            except Exception as exception:
                return("Error: %s!\n\n" % exception)

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/spamDetection/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/spamDetection/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/spamDetection/profile/edit')
def edit():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('edit.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/spamDetection/profile/edit/update', methods=['GET', 'POST'])
def update():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Output message if something goes wrong...
        msg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
            username = session['username']
            password = request.form['password']
            email = request.form['email']

            # Check if account exists using MySQL
            cursor.execute('SELECT * FROM accounts WHERE username = %s',(username,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not password or not email:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute('UPDATE accounts SET password=%s ,email=%s WHERE id=%s',(password, email,session['id']))
                mysql.connection.commit()
                #send gmail
                gmail_user = 'naveenpandianp5@gmail.com'
                gmail_app_password = 'vqnb putb pfgi ypzi'

                sent_from = gmail_user
                sent_to = email
                sent_subject = "You Get Updated Successfully"
                sent_body = ("Hi !! {} !!\n\n".format(username)+
                             "You have Successfully updated your profile in our website SPAM DETECTION !!\n"+
                             "\n"+
                             "New email : {}".format(email)+
                             "\n"+
                             "New Password : {}".format(password)+
                             "\n\n"
                             "IV Year CSE,\n"+
                             "NCT\n")

                email_text = """\
                From: %s\nTo: %s\nSubject: %s\n%s
                """ % (sent_from, sent_to, sent_subject, sent_body)
                try:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.ehlo()
                    server.login(gmail_user, gmail_app_password)
                    server.sendmail(sent_from, sent_to, email_text)
                    server.close()
                except Exception as exception:
                    return("Error: %s!\n\n" % exception)

                msg = 'You have successfully updated'

        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('edit.html', msg=msg)
    return redirect(url_for('login'))

@app.route('/spamDetection/about')
def about():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the url page
        return render_template('about.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/spamDetection/about1')
def about1():
    if 'loggedin' in session:
        return render_template('about1.html')
    return redirect(url_for('login'))

@app.route('/spamDetection/about2')
def about2():
    if 'loggedin' in session:
        return render_template('about2.html')
    return redirect(url_for('login'))

@app.route('/spamDetection/contact')
def contact():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the url page
        return render_template('contact.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/spamDetection/mail/')
def mail():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the mail page
        return render_template('mail.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/spamDetection/url/')
def url():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the url page
        return render_template('url.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/spamDetection/mail/predict',methods=['POST'])
def mail_predict():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the mail page
        input_mail=[request.form.get("message")]
        # Convert text to the feature vectors 
        input_data_features = feature_extraction.transform(input_mail)
        # making the prediction
        predictionInput =model1.predict(input_data_features)
        if predictionInput[0] == 1:        
            return render_template("ham.html",prediction_text="It is Ham Message",pred=predictionInput[0],message=input_mail)
        else:
            return render_template("spam.html",prediction_text="It is Spam Message",pred=predictionInput[0],message=input_mail)    

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/spamDetection/url/predict', methods=['GET','POST'])
def url_predict():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the url page
        if request.method=='POST':
            url = request.form['url']
            ob = FeatureExtraction(url)
            z = np.array(ob.getFeaturesList()).reshape(1,30)
            y_pred=model2.predict(z)[0]
            c=model2.predict_proba(z)[0,0]
            f=model2.predict_proba(z)[0,1]
            if(y_pred==1):
                return render_template("leg.html",prediction_text="It is Legitimate safe website",pred=y_pred,url=url)
            else:
                return render_template("phish.html",prediction_text="It is a phishing Website",pred=y_pred,url=url)
        
        else:
            return render_template("url.html")

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)





