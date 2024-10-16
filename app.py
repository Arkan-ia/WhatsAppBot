#app.py
from flask import Flask, request
import sett 
import chat
from chat import bot  

app = Flask(__name__)


@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
      
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]

        chat.handle_incoming_message(message)
        return 'enviado'

    except Exception as e:
        print('Exception in recibir_mensajes:', str(e))
        return 'no enviado ' + str(e)

if __name__ == '__main__':
    app.run()