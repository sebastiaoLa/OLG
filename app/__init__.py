from flask import Flask

app = Flask(__name__)
app.secret_key = "d2a57dc1d883fd21fb9951699df71cc7"
from app import views
