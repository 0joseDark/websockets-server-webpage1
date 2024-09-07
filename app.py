from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Dicionário para armazenar usuários conectados
usuarios_conectados = {}

@app.route('/')
def index():
    return render_template('index.html')

# WebSocket: Lida com eventos de conexão
@socketio.on('connect')
def handle_connect():
    print('Um cliente conectou')

# WebSocket: Lida com eventos de autenticação
@socketio.on('autenticar')
def handle_autenticacao(data):
    username = data['username']
    password = data['password']

    # Simula autenticação com senha "1234" para todos
    if password == "1234":
        usuarios_conectados[username] = request.sid
        emit('autenticado', {'status': 'success', 'username': username})
    else:
        emit('autenticado', {'status': 'fail'})

# WebSocket: Lida com eventos de mensagens
@socketio.on('mensagem')
def handle_message(data):
    username = data['username']
    message = data['message']
    recipient = data.get('recipient')

    # Mensagem pública
    if not recipient:
        send({'username': username, 'message': message}, broadcast=True)

    # Mensagem privada
    else:
        recipient_sid = usuarios_conectados.get(recipient)
        if recipient_sid:
            emit('mensagem_privada', {'username': username, 'message': message}, room=recipient_sid)

# WebSocket: Lida com a desconexão do cliente
@socketio.on('disconnect')
def handle_disconnect():
    print('Um cliente desconectou')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
