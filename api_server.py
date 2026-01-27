# -*- coding: utf-8 -*-
"""
Servidor API y WebSocket para conexión remota
"""

import threading
import socket
from flask import Flask, request
from flask_socketio import SocketIO, emit

class ChatServer(threading.Thread):
    def __init__(self, chat_engine, ui_callback_handler=None):
        super().__init__()
        self.chat_engine = chat_engine
        self.ui_callback_handler = ui_callback_handler
        self.daemon = True
        
        self.app = Flask(__name__)
        # Cambio a 'threading' para evitar conflictos con Tkinter
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        self.host = '0.0.0.0'
        self.port = 5000
        
        # Iniciar servicio de descubrimiento UDP
        self.discovery_thread = threading.Thread(target=self.start_discovery_service)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()
        
        # Ruta de estado simple
        @self.app.route('/')
        def index():
            return "Aurora Server Running", 200

        # Registrar eventos
        self.register_events()
        
    def get_local_ip(self):
        """Obtiene la IP local para mostrarla"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start_discovery_service(self):
        """Escucha broadcast UDP para descubrimiento automático"""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Bind a 0.0.0.0 permite recibir broadcast de cualquier interfaz
        udp_socket.bind(('0.0.0.0', 5005))
        print(f"[DISCOVERY] Escuchando peticiones UDP en puerto 5005")
        
        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                message = data.decode('utf-8')
                if message == "AURORA_DISCOVER":
                    # Responder al cliente que nos buscó
                    response = "AURORA_HERE"
                    udp_socket.sendto(response.encode('utf-8'), addr)
                    print(f"[DISCOVERY] Respondido a {addr[0]}")
            except Exception as e:
                print(f"[DISCOVERY] Error: {e}")

    def register_events(self):
        """Registra los eventos de SocketIO"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"[SERVER] Cliente conectado: {request.sid}")
            # Enviar historial actual al conectar
            history = []
            for msg in self.chat_engine.conversation_history:
                history.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            emit('history_sync', {'messages': history})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"[SERVER] Cliente desconectado: {request.sid}")

        @self.socketio.on('client_message')
        def handle_client_message(data):
            """Maneja mensajes enviados desde el móvil"""
            message = data.get('message', '')
            print(f"[SERVER] Mensaje recibido del móvil: {message}")
            
            if message and self.ui_callback_handler:
                # Inyectar el mensaje en el flujo principal de la UI
                self.ui_callback_handler(message)

    def run(self):
        """Inicia el servidor"""
        print(f"=================================================")
        print(f"🚀 Servidor Aurora escuchando en: {self.get_local_ip()}:{self.port}")
        print(f"=================================================")
        # Usar socketio.run en lugar de app.run para soporte WebSocket
        self.socketio.run(self.app, host=self.host, port=self.port, log_output=False, allow_unsafe_werkzeug=True)

    def broadcast_message(self, role, content):
        """Emite un mensaje completo a todos los clientes"""
        if self.socketio:
            self.socketio.emit('new_message', {
                'role': role,
                'content': content
            })

    def broadcast_token(self, token):
        """Emite un token de streaming"""
        if self.socketio:
            self.socketio.emit('token_stream', {
                'token': token
            })

    def broadcast_error(self, message):
        """Emite un mensaje de error a todos los clientes"""
        if self.socketio:
            self.socketio.emit('error_message', {
                'message': message
            })
