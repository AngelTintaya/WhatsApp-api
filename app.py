from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import http.client
import json
import os
from db_setup import setup_database

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env
setup_database()  # Set up database if not exists

SECRET_TOKEN = os.getenv('SECRET_TOKEN')  # Use your WhatsApp Cloud API access token
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')  # Your WhatsApp number ID

if not SECRET_TOKEN:
    raise ValueError("FLASK_SECRET_TOKEN is not set!")

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

                # Save log in BD
                add_messages_log(json.dumps(messages))

                if tipo == 'interactive':
                    tipo_interactivo = messages['interactive']['type']

                    if tipo_interactivo == 'button_reply':
                        text = messages['interactive']['button_reply']['id']
                        numero = messages['from']

                        enviar_mensajes_whatsapp(text, numero)
                    
                    elif tipo_interactivo == 'list_reply':
                        text = messages['interactive']['list_reply']['id']
                        numero = messages['from']

                        enviar_mensajes_whatsapp(text, numero)
                
                if 'text' in messages:
                    text = messages['text']['body']
                    numero = messages['from']
                    # add_messages_log(json.dumps(text))
                    # add_messages_log(json.dumps(numero))
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
            "to": number,
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
    elif "boton" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "¿Confirmas tu registro?"
                },
                "footer": {
                    "text": "Selecciona una de las opciones"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btnsi",
                                "title": "Si"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btnno",
                                "title": "No"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btntalvez",
                                "title": "Tal vez"
                            }
                        }
                    ]
                }

            }
        }
    elif "btnsi" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Muchas gracias por aceptar."
            }
        }
    elif "btnno" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Es una lástima."
            }
        }
    elif "btntalvez" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Estaré a la espera."
            }
        }
    elif "lista" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": "Selecciona alguna opción"
                },
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte"
                },
                "action": {
                    "button": "Ver opciones",
                    "sections": [
                        {
                            "title": "Compra y venta",
                            "rows": [
                                {
                                    "id": "btncompra",
                                    "title": "Comprar",
                                    "description": "Compra los mejores artículos en tecnología"
                                },
                                {
                                    "id": "btnventa",
                                    "title": "Vender",
                                    "description": "Vende lo que ya no estés usando."
                                }
                            ]
                        },
                        {
                            "title": "Distribución y entrega",
                            "rows": [
                                {
                                    "id": "btndireccion",
                                    "title": "Local",
                                    "description": "Puedes visitar nuestro local."
                                },
                                {
                                    "id": "btnentrega",
                                    "title": "Entrega",
                                    "description": "La entrega se realiza todos los días."
                                }
                            ]

                        }
                    ]
                }

            }
        }
    elif "btncompra" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Los mejores artículos top en ofertas."
            }
        }
    elif "btnventa" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Excelente elección."
            }
        }
    elif "btndireccion" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Te encantará nuestro local."
            }
        }
    elif "btnentrega" in texto:
        data = {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Si no lo recibes a tiempo, el envío es gratis."
            }
        }
    elif "~" in texto:
        name_value, company_value = [t.title() for t in texto.split('~')]
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "template",
            "template": {
                "name": "eva_car_maintenance",
                "language": {
                    "code": "es"
                    },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "parameter_name": "name",
                                "text": name_value
                            },
                            {
                                "type": "text",
                                "parameter_name": "company",
                                "text": company_value
                            }
                        ]
                    }
                ]
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
        'Authorization': f'Bearer {SECRET_TOKEN}'
    }

    connection = http.client.HTTPSConnection('graph.facebook.com')

    try:
        connection.request('POST', f'/v21.0/{PHONE_NUMBER_ID}/messages', data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        add_messages_log(json.dumps(e))
    finally:
        connection.close()

@app.route('/send_first_contact', methods=['GET', 'POST'])
def send_first_contact():
    try:
        data = request.get_json()  # Get the incoming data from the POST request
        
        if 'users' in data and isinstance(data['users'], list):
            users = data['users']
        else:
            return jsonify({'error': 'Invalid input, expected a list of numbers.'}), 400

        # Iterate over the list of numbers and send the message
        for user in users:
            message = '~'.join([user['name'], user['company']])
            enviar_mensajes_whatsapp(message, user['phone_number'])  # You need to implement this function

        return jsonify({'message': f'Messages sent to {len(users)} numbers successfully.'}), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': f'Error occurred while sending messages\n{e}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
