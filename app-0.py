from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import eventlet

# Inicializa o Flask e o SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Dicionários para armazenar os usuários e suas conexões
usuarios = {}
usuarios_conectados = {}

# Função para adicionar usuário na interface gráfica
def adicionar_usuario(username, password):
    if username in usuarios:
        messagebox.showerror("Erro", "Usuário já existe.")
    else:
        usuarios[username] = password
        messagebox.showinfo("Sucesso", f"Usuário {username} adicionado com sucesso.")

# Função para remover usuário na interface gráfica
def remover_usuario(username):
    if username in usuarios:
        del usuarios[username]
        messagebox.showinfo("Sucesso", f"Usuário {username} removido com sucesso.")
    else:
        messagebox.showerror("Erro", "Usuário não encontrado.")

# Thread para rodar o servidor Flask com WebSockets
def rodar_servidor():
    socketio.run(app, host=host, port=int(port), debug=False)

# Inicia o servidor Flask no menu
def iniciar_servidor():
    global thread_servidor
    thread_servidor = threading.Thread(target=rodar_servidor)
    thread_servidor.start()
    chat_log.insert(tk.END, f"Servidor iniciado em {host}:{port}\n")

# Para o servidor
def parar_servidor():
    socketio.stop()
    thread_servidor.join()
    chat_log.insert(tk.END, "Servidor parado.\n")

# WebSocket: Lida com a autenticação do cliente
@socketio.on('autenticar')
def handle_autenticacao(data):
    username = data['username']
    password = data['password']
    
    # Autenticação
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

# Função para sair da aplicação
def sair():
    root.destroy()

# Função para configurar Host e Porta
def configurar_host_porta():
    global host, port
    host = simpledialog.askstring("Host", "Digite o Host:", initialvalue=host)
    port = simpledialog.askstring("Porta", "Digite a Porta:", initialvalue=port)

# Interface Gráfica com Tkinter
def criar_interface_servidor():
    global chat_log, root, host, port

    root = tk.Tk()
    root.title("Servidor Flask")

    # Logs do chat
    chat_log = tk.Text(root, state='normal', wrap=tk.WORD, width=50, height=20)
    chat_log.grid(row=0, column=0, padx=10, pady=10)

    # Menu do servidor
    menu = tk.Menu(root)
    root.config(menu=menu)

    servidor_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Servidor", menu=servidor_menu)
    servidor_menu.add_command(label="Ligar", command=iniciar_servidor)
    servidor_menu.add_command(label="Desligar", command=parar_servidor)
    servidor_menu.add_command(label="Sair", command=sair)

    usuarios_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Usuários", menu=usuarios_menu)
    usuarios_menu.add_command(label="Adicionar usuário", command=lambda: adicionar_usuario(simpledialog.askstring("Usuário", "Digite o nome do usuário:"
