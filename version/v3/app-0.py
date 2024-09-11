import eventlet
eventlet.monkey_patch()  # Certifique-se de que o Eventlet faz o patch corretamente

from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading

# Inicializa o Flask e o SocketIO com o modo 'eventlet'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

# Dicionários para armazenar os usuários e conexões
usuarios = {}
usuarios_conectados = {}

# Função para rodar o servidor Flask com WebSockets
def rodar_servidor():
    socketio.run(app, host=host, port=int(port))

# Servir a página web do cliente
@app.route('/')
def index():
    return render_template('index.html')

# WebSocket: Lida com a autenticação dos clientes
@socketio.on('autenticar')
def handle_autenticacao(data):
    username = data['username']
    password = data['password']

    # Verifica se o usuário e senha estão corretos
    if username in usuarios and usuarios[username] == password:
        usuarios_conectados[username] = request.sid  # Armazena a sessão conectada
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
        # Mensagem privada para destinatário
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

# Função para iniciar o servidor via interface gráfica
def iniciar_servidor():
    global thread_servidor
    thread_servidor = threading.Thread(target=rodar_servidor)
    thread_servidor.start()
    chat_log.insert(tk.END, f"Servidor iniciado em {host}:{port}\n")

# Função para parar o servidor via interface gráfica
def parar_servidor():
    socketio.stop()  # Para o SocketIO
    chat_log.insert(tk.END, "Servidor parado.\n")

# Função para adicionar usuário via interface gráfica
def adicionar_usuario():
    username = simpledialog.askstring("Usuário", "Digite o nome do usuário:")
    password = simpledialog.askstring("Senha", "Digite a senha:")
    if username and password:
        usuarios[username] = password
        messagebox.showinfo("Sucesso", f"Usuário {username} adicionado com sucesso.")
    else:
        messagebox.showerror("Erro", "Preencha corretamente o nome de usuário e a senha.")

# Função para remover usuário via interface gráfica
def remover_usuario():
    username = simpledialog.askstring("Usuário", "Digite o nome do usuário para remover:")
    if username in usuarios:
        del usuarios[username]
        messagebox.showinfo("Sucesso", f"Usuário {username} removido com sucesso.")
    else:
        messagebox.showerror("Erro", f"Usuário {username} não encontrado.")

# Função para sair da aplicação via interface gráfica
def sair():
    root.destroy()  # Fecha a interface Tkinter

# Função para configurar Host e Porta via interface gráfica
def configurar_host_porta():
    global host, port
    host = simpledialog.askstring("Host", "Digite o Host:", initialvalue=host)
    port = simpledialog.askstring("Porta", "Digite a Porta:", initialvalue=port)

# Interface gráfica usando Tkinter
def criar_interface_servidor():
    global chat_log, root, host, port

    root = tk.Tk()
    root.title("Servidor Flask com WebSockets")

    # Área de logs do servidor
    chat_log = tk.Text(root, state='normal', wrap=tk.WORD, width=50, height=20)
    chat_log.grid(row=0, column=0, padx=10, pady=10)

    # Menu da interface gráfica
    menu = tk.Menu(root)
    root.config(menu=menu)

    # Menu de controle do servidor
    servidor_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Servidor", menu=servidor_menu)
    servidor_menu.add_command(label="Ligar", command=iniciar_servidor)
    servidor_menu.add_command(label="Desligar", command=parar_servidor)
    servidor_menu.add_command(label="Sair", command=sair)

    # Menu para adicionar e remover usuários
    usuarios_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Usuários", menu=usuarios_menu)
    usuarios_menu.add_command(label="Adicionar usuário", command=adicionar_usuario)
    usuarios_menu.add_command(label="Remover usuário", command=remover_usuario)

    # Menu para configurar host e porta
    configuracao_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Configurações", menu=configuracao_menu)
    configuracao_menu.add_command(label="Host e Porta", command=configurar_host_porta)

    # Inicializa a interface gráfica
    root.mainloop()

if __name__ == "__main__":
    # Configurações padrão de host e porta
    host = '127.0.0.1'
    port = '5000'
    criar_interface_servidor()  # Inicia a interface Tkinter
