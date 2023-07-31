from flask import Flask
import os
import secrets

app = Flask(__name__)

# Set the ALLOWED_HOSTS configuration
app.config['ALLOWED_HOSTS'] = os.environ.get('ALLOWED_HOSTS')

# Set the secret key from an environment variable
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')



@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
