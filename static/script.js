const socket = io();

document.getElementById('connect-btn').addEventListener('click', () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        alert("Por favor, preencha o usuário e a senha.");
        return;
    }

    // Enviar autenticação ao servidor
    socket.emit('autenticar', { username: username, password: password });

    socket.on('autenticado', (data) => {
        if (data.status === 'success') {
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('chat-section').classList.remove('hidden');
        } else {
            alert('Autenticação falhou');
        }
    });
});

document.getElementById('send-btn').addEventListener('click', () => {
    const username = document.getElementById('username').value;
    const message = document.getElementById('message').value;
    const recipient = document.getElementById('recipient').value;

    if (!message) return;

    // Enviar mensagem ao servidor
    socket.emit('mensagem', { username: username, message: message, recipient: recipient });
    document.getElementById('message').value = '';
});

document.getElementById('disconnect-btn').addEventListener('click', () => {
    socket.disconnect();
});

socket.on('mensagem_privada', (data) => {
    const chatLog = document.getElementById('chat-log');
    const messageElement = document.createElement('div');
    messageElement.textContent = `${data.username} (privado): ${data.message}`;
    chatLog.appendChild(messageElement);
});

socket.on('message', (data) => {
    const chatLog = document.getElementById('chat-log');
    const messageElement = document.createElement('div');
    messageElement.textContent = `${data.username}: ${data.message}`;
    chatLog.appendChild(messageElement);
});
