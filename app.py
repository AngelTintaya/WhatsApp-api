from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# SQLite Database Configuration
app.config('SQLALCHEMY_DATABASE_URI') = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Log Table Datamodel
class log(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.Datetime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

@app.route('/')

def hola_mundo():
    return render_template('holaflask.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
