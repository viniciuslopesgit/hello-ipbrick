from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import json
import os

load_dotenv()
app = Flask(__name__)




app.secret_key = "app-secret.com"
oauth = OAuth(app)
google = oauth.register(
    name = 'google',
    client_id = os.getenv('GOOGLE_ID'),
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs = {'scope': 'openid profile email'},
)

def load_users():
    with open('./users.json', 'r') as file:
        return json.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return render_template('index.html', error="Usuário ou senha incorretos")
    else:
        return render_template('index.html')

@app.route('/google_login')
def google_login():
    redirect_uri = url_for('google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/google_auth')
def google_auth():
    try:
        token = google.authorize_access_token()
        user_info_resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo', token=token)
        user_info = user_info_resp.json()
        email = user_info.get('email')
        name = user_info.get('name')
        session['google_id'] = user_info.get('sub')
        session['email'] = email
        session['name'] = name
        return redirect(url_for('dashboard'))

    except Exception as e:
        print("Erro durante a autenticação", e)
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if ('username' in session):
        name = session.get("name")
        username = session.get("username")
        return render_template("dashboard.html", username=username, name=name)
    elif ('google_id' in session):
        name = session.get("name")
        email = session.get("email")
        return render_template("dashboard.html", username=email, name=name)
    else:
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)