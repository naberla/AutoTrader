#app.py

from flask import Flask, request #import main Flask class and request object

app = Flask(__name__) #create the Flask app

@app.route('/query-example')
def query_example():
    language = request.args.get('language') #if key doesn't exist, returns None

    return '''<h1>The language value is: {}</h1>'''.format(language)

@app.route('/form-example')
def formexample():
    return 'Todo...'

@app.route('/json-example')
def jsonexample():
    return 'Todo...'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) #run app in debug mode on port 5000
