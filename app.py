from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

app = Flask(__name__)

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Log Table Datamodel
class Log(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
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

# Token de verificación para la configuración del webhook
TOKEN_EVA = 'EVATOKEN'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)

        return response

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_EVA:
        return challenge
    else:
        return jsonify({'error': 'Token Invalido'}), 401

def recibir_mensajes(req):
    # req = request.get_json()
    # add_messages_log(req)
    # add_messages_log(json.dumps(req))
    
    try:
        req = request.get_json()
        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if 'type' in messages:
                tipo = messages['type']

                if tipo == 'interactive':
                    return 0
                
                if 'text' in messages:
                    text = messages['text']['body']
                    numero = messages['from']
                    add_messages_log(json.dumps(text))
                    add_messages_log(json.dumps(numero))
                    enviar_mensajes_whatsapp(text, numero)

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})

def enviar_mensajes_whatsapp(texto, number):
    texto = texto.lower()

    if 'hola' in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, ¿Cómo estás? Bienvenido."
            }
        }
    elif "1" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
            }
        }
    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "-12.135245519053214",
                "longitude": "-77.02191294280868",
                "name": "UTEC Post-Grado (TechMBA)",
                "address": "Barranco, UTEC Ventures"
            }
        }
    elif "3" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://startup.proinnovate.gob.pe/wp-content/uploads/2023/10/Startup-Peru-10G-Manual-de-Postulacion.pdf",
                "caption": "Temario de curso Capstone",
                "filename": "Startup_Peru_Temario.pdf"
            }
        }
    elif "4" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": "51939927185",
            "type": "audio",
            "audio": {
                "link": "https://download.samplelib.com/mp3/sample-3s.mp3"
            }
        }
    elif "5" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "to": number,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": "Introducción al TechMBA! https://www.youtube.com/watch?v=do_n5y9pjHo"
            }
        }
    elif "6" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🤝🏽 En breve me pondré en contacto contigo. 👱‍♂️"
            }
        }
    elif "7" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🗓️ Horario de atención: Lunes a Viernes. \n🕝 Horario : 9:00 am a 5:00 pm 👱‍♂️"
            }
        }
    elif "0" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita mi web: https://angeltintaya.github.io para más información. \n\n📌 Por favor, ingresa un número #️⃣ para recibir información.\n\n1️⃣. Información del curso. ❔\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar temario en PDF. 📄\n4️⃣. Audio explicando curso. 🎧\n5️⃣. Video de introducción. ⏯️\n6️⃣. Hablar con EvA. 🙋🏻\n7️⃣. Horario de atención. 🕝\n0️⃣. Regresar al menú. 📋"
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita mi web: https://angeltintaya.github.io para más información. \n\n📌 Por favor, ingresa un número #️⃣ para recibir información.\n\n1️⃣. Información del curso. ❔\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar temario en PDF. 📄\n4️⃣. Audio explicando curso. 🎧\n5️⃣. Video de introducción. ⏯️\n6️⃣. Hablar con EvA. 🙋🏻\n7️⃣. Horario de atención. 🕝\n0️⃣. Regresar al menú. 📋"
            }
        }
    
    # Convertir diccionario a formato json
    data = json.dumps(data)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer EAANfFwakcRIBO0YGAmYSJl9gkwFDX6Gl014yk3HcyNKssqmDYL3p0YoMz9XPSf2f0ztzxisWItvKVDlXvkyqONYooZBjvT0QX9rc1azUiFeXHRlfM4z8yBaRN5EusfMWuedSpaItzZBNkZAYqRnfhUeopp2xRiIIceyR2PF5eAPmju6qEr1r4SsRefBSubngGc0cGRS3cKTRZAnhFNZBdf2yI'
    }

    connection = http.client.HTTPSConnection('graph.facebook.com')

    try:
        connection.request('POST', '/v21.0/447962701732006/messages', data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        add_messages_log(json.dumps(e))
    finally:
        connection.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
