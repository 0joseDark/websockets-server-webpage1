from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import threading
import eventlet

eventlet.monkey_patch()

# Inicializa o Flask e o SocketIO para WebSockets
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Dicionário para armazenar os usuários cadastrados e conectados
usuarios = {}
usuarios_conectados = {}

# Função para rodar o servidor Flask em uma thread
def rodar_servidor():
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

# Servir a página web do cliente
@app.route('/')
def index():
    return render_template('index.html')

# WebSocket: Lida com a autenticação dos clientes
@socketio.on('autenticar')
def handle_autenticacao(data):
    username = data['username']
    password = data['password']

    # Verifica se o usuário e a senha são válidos
    if username in usuarios and usuarios[username] == password:
        usuarios_conectados[username] = request.sid
        emit('autenticado', {'status': 'success', 'username': username})
    else:
        emit('autenticado', {'status': 'fail'})

# WebSocket: Lida com mensagens públicas e privadas
@socketio.on('mensagem')
def handle_message(data):
    username = data['username']
    message = data['message']
    recipient = data.get('recipient')

    # Mensagem pública
    if not recipient:
        send({'username': username, 'message': message}, broadcast=True)
    else:
        # Mensagem privada
        recipient_sid = usuarios_conectados.get(recipient)
        if recipient_sid:
            emit('mensagem_privada', {'username': username, 'message': message}, room=recipient_sid)

# WebSocket: Lida com a desconexão do cliente
@socketio.on('disconnect')
def handle_disconnect():
    for user, sid in list(usuarios_conectados.items()):
        if request.sid == sid:
            del usuarios_conectados[user]
            break

if __name__ == "__main__":
    # Adicionar alguns usuários para testar
    usuarios = {
        "user1": "1234",
        "user2": "1234"
    }

    # Rodar o servidor em uma nova thread para que a interface gráfica possa funcionar
    threading.Thread(target=rodar_servidor).start()
