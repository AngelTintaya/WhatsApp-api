from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Log Table Datamodel
class Log(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow())
    texto = db.Column(db.TEXT)

# Creating table if not exists
with app.app_context():
    db.create_all()

    """
    prueba1 = Log(texto = 'Mensaje de prueba 1')
    prueba2 = Log(texto = 'Mensaje de prueba 2')

    db.session.add(prueba1)
    db.session.add(prueba2)
    db.session.commit()
    """

# Function to order records by datetime
def order_by_date(records):
    return sorted(records, key=lambda x: x.fecha_y_hora, reverse=True)

@app.route('/')
def index():
    # Get all records from database
    records = Log.query.all()
    ordered_records = order_by_date(records)
    return render_template('index.html', records=ordered_records)

message_log = []

# Function to add messages and store in database
def add_messages_log(texto):
    message_log.append(texto)

    # Save message in database
    new_record = Log(texto=texto)
    db.session.add(new_record)
    db.session.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
