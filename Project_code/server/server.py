from flask import request
from werkzeug.utils import secure_filename
from flask import Flask
app = Flask(__name__)
app.debug = True
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
config = {
        "database": {
                "host": "127.0.0.1",
                "user": "root",
                "passwd": "",
                "db" : "dejavu",
        }
}

djv = Dejavu(config)
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/recognize', methods=['GET', 'POST'])
def recognize_file():
    if request.method == 'POST':
        print 'got a post request'
        f = request.files['the_file']
        f.save('/home/andrewcao/PycharmProjects/server/tmpfiles/' + secure_filename(f.filename))
        recognizedFile = djv.recognize(FileRecognizer,'/home/andrewcao/PycharmProjects/server/tmpfiles/'+ secure_filename(f.filename))
        print 'found a file', f
        print 'recognized File', recognizedFile
        #djv.fingerprint_file(f)
    	return str(recognizedFile) or 'No file found'

@app.route('/fingerprint', methods=['GET', 'POST'])
def fingerprint_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/home/andrewcao/PycharmProjects/server/tmpfiles/' + secure_filename(f.filename))
        recognizedFile = djv.fingerprint_file('/home/andrewcao/PycharmProjects/server/tmpfiles/'+ secure_filename(f.filename))
        print 'recognized File', recognizedFile
    	return str(recognizedFile) or 'No file found'

@app.route('/register', methods=['POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        file1 = request.files['file1']
	file2 = request.files['file2']
	file3 = request.files['file3']
        #/home/andrewcao/PycharmProjects/server/uploadfiles
        file1.save('/home/andrewcao/PycharmProjects/server/tmpfiles/' + username + '_' + secure_filename(file1.filename))
        recognizedFile = djv.fingerprint_file('/home/andrewcao/PycharmProjects/server/tmpfiles/'+ username + '_' + secure_filename(file1.filename))

        file2.save('/home/andrewcao/PycharmProjects/server/tmpfiles/' + username + '_'+ secure_filename(file2.filename))
        recognizedFile = djv.fingerprint_file('/home/andrewcao/PycharmProjects/server/tmpfiles/'+ username + '_'+ secure_filename(file2.filename))
        file3.save('/home/andrewcao/PycharmProjects/server/tmpfiles/' + username + '_'+ secure_filename(file3.filename))
        recognizedFile = djv.fingerprint_file('/home/andrewcao/PycharmProjects/server/tmpfiles/'+ username + '_'+ secure_filename(file3.filename))
	
    	return str(recognizedFile) or 'User not registered'

@app.route('/authenticate', methods=['POST'])
def authenticate_user():
    if request.method == 'POST':
         username = request.form['username']
         tmpFile = request.files['file']
         tmpFile.save('/home/andrewcao/PycharmProjects/server/uploadfiles/' + secure_filename(tmpFile.filename));

         recognizedFile = djv.recognize(FileRecognizer,'/home/andrewcao/PycharmProjects/server/uploadfiles/'+ secure_filename(tmpFile.filename))
         return str(recognizedFile) or 'Not authenticated'
    return 'Bad method'
	
         
if __name__ == '__main__':
    app.run(host='0.0.0.0')
