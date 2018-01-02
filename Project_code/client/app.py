import requests, os
from flask import Flask, render_template, request, redirect, url_for
from random_words import RandomWords
app = Flask(__name__)

rw = RandomWords()
username = None
voice = False
passwords = {'ashoup':'a'}

@app.route("/", methods=['GET', 'POST'])
def main():
    global username
    if request.method == 'POST':
        usrname = request.form['inputUsrname']
        password = request.form['pswrd']
        if usrname in passwords.keys():
            if passwords[usrname] == password:
                username = usrname
                return redirect(url_for('recognize'))
            else:
                return render_template('login.html', err="password")
        else:
            return render_template('login.html', err="username")
    username=None
    return render_template('login.html', err=None)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        passwords[request.form['inputName']] = request.form['pswrd']
        req = {'username': request.form['inputName']}
        res = requests.post('http://127.0.0.1:5000/register', data=req, files=request.files)
        return redirect(url_for('main'))
    return render_template('recordingInit.html', recordingPhrase=rw.random_word())

@app.route('/recognize', methods=['GET', 'POST'])
def recognize():
    global voice
    global username
    if request.method == 'POST':
        req = {'username':username}
        res = requests.post('http://127.0.0.1:5000/authenticate', data=req, files=request.files)
        #res = requests.post('http://128.30.31.185:5000/authenticate', data=req, files=request.files)
        confidence = int(res.text.split(',')[3].split(":")[1])
        if confidence > 1000:
            voice = True
            return redirect(url_for('loggedIn'))
        return render_template('recognize.html', err="voice")
    if username == None:
        return redirect(url_for('main'))
    else:
        return render_template('recognize.html', err=None)

@app.route('/loggedIn', methods=['GET', 'POST'])
def loggedIn():
    global username
    print username
    global voice
    if request.method == 'POST':
        username = None
        voice = False
        return redirect(url_for('main'))
    if username == None:
        return redirect(url_for('main'))
    if not voice:
            return redirect(url_for('recognize'))
    else:
        return render_template('loggedIn.html', username=username)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
