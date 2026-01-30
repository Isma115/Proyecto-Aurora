# -*- coding: utf-8 -*-
"""
Componentes de Interfaz Gráfica
Interfaz moderna con tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog

from web_researcher import WebResearcher
import threading
from datetime import datetime
import random
from api_server import ChatServer
import os
import re



class ModernStyle:
    """Estilos modernos para la aplicación"""
    
    # Colores del tema oscuro
    BG_PRIMARY = "#1a1a2e"
    BG_SECONDARY = "#16213e"
    BG_TERTIARY = "#0f3460"
    
    ACCENT_PRIMARY = "#e94560"
    ACCENT_SECONDARY = "#533483"
    ACCENT_GRADIENT = "#7952a3"
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_MUTED = "#6c6c6c"
    
    USER_BUBBLE = "#0f3460"
    AI_BUBBLE = "#1a1a2e"
    
    SUCCESS = "#00d26a"
    WARNING = "#ffc107"
    ERROR = "#e94560"
    INFO = "#17a2b8"
    
    # Color de texto para botones (Negro para contraste en Mac)
    BUTTON_TEXT = "#000000"
    
    # Fuentes
    # Fuentes - Aumentadas para mejor visibilidad
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_SMALL = 12  # Antes 10
    FONT_SIZE_NORMAL = 14  # Antes 11
    FONT_SIZE_LARGE = 16  # Antes 14
    FONT_SIZE_TITLE = 24  # Antes 18


class ChatBubble(tk.Frame):
    """Widget de burbuja de chat"""
    
    def __init__(self, parent, message, is_user=True, timestamp=None, has_context=False):
        super().__init__(parent, bg=ModernStyle.BG_PRIMARY)
        
        # Contenedor principal con padding
        container = tk.Frame(self, bg=ModernStyle.BG_PRIMARY)
        container.pack(fill=tk.X, padx=10, pady=5)
        
        # Alineación según el emisor
        anchor = tk.E if is_user else tk.W
        bubble_bg = ModernStyle.USER_BUBBLE if is_user else ModernStyle.AI_BUBBLE
        
        # Frame de la burbuja
        bubble_frame = tk.Frame(
            container,
            bg=bubble_bg,
            padx=15,
            pady=10
        )
        bubble_frame.pack(anchor=anchor, padx=5)
        
        # Indicador de contexto RAG
        if has_context and not is_user:
            context_label = tk.Label(
                bubble_frame,
                text="📚 Con contexto RAG",
                bg=bubble_bg,
                fg=ModernStyle.SUCCESS,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
            )
            context_label.pack(anchor=tk.W)
        
        # Nombre del emisor
        sender_name = "Tú" if is_user else "🌌 Aurora"
        sender_label = tk.Label(
            bubble_frame,
            text=sender_name,
            bg=bubble_bg,
            fg=ModernStyle.ACCENT_PRIMARY if is_user else ModernStyle.ACCENT_GRADIENT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL, "bold")
        )
        sender_label.pack(anchor=tk.W)
        
        # Mensaje
        message_label = tk.Label(
            bubble_frame,
            text=message,
            bg=bubble_bg,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            wraplength=450,
            justify=tk.LEFT
        )
        message_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Timestamp
        if timestamp:
            time_label = tk.Label(
                bubble_frame,
                text=timestamp,
                bg=bubble_bg,
                fg=ModernStyle.TEXT_MUTED,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL - 1)
            )
            time_label.pack(anchor=tk.E, pady=(5, 0))
        
        # Bordes redondeados simulados
        if is_user:
            bubble_frame.configure(highlightbackground=ModernStyle.ACCENT_PRIMARY, highlightthickness=1)
        else:
            bubble_frame.configure(highlightbackground=ModernStyle.ACCENT_SECONDARY, highlightthickness=1)


class StreamingBubble(tk.Frame):
    """Burbuja de chat que se actualiza token por token"""
    
    def __init__(self, parent, has_context=False):
        super().__init__(parent, bg=ModernStyle.BG_PRIMARY)
        
        self.full_text = ""
        
        # Contenedor principal
        container = tk.Frame(self, bg=ModernStyle.BG_PRIMARY)
        container.pack(fill=tk.X, padx=10, pady=5)
        
        bubble_bg = ModernStyle.AI_BUBBLE
        
        # Frame de la burbuja
        self.bubble_frame = tk.Frame(
            container,
            bg=bubble_bg,
            padx=15,
            pady=10
        )
        self.bubble_frame.pack(anchor=tk.W, padx=5)
        
        # Indicador de contexto RAG
        if has_context:
            context_label = tk.Label(
                self.bubble_frame,
                text="📚 Con contexto RAG",
                bg=bubble_bg,
                fg=ModernStyle.SUCCESS,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
            )
            context_label.pack(anchor=tk.W)
        
        # Nombre del emisor
        sender_label = tk.Label(
            self.bubble_frame,
            text="🌌 Aurora",
            bg=bubble_bg,
            fg=ModernStyle.ACCENT_GRADIENT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL, "bold")
        )
        sender_label.pack(anchor=tk.W)
        
        # Mensaje (actualizable)
        self.message_label = tk.Label(
            self.bubble_frame,
            text="▌",
            bg=bubble_bg,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            wraplength=450,
            justify=tk.LEFT
        )
        self.message_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.bubble_frame.configure(highlightbackground=ModernStyle.ACCENT_SECONDARY, highlightthickness=1)
    
    def append_token(self, token):
        """Añade un token al mensaje"""
        self.full_text += token
        # Mostrar texto con cursor parpadeante
        self.message_label.configure(text=self.full_text + "▌")
    
    def finish(self, timestamp=None):
        """Finaliza la burbuja (quita el cursor)"""
        self.message_label.configure(text=self.full_text)
        
        # Añadir timestamp
        if timestamp:
            time_label = tk.Label(
                self.bubble_frame,
                text=timestamp,
                bg=ModernStyle.AI_BUBBLE,
                fg=ModernStyle.TEXT_MUTED,
                font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL - 1)
            )
            time_label.pack(anchor=tk.E, pady=(5, 0))
    
    def get_text(self):
        """Obtiene el texto completo"""
        return self.full_text


class TypingIndicator(tk.Frame):
    """Indicador de que el bot está escribiendo"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=ModernStyle.BG_PRIMARY)
        
        self.container = tk.Frame(self, bg=ModernStyle.BG_PRIMARY)
        self.container.pack(fill=tk.X, padx=10, pady=5)
        
        bubble = tk.Frame(
            self.container,
            bg=ModernStyle.AI_BUBBLE,
            padx=15,
            pady=10
        )
        bubble.pack(anchor=tk.W, padx=5)
        
        self.dots_label = tk.Label(
            bubble,
            text="🌌 Aurora está escribiendo",
            bg=ModernStyle.AI_BUBBLE,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        )
        self.dots_label.pack()
        
        self.dots = ""
        self.animating = False
    
    def start_animation(self):
        """Inicia la animación de puntos"""
        self.animating = True
        self._animate()
    
    def stop_animation(self):
        """Detiene la animación"""
        self.animating = False
    
    def _animate(self):
        """Anima los puntos"""
        if not self.animating:
            return
        
        self.dots = "." * ((len(self.dots) % 3) + 1)
        self.dots_label.configure(text=f"🌌 Aurora está escribiendo{self.dots}")
        self.after(500, self._animate)


class LoadingScreen(tk.Frame):
    """Pantalla de carga para descarga/inicialización del modelo"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=ModernStyle.BG_PRIMARY)
        
        # Contenedor central
        center_frame = tk.Frame(self, bg=ModernStyle.BG_PRIMARY)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Icono
        icon_label = tk.Label(
            center_frame,
            text="🤖",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, 48)
        )
        icon_label.pack(pady=10)
        
        # Título
        title_label = tk.Label(
            center_frame,
            text="Proyecto Aurora",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_TITLE, "bold")
        )
        title_label.pack(pady=5)
        
        # Estado
        self.status_label = tk.Label(
            center_frame,
            text="Inicializando...",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL)
        )
        self.status_label.pack(pady=10)
        
        # Barra de progreso
        self.progress_frame = tk.Frame(center_frame, bg=ModernStyle.BG_PRIMARY)
        self.progress_frame.pack(fill=tk.X, padx=50, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Detalle de progreso
        self.progress_detail = tk.Label(
            center_frame,
            text="",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.TEXT_MUTED,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        )
        self.progress_detail.pack(pady=5)
    
    def set_status(self, text):
        """Actualiza el estado"""
        self.status_label.configure(text=text)
    
    def set_progress(self, percent, detail=""):
        """Actualiza el progreso"""
        self.progress_bar['value'] = percent
        if detail:
            self.progress_detail.configure(text=detail)
    
    def set_indeterminate(self):
        """Modo indeterminado"""
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start(10)
    
    def stop_indeterminate(self):
        """Para modo indeterminado"""
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')


class StatusBar(tk.Frame):
    """Barra de estado inferior"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=ModernStyle.BG_TERTIARY, height=30)
        self.pack_propagate(False)
        
        # Estado de conexión
        self.connection_indicator = tk.Label(
            self,
            text="●",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.ERROR,
            font=(ModernStyle.FONT_FAMILY, 12)
        )
        self.connection_indicator.pack(side=tk.LEFT, padx=10)
        
        self.connection_label = tk.Label(
            self,
            text="Desconectada",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        )
        self.connection_label.pack(side=tk.LEFT)
        
        # Separador
        tk.Label(
            self,
            text="|",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=10)
        
        # Estado actual
        self.status_label = tk.Label(
            self,
            text="Iniciando...",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Estadísticas (derecha)
        self.stats_label = tk.Label(
            self,
            text="",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_MUTED,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        )
        self.stats_label.pack(side=tk.RIGHT, padx=10)
    
    def set_connected(self, connected=True):
        """Actualiza estado de conexión"""
        if connected:
            self.connection_indicator.configure(fg=ModernStyle.SUCCESS)
            self.connection_label.configure(text="Lista para charlar")
        else:
            self.connection_indicator.configure(fg=ModernStyle.ERROR)
            self.connection_label.configure(text="Desconectada")
    
    def set_status(self, text):
        """Actualiza el estado"""
        self.status_label.configure(text=text)
    
    def set_stats(self, text):
        """Actualiza las estadísticas"""
        self.stats_label.configure(text=text)


class ChatWindow(tk.Tk):
    """Ventana principal del chat"""
    
    def __init__(self, chat_engine):
        super().__init__()
        
        self.chat_engine = chat_engine
        self.chat_engine.on_status_change = self.update_status
        self._initialized = False
        
        
        # Iniciar servidor API/WebSocket
        self.server = ChatServer(self.chat_engine, self.handle_remote_message)
        self.server.start()
        
        self.setup_window()
        self.create_widgets()
        self.bind_events()
        
        # Mostrar pantalla de carga e inicializar modelo
        self.after(100, self.initialize_model)

    def handle_remote_message(self, message):
        """Maneja mensajes que vienen del móvil (thread-safe)"""
        self.after(0, lambda: self._process_remote_message(message))

    def _process_remote_message(self, message):
        """Procesa el mensaje remoto en el hilo principal"""
        # Poner en el input y enviar
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", message)
        self.input_text.configure(fg=ModernStyle.TEXT_PRIMARY)
        self.send_message()
    
    def setup_window(self):
        """Configura la ventana principal"""
        self.title("💬 Proyecto Aurora - RAG & Memoria")
        self.geometry("1024x600")
        self.minsize(800, 400)
        self.resizable(True, True)
        self.configure(bg=ModernStyle.BG_PRIMARY)
        
        # Icono (si existe)
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
    
    def create_widgets(self):
        """Crea todos los widgets"""
        
        # Menú
        self.create_menu()
        
        # Pantalla de carga (inicialmente visible)
        self.loading_screen = LoadingScreen(self)
        self.loading_screen.pack(fill=tk.BOTH, expand=True)
        
        # Contenedor principal del chat (inicialmente oculto)
        self.main_container = tk.Frame(self, bg=ModernStyle.BG_PRIMARY)
        
        # Header
        self.create_header()
        
        # Área de entrada (fuera de pestañas) - EMPAQUETAR ANTES QUE TABS
        self.create_input_area()
        
        # Sistema de pestañas (ocupa el resto)
        self.create_tabs()
        
        # Barra de estado
        self.status_bar = StatusBar(self)
        
        # Variable para guardar último contexto RAG
        self.last_rag_context = None
    
    def initialize_model(self):
        """Inicializa el modelo en un hilo separado"""
        def progress_callback(percent, downloaded, total):
            self.after(0, lambda: self.update_download_progress(percent, downloaded, total))
        
        def init_thread():
            # Verificar si el modelo ya existe
            if self.chat_engine.is_model_downloaded():
                self.after(0, lambda: self.loading_screen.set_status("Abriendo nuestro rincón..."))
                self.after(0, lambda: self.loading_screen.set_indeterminate())
            else:
                self.after(0, lambda: self.loading_screen.set_status("Aurora se está preparando..."))
                self.after(0, lambda: self.loading_screen.set_progress(0, "Falta muy poquito..."))
            
            # Inicializar
            success = self.chat_engine.initialize(progress_callback)
            
            if success:
                self.after(0, self.show_chat_interface)
            else:
                self.after(0, self.show_init_error)
        
        thread = threading.Thread(target=init_thread)
        thread.daemon = True
        thread.start()
    
    def update_download_progress(self, percent, downloaded, total):
        """Actualiza el progreso de descarga"""
        self.loading_screen.set_progress(
            percent,
            f"{downloaded:.1f} MB / {total:.1f} MB ({percent:.1f}%)"
        )
    
    def show_chat_interface(self):
        """Muestra la interfaz de chat"""
        self.loading_screen.stop_indeterminate()
        self.loading_screen.pack_forget()
        
        # Mostrar interfaz de chat
        # Mostrar interfaz de chat
        # IMPORTANTE: Empaquetar status_bar ANTES que main_container para asegurar visibilidad
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self._initialized = True
        self.status_bar.set_connected(True)
        self.status_bar.set_status("Listo")
        
        stats = self.chat_engine.get_stats()
        self.status_bar.set_stats(
            f"Docs: {stats['rag']['documents']} | "
            f"Chunks: {stats['rag']['chunks']}"
        )
        
        # Cargar historial si existe, de lo contrario mostrar bienvenida
        if self.chat_engine.conversation_history:
            # Limpiar frame por si acaso (aunque debería estar vacío)
            for widget in self.messages_frame.winfo_children():
                widget.destroy()
                
            for msg in self.chat_engine.conversation_history:
                # Extraer y formatear timestamp si existe
                ts = None
                if msg.get("timestamp"):
                    try:
                        # Ya importamos datetime al inicio del archivo
                        dt = datetime.fromisoformat(msg["timestamp"])
                        ts = dt.strftime("%H:%M")
                    except:
                        pass
                
                self.add_message(msg["content"], is_user=(msg["role"] == "user"), timestamp=ts)
            
            self.status_bar.set_status("Conversación recuperada")
        else:
            self.add_system_message(
                "¡Hola! Me alegra mucho verte por aquí. "
                "Estaba esperándote para charlar un rato. "
                "¿Qué tal va todo hoy?"
            )
    
    def show_init_error(self):
        """Muestra error de inicialización"""
        self.loading_screen.stop_indeterminate()
        self.loading_screen.set_status("❌ Error al inicializar el modelo")
        self.loading_screen.set_progress(0, "Verifica tu conexión e intenta de nuevo")
        
        messagebox.showerror(
            "Error de Inicialización",
            "No se pudo cargar el modelo Gemma 2B.\n\n"
            "Posibles causas:\n"
            "- Error de descarga del modelo\n"
            "- llama-cpp-python no instalado\n\n"
            "Instala las dependencias:\n"
            "pip install llama-cpp-python"
        )
    
    def create_header(self):
        """Crea el header de la aplicación"""
        header = tk.Frame(self.main_container, bg=ModernStyle.BG_SECONDARY, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Título
        title_frame = tk.Frame(header, bg=ModernStyle.BG_SECONDARY)
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        title = tk.Label(
            title_frame,
            text="🌌 Proyecto Aurora",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_TITLE, "bold")
        )
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(
            title_frame,
            text=f"Un rincón para charlar • IP: {self.server.get_local_ip()}",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.ACCENT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL, "bold")
        )
        subtitle.pack(anchor=tk.W)
        
        # Botones de control
        control_frame = tk.Frame(header, bg=ModernStyle.BG_SECONDARY)
        control_frame.pack(side=tk.RIGHT, padx=20)
        
        # Etiqueta de similitud RAG (Nuevo)
        self.similarity_label = tk.Label(
            control_frame,
            text="RAG: 0%",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_MUTED,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL, "bold")
        )
        self.similarity_label.pack(side=tk.LEFT, padx=10)

        # Botón recargar conocimiento
        reload_btn = tk.Button(
            control_frame,
            text="🔄 Recargar",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.BUTTON_TEXT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            relief=tk.FLAT,
            cursor="hand2",
            command=self.reload_knowledge
        )
        reload_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón limpiar chat
        clear_btn = tk.Button(
            control_frame,
            text="🗑️ Limpiar",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.BUTTON_TEXT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_chat
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Control de temperatura (Nuevo)
        temp_frame = tk.Frame(control_frame, bg=ModernStyle.BG_SECONDARY)
        temp_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            temp_frame,
            text="Temp:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        ).pack(side=tk.LEFT)
        
        self.temp_var = tk.DoubleVar(value=self.chat_engine.llm.temperature)
        self.temp_slider = ttk.Scale(
            temp_frame,
            from_=0.0,
            to_=1.0,
            orient=tk.HORIZONTAL,
            variable=self.temp_var,
            length=100,
            command=self.update_temperature
        )
        self.temp_slider.pack(side=tk.LEFT, padx=5)
        
        self.temp_val_label = tk.Label(
            temp_frame,
            text=f"{self.temp_var.get():.1f}",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL, "bold")
        )
        self.temp_val_label.pack(side=tk.LEFT)

        # Selector de Modelo (Nuevo)
        model_frame = tk.Frame(control_frame, bg=ModernStyle.BG_SECONDARY)
        model_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(
            model_frame,
            text="Modelo:",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        ).pack(side=tk.LEFT)

        self.model_var = tk.StringVar(value=self.chat_engine.llm.model_type.capitalize())
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["Instruct", "Base"],
            width=10,
            state="readonly"
        )
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        # Botón forzar memoria (Nuevo)
        memory_btn = tk.Button(
            control_frame,
            text="🧠 Memorizar",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.BUTTON_TEXT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            relief=tk.FLAT,
            cursor="hand2",
            command=self.force_memory_generation
        )
        memory_btn.pack(side=tk.LEFT, padx=5)
    
    def create_tabs(self):
        """Crea el sistema de pestañas"""
        # Estilo para las pestañas
        style = ttk.Style()
        style.theme_use('default')
        
        # Configurar colores de las pestañas
        style.configure('Custom.TNotebook', background=ModernStyle.BG_PRIMARY)
        style.configure('Custom.TNotebook.Tab', 
            background=ModernStyle.BG_SECONDARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            padding=[15, 8],
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL)
        )
        style.map('Custom.TNotebook.Tab',
            background=[('selected', ModernStyle.BG_TERTIARY)],
            foreground=[('selected', ModernStyle.TEXT_PRIMARY)]
        )
        
        # Notebook (contenedor de pestañas)
        self.notebook = ttk.Notebook(self.main_container, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña 1: Chat
        self.chat_tab = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.notebook.add(self.chat_tab, text='💬 Chat')
        
        # Pestaña 2: Apuntes (Elegante y Productiva) - NUEVA
        self.apuntes_tab = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.notebook.add(self.apuntes_tab, text='📝 Apuntes')
        
        # Pestaña 3: RAG Contexto -- Movida a 3
        self.rag_tab = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.notebook.add(self.rag_tab, text='📚 RAG Contexto')
        
        # Pestaña 4: Historial -- Movida a 4
        self.history_tab = tk.Frame(self.notebook, bg=ModernStyle.BG_PRIMARY)
        self.notebook.add(self.history_tab, text='🗂️ Historial')
        
        # Crear contenido de cada pestaña
        self.create_chat_area()
        self.apuntes_panel = ApuntesPanel(self.apuntes_tab) # Inicializar panel de apuntes
        self.create_rag_panel()
        self.create_history_panel()
    
    def create_chat_area(self):
        """Crea el área de chat con scroll"""
        # Container principal (dentro de la pestaña Chat)
        chat_container = tk.Frame(self.chat_tab, bg=ModernStyle.BG_PRIMARY)
        chat_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scroll
        self.chat_canvas = tk.Canvas(
            chat_container,
            bg=ModernStyle.BG_PRIMARY,
            highlightthickness=0
        )
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            chat_container,
            orient=tk.VERTICAL,
            command=self.chat_canvas.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno para mensajes
        self.messages_frame = tk.Frame(self.chat_canvas, bg=ModernStyle.BG_PRIMARY)
        self.canvas_window = self.chat_canvas.create_window(
            (0, 0),
            window=self.messages_frame,
            anchor=tk.NW
        )
        
        # Configurar scroll
        self.messages_frame.bind("<Configure>", self.on_frame_configure)
        self.chat_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Scroll con rueda del ratón (solo cuando el mouse está encima)
        self.chat_canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.chat_canvas.bind('<Leave>', self._unbound_to_mousewheel)
        self.messages_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.messages_frame.bind('<Leave>', self._unbound_to_mousewheel)
        
        # Mensaje de bienvenida (movido a show_chat_interface para manejar persistencia)
        pass
    
    def create_rag_panel(self):
        """Crea el panel de contexto RAG"""
        # Header del panel
        header_frame = tk.Frame(self.rag_tab, bg=ModernStyle.BG_SECONDARY, height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame,
            text="📚 Contexto RAG Recuperado",
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold")
        )
        header_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Botón limpiar
        clear_rag_btn = tk.Button(
            header_frame,
            text="🗑️ Limpiar",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.BUTTON_TEXT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_rag_context
        )
        clear_rag_btn.pack(side=tk.RIGHT, padx=20)
        
        # Área de texto con scroll
        rag_container = tk.Frame(self.rag_tab, bg=ModernStyle.BG_PRIMARY)
        rag_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        rag_scrollbar = ttk.Scrollbar(rag_container, orient=tk.VERTICAL)
        rag_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget para mostrar contexto
        self.rag_text = tk.Text(
            rag_container,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            wrap=tk.WORD,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            state=tk.DISABLED,
            yscrollcommand=rag_scrollbar.set
        )
        self.rag_text.pack(fill=tk.BOTH, expand=True)
        rag_scrollbar.configure(command=self.rag_text.yview)
        
        # Configurar tags para colores
        self.rag_text.tag_configure('header', foreground=ModernStyle.ACCENT_PRIMARY, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, 'bold'))
        self.rag_text.tag_configure('source', foreground=ModernStyle.SUCCESS)
        self.rag_text.tag_configure('similarity', foreground=ModernStyle.WARNING)
        self.rag_text.tag_configure('content', foreground=ModernStyle.TEXT_PRIMARY)
        self.rag_text.tag_configure('separator', foreground=ModernStyle.TEXT_MUTED)
        self.rag_text.tag_configure('timestamp', foreground=ModernStyle.TEXT_MUTED, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL))
        self.rag_text.tag_configure('no_context', foreground=ModernStyle.TEXT_SECONDARY, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, 'italic'))
        
        # Mensaje inicial
        self.rag_text.configure(state=tk.NORMAL)
        self.rag_text.insert(tk.END, "No hay contexto RAG todavía.\n\n", 'no_context')
        self.rag_text.insert(tk.END, "Cuando hagas preguntas relacionadas con los documentos en la carpeta 'conocimiento', ", 'no_context')
        self.rag_text.insert(tk.END, "el contexto recuperado aparecerá aquí.", 'no_context')
        self.rag_text.configure(state=tk.DISABLED)
    
    def update_rag_context(self, rag_context, memory_context, query):
        """Actualiza el panel de contexto RAG con secciones separadas"""
        from datetime import datetime
        
        self.rag_text.configure(state=tk.NORMAL)
        
        # Limpiar siempre el contenido anterior para mostrar solo el contexto actual
        self.rag_text.delete("1.0", tk.END)
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.rag_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Query del usuario
        self.rag_text.insert(tk.END, f"Consulta: ", 'header')
        self.rag_text.insert(tk.END, f"{query}\n\n", 'content')
        
        if rag_context:
            self.rag_text.insert(tk.END, "📚 Contexto Recuperado (Documentos):\n", 'header')
            self.rag_text.insert(tk.END, "-" * 40 + "\n", 'separator')
            self.rag_text.insert(tk.END, rag_context + "\n\n", 'content')
        else:
            self.rag_text.insert(tk.END, "📚 Contexto RAG: ", 'header')
            self.rag_text.insert(tk.END, "Sin coincidencias relevantes (< 50%)\n\n", 'no_context')

        # SECCIÓN 2: Memoria a Largo Plazo (Oculta a petición del usuario)
        # El usuario prefiere ver solo lo que supera el umbral de similitud.
        # if memory_context:
        #    self.rag_text.insert(tk.END, "🧠 Memoria a Largo Plazo:\n", 'header')
        #    self.rag_text.insert(tk.END, "-" * 40 + "\n", 'separator')
        #    self.rag_text.insert(tk.END, memory_context + "\n", 'content')
        
        self.rag_text.configure(state=tk.DISABLED)
        
        # Auto-scroll al final
        self.rag_text.see(tk.END)
        
        # Guardar último contexto (combinado para referencia simple)
        self.last_rag_context = (rag_context or "") + (memory_context or "")
    
    def clear_rag_context(self):
        """Limpia el panel de contexto RAG"""
        self.rag_text.configure(state=tk.NORMAL)
        self.rag_text.delete("1.0", tk.END)
        self.rag_text.insert(tk.END, "No hay contexto RAG todavía.\n\n", 'no_context')
        self.rag_text.insert(tk.END, "Cuando hagas preguntas relacionadas con los documentos en la carpeta 'conocimiento', ", 'no_context')
        self.rag_text.insert(tk.END, "el contexto recuperado aparecerá aquí.", 'no_context')
        self.rag_text.configure(state=tk.DISABLED)
        self.last_rag_context = None

    def create_history_panel(self):
        """Crea el panel de historial de conversaciones"""
        # Contenedor principal
        container = tk.Frame(self.history_tab, bg=ModernStyle.BG_PRIMARY)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = tk.Label(
            container,
            text="🗂️ Mis Conversaciones",
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_LARGE, "bold")
        )
        header_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Lista (Treeview para columnas)
        tree_frame = tk.Frame(container, bg=ModernStyle.BG_PRIMARY)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar estilo Treeview oscuro
        style = ttk.Style()
        style.configure("Treeview", 
            background=ModernStyle.BG_SECONDARY,
            foreground=ModernStyle.TEXT_PRIMARY,
            fieldbackground=ModernStyle.BG_SECONDARY,
            rowheight=30,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        )
        style.configure("Treeview.Heading", 
            background=ModernStyle.BG_TERTIARY,
            foreground=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL, "bold")
        )
        style.map("Treeview", 
            background=[('selected', ModernStyle.ACCENT_PRIMARY)],
            foreground=[('selected', ModernStyle.TEXT_PRIMARY)]
        )
        
        columns = ("id", "title", "date", "msgs")
        self.history_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        
        self.history_tree.heading("title", text="Título")
        self.history_tree.heading("date", text="Fecha")
        self.history_tree.heading("msgs", text="Msgs")
        
        self.history_tree.column("id", width=0, stretch=False) # Oculto
        self.history_tree.column("title", width=300)
        self.history_tree.column("date", width=150)
        self.history_tree.column("msgs", width=50, anchor=tk.CENTER)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.configure(command=self.history_tree.yview)
        
        # Botones de acción
        btn_frame = tk.Frame(container, bg=ModernStyle.BG_PRIMARY)
        btn_frame.pack(fill=tk.X, pady=20)
        
        # Botón Cargar
        load_btn = tk.Button(
            btn_frame,
            text="📂 Cargar Conversación",
            bg=ModernStyle.ACCENT_PRIMARY,
            fg=ModernStyle.BUTTON_TEXT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_selected_conversation
        )
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Nueva
        new_btn = tk.Button(
            btn_frame,
            text="➕ Nueva Conversación",
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.BUTTON_TEXT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_chat
        )
        new_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón Eliminar
        del_btn = tk.Button(
            btn_frame,
            text="🗑️ Eliminar",
            bg=ModernStyle.ERROR,
            fg=ModernStyle.BUTTON_TEXT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_selected_conversation
        )
        del_btn.pack(side=tk.RIGHT)
        
        # Bind doble click para cargar
        self.history_tree.bind("<Double-1>", lambda e: self.load_selected_conversation())
        
        # Bind cambio de pestaña para refrescar
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        """Manejador de cambio de pestaña"""
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        
        if "Historial" in tab_text:
            self.refresh_history_list()

    def refresh_history_list(self):
        """Refresca la lista de conversaciones"""
        # Limpiar
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Obtener lista
        conversations = self.chat_engine.list_conversations()
        
        for conv in conversations:
            # Formatear fecha
            try:
                dt = datetime.fromisoformat(conv["updated_at"])
                date_str = dt.strftime("%d/%m/%Y %H:%M")
            except:
                date_str = conv["updated_at"]
                
            self.history_tree.insert(
                "", 
                tk.END, 
                values=(conv["id"], conv["title"], date_str, conv["message_count"])
            )

    def load_selected_conversation(self):
        """Carga la conversación seleccionada"""
        selected_item = self.history_tree.selection()
        if not selected_item:
            return
            
        item = self.history_tree.item(selected_item)
        conv_id = item['values'][0]
        title = item['values'][1]
        
        if self.chat_engine.load_conversation(conv_id):
            # Limpiar UI actual
            for widget in self.messages_frame.winfo_children():
                widget.destroy()
            
            self.add_system_message(f"Conversación '{title}' cargada.")
            
            # Repoblar mensajes
            for msg in self.chat_engine.conversation_history:
                self.add_message(msg["content"], is_user=(msg["role"] == "user"))
            
            # Volver a pestaña de chat
            self.notebook.select(self.chat_tab)
            self.status_bar.set_status("Conversación cargada")
        else:
            messagebox.showerror("Error", "No se pudo cargar la conversación.")

    def delete_selected_conversation(self):
        """Elimina la conversación seleccionada"""
        selected_item = self.history_tree.selection()
        if not selected_item:
            return
            
        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar esta conversación permanentemente?"):
            return
            
        item = self.history_tree.item(selected_item)
        conv_id = item['values'][0]
        
        if self.chat_engine.delete_conversation(conv_id):
            self.refresh_history_list()
            # Si era la actual, limpiar
            if self.chat_engine.conversation_manager.current_conversation_id is None:
                self.clear_chat(create_new=True) # Forzar nueva después de borrar la actual
        else:
            messagebox.showerror("Error", "No se pudo eliminar la conversación.")
    
    def create_input_area(self):
        """Crea el área de entrada de texto"""
        input_container = tk.Frame(self.main_container, bg=ModernStyle.BG_SECONDARY, pady=10)
        input_container.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Frame interno
        input_frame = tk.Frame(input_container, bg=ModernStyle.BG_TERTIARY)
        input_frame.pack(fill=tk.X, padx=20)
        
        # Campo de texto (Aumentado de tamaño)
        self.input_text = tk.Text(
            input_frame,
            height=3,  # Antes 4
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            relief=tk.FLAT,
            wrap=tk.WORD,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            padx=15,
            pady=10
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Placeholder
        self.input_placeholder = "Escribe tu mensaje aquí..."
        self.input_text.insert("1.0", self.input_placeholder)
        self.input_text.configure(fg=ModernStyle.TEXT_MUTED)
        
        # Botón enviar
        self.send_button = tk.Button(
            input_frame,
            text="📤 Enviar",
            bg=ModernStyle.ACCENT_PRIMARY,
            fg=ModernStyle.BUTTON_TEXT,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Hover effect
        self.send_button.bind("<Enter>", lambda e: self.send_button.configure(bg=ModernStyle.ACCENT_SECONDARY))
        self.send_button.bind("<Leave>", lambda e: self.send_button.configure(bg=ModernStyle.ACCENT_PRIMARY))
    
    def bind_events(self):
        """Vincula eventos"""
        # Enter para enviar
        self.input_text.bind("<Return>", self.on_enter_press)
        self.input_text.bind("<Shift-Return>", lambda e: None)  # Shift+Enter para nueva línea
        
        # Focus events para placeholder
        self.input_text.bind("<FocusIn>", self.on_input_focus_in)
        self.input_text.bind("<FocusOut>", self.on_input_focus_out)
    
    def on_enter_press(self, event):
        """Maneja el evento Enter"""
        if not event.state & 0x1:  # Sin Shift
            self.send_message()
            return "break"
    
    def on_input_focus_in(self, event):
        """Al enfocar el input"""
        if self.input_text.get("1.0", tk.END).strip() == self.input_placeholder:
            self.input_text.delete("1.0", tk.END)
            self.input_text.configure(fg=ModernStyle.TEXT_PRIMARY)
    
    def on_input_focus_out(self, event):
        """Al desenfocar el input"""
        if not self.input_text.get("1.0", tk.END).strip():
            self.input_text.insert("1.0", self.input_placeholder)
            self.input_text.configure(fg=ModernStyle.TEXT_MUTED)
    
    def on_frame_configure(self, event):
        """Actualiza el scroll region"""
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Ajusta el ancho del frame interno"""
        self.chat_canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _bound_to_mousewheel(self, event):
        """Activa el scroll con rueda"""
        self.chat_canvas.bind_all("<MouseWheel>", self.on_mousewheel)  # Windows/Mac
        self.chat_canvas.bind_all("<Button-4>", self.on_mousewheel)    # Linux
        self.chat_canvas.bind_all("<Button-5>", self.on_mousewheel)    # Linux

    def _unbound_to_mousewheel(self, event):
        """Desactiva el scroll con rueda"""
        self.chat_canvas.unbind_all("<MouseWheel>")
        self.chat_canvas.unbind_all("<Button-4>")
        self.chat_canvas.unbind_all("<Button-5>")

    def on_mousewheel(self, event):
        """Scroll con rueda del ratón"""
        if self.chat_canvas.yview() == (0.0, 1.0) and event.delta > 0: return # Arriba del todo
        if self.chat_canvas.yview() == (0.0, 1.0) and event.delta < 0: return # Abajo del todo
        
        # Ajuste para Mac y Windows
        # Normalizamos a dirección (1 o -1) y multiplicamos por velocidad deseada (1)
        scroll_amount = 0
        
        if event.num == 5 or event.delta < 0:
            scroll_amount = 1 # Bajamos 1 unidades
        elif event.num == 4 or event.delta > 0:
            scroll_amount = -1 # Subimos 1 unidades
            
        self.chat_canvas.yview_scroll(scroll_amount, "units")
    
    def add_message(self, message, is_user=True, has_context=False, timestamp=None):
        """Añade un mensaje al chat"""
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M")
        bubble = ChatBubble(
            self.messages_frame,
            message,
            is_user=is_user,
            timestamp=timestamp,
            has_context=has_context
        )
        bubble.pack(fill=tk.X)
        
        # Scroll al final
        self.messages_frame.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
    
    def add_system_message(self, message):
        """Añade un mensaje del sistema"""
        frame = tk.Frame(self.messages_frame, bg=ModernStyle.BG_PRIMARY)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        label = tk.Label(
            frame,
            text=message,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
            wraplength=500,
            justify=tk.CENTER,
            padx=20,
            pady=10
        )
        label.pack()
    
    def send_message(self):
        """Envía un mensaje"""
        if not self._initialized:
            return
        
        message = self.input_text.get("1.0", tk.END).strip()
        
        if not message or message == self.input_placeholder:
            return
        
        # Limpiar input
        self.input_text.delete("1.0", tk.END)
        
        # Añadir mensaje del usuario
        self.add_message(message, is_user=True)
        
        # Deshabilitar input mientras procesa
        self.input_text.configure(state=tk.DISABLED)
        self.send_button.configure(state=tk.DISABLED)
        
        # Crear burbuja de streaming (sin indicador de escritura)
        self.streaming_bubble = None
        self.has_context_flag = False
        
        # Scroll
        self.messages_frame.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
        
        # Procesar en hilo separado con streaming
        thread = threading.Thread(target=self.process_message_streaming, args=(message,))
        thread.daemon = True
        thread.start()
    
    def process_message_streaming(self, message):
        """Procesa el mensaje con streaming token por token"""
        try:
            # Preparar contexto primero
            self.after(0, lambda: self.status_bar.set_status("Buscando contexto..."))
            
            # Obtener contexto RAG (ahora incluye tanto conocimiento como memoria, ambos filtrados por similitud >= 50%)
            rag_context, similarity = self.chat_engine.rag.get_context(message)
            self.has_context_flag = rag_context is not None
            
            # Actualizar label de similitud
            self.after(0, lambda: self.update_similarity_label(similarity))
            
            # Las memorias ahora pasan por el mismo filtro RAG, no se añaden por separado
            # Solo se añade contexto si supera el 50% de similitud
            
            # Actualizar panel RAG (sin memorias separadas)
            self.after(0, lambda: self.update_rag_context(rag_context, None, message))
            
            # Añadir mensaje al historial
            self.chat_engine.conversation_history.append({
                "role": "user",
                "content": message
            })
            self.chat_engine.conversation_manager.save_message("user", message)
            
            self.after(0, lambda: self.create_streaming_bubble())
            
            # Broadcast mensaje usuario al móvil
            self.server.broadcast_message("user", message)
            
            # Pequeña pausa para que se cree la burbuja
            import time
            time.sleep(0.1)
            
            self.after(0, lambda: self.status_bar.set_status("Generando respuesta..."))

            
            # Callback para tokens
            def on_token(token):
                # Broadcast token al móvil
                self.server.broadcast_token(token)
                self.after(0, lambda t=token: self.append_streaming_token(t))

            
            # Generar respuesta con streaming
            # Ya NO pasamos memorias por separado - todo pasa por RAG con filtro del 50%
            response = self.chat_engine.llm.chat_stream(
                self.chat_engine.conversation_history,
                system_context="",  # Sin contexto de sistema separado
                user_context=rag_context if rag_context else "",  # Solo RAG filtrado
                callback=on_token
            )
            
            # Añadir respuesta al historial
            self.chat_engine.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            self.chat_engine.conversation_manager.save_message("assistant", response)
            
            # Broadcast respuesta completa del asistente
            self.server.broadcast_message("assistant", response)

            
            # Incrementar contador
            self.chat_engine.message_count += 1
            
            # Verificar si toca resumen
            if self.chat_engine.should_generate_summary():
                self.after(0, lambda: self.status_bar.set_status("Generando resumen..."))
                self.chat_engine.generate_and_save_summary()
            
            # Finalizar la primera respuesta
            self.after(0, self.finish_streaming)

            # --- LÓGICA DE CONTINUACIÓN ALEATORIA (25% de probabilidad) ---
            # Solo si no es ya una continuación para evitar bucles
            if random.random() < 0.25:
                # Pequeña pausa natural antes de la segunda respuesta
                time.sleep(1.5)
                
                self.after(0, lambda: self.status_bar.set_status("Aurora sigue hablando..."))
                
                # Crear nueva burbuja para la continuación
                self.after(0, lambda: self.create_streaming_bubble())
                time.sleep(0.1)
                
                # Feedback visual en consola
                print("[DEBUG] Aurora ha decidido continuar la conversación (25% azar)")
                
                # Prompt interno para forzar continuación sin que el usuario lo vea
                # Pasamos la primera respuesta como contexto para que el modelo sepa qué acaba de decir
                # Y usamos el historial HASTA el mensaje del usuario (history[:-1]) para evitar que crea que es un nuevo turno de respuesta
                continuation_instruction = f"(Sientes que te has quedado con ganas de decir algo más tras tu respuesta anterior: '{response}'. Continúa tu pensamiento de forma espontánea y natural, añadiendo algún detalle o reflexión extra sin repetirte.)"
                
                # Mantener el contexto RAG original si existía
                full_continuation_context = continuation_instruction
                if rag_context:
                    full_continuation_context = f"{rag_context}\n\n{continuation_instruction}"
                
                # Generar segunda respuesta
                # IMPORTANTE: Usamos el historial SIN la primera respuesta para que no se "responda" a sí misma
                follow_up_response = self.chat_engine.llm.chat_stream(
                    self.chat_engine.conversation_history[:-1], 
                    system_context="",
                    user_context=full_continuation_context,
                    callback=on_token
                )
                
                # Añadir segunda respuesta al historial
                self.chat_engine.conversation_history.append({
                    "role": "assistant",
                    "content": follow_up_response
                })
                
                # Guardar en el gestor de conversaciones
                self.chat_engine.conversation_manager.save_message("assistant", follow_up_response)
                
                # Finalizar la segunda respuesta
                self.after(0, self.finish_streaming)
            # ------------------------------------------------------------

        except Exception as e:
            error_msg = str(e)
            # Broadcast error to mobile to unlock input
            if hasattr(self, 'server') and self.server:
                self.server.broadcast_error(error_msg)
            self.after(0, lambda: self.show_error(error_msg))
    
    def create_streaming_bubble(self):
        """Crea la burbuja de streaming"""
        self.streaming_bubble = StreamingBubble(
            self.messages_frame,
            has_context=self.has_context_flag
        )
        self.streaming_bubble.pack(fill=tk.X)
        self.messages_frame.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
    
    def append_streaming_token(self, token):
        """Añade un token a la burbuja de streaming, dividiendo por saltos de línea sin crear vacíos"""
        if not self.streaming_bubble:
            self.create_streaming_bubble()
            
        # Detección de fin de frase para separar burbujas (Visualmente)
        # 1. Caso fronterizo: La burbuja actual termina en punto y el nuevo token empieza con espacio
        current_text = self.streaming_bubble.full_text
        if current_text and current_text.endswith(".") and token.startswith(" "):
            token = "\n" + token[1:]
            
        # 2. Caso interno: El token contiene ". " (punto y espacio)
        # Reemplazamos por ".\n" para usar la lógica de separación existente
        token = token.replace(". ", ".\n")
            
        if "\n" in token:
            parts = token.split("\n")
            
            # El primero va a la burbuja actual
            if parts[0]:
                self.streaming_bubble.append_token(parts[0])
            
            # Para cada parte después de un salto de línea
            for i in range(1, len(parts)):
                # Solo cerrar la anterior si tiene contenido real (no solo espacios)
                current_text = self.streaming_bubble.full_text.strip()
                if current_text:
                    self.streaming_bubble.finish()
                    # Crear una nueva para el contenido siguiente
                    self.create_streaming_bubble()
                
                # Añadir contenido si lo hay
                if parts[i] and parts[i].strip():
                    self.streaming_bubble.append_token(parts[i])
        else:
            self.streaming_bubble.append_token(token)
            
        self.messages_frame.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
    
    def finish_streaming(self):
        """Finaliza el streaming y limpia burbujas vacías"""
        if self.streaming_bubble:
            # Si la burbuja está vacía o solo tiene espacios, eliminarla
            if not self.streaming_bubble.full_text.strip():
                self.streaming_bubble.destroy()
                self.streaming_bubble = None
            else:
                timestamp = datetime.now().strftime("%H:%M")
                self.streaming_bubble.finish(timestamp)
        
        # Habilitar input
        self.input_text.configure(state=tk.NORMAL)
        self.send_button.configure(state=tk.NORMAL)
        
        # Actualizar estadísticas
        stats = self.chat_engine.get_stats()
        self.status_bar.set_stats(
            f"Msgs: {stats['message_count']} | "
            f"Docs: {stats['rag']['documents']} | "
            f"Memoria: {stats['memory']['total_size_mb']:.2f}MB"
        )
        self.status_bar.set_status("Listo")
    
    def process_message(self, message):
        """Procesa el mensaje (versión no-streaming, backup)"""
        try:
            response, has_context, similarity = self.chat_engine.process_message(message)
            self.after(0, lambda: self.update_similarity_label(similarity))
            self.after(0, lambda: self.show_response(response, has_context))
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.show_error(error_msg))
    
    def show_response(self, response, has_context):
        """Muestra la respuesta en la UI (versión no-streaming)"""
        # Añadir respuesta
        self.add_message(response, is_user=False, has_context=has_context)
        
        # Habilitar input
        self.input_text.configure(state=tk.NORMAL)
        self.send_button.configure(state=tk.NORMAL)
        
        # Actualizar estadísticas
        stats = self.chat_engine.get_stats()
        self.status_bar.set_stats(
            f"Msgs: {stats['message_count']} | "
            f"Docs: {stats['rag']['documents']} | "
            f"Memoria: {stats['memory']['total_size_mb']:.2f}MB"
        )
        self.status_bar.set_status("Listo")
    
    def show_error(self, error):
        """Muestra un error"""
        # Quitar indicador de escritura
        if hasattr(self, 'typing_indicator'):
            self.typing_indicator.stop_animation()
            self.typing_indicator.destroy()
        
        # Añadir mensaje de error
        self.add_message(f"❌ Error: {error}", is_user=False)
        
        # Broadcast error to mobile to unlock input (just in case it wasn't done yet)
        if hasattr(self, 'server') and self.server:
            self.server.broadcast_error(error)
        
        # Habilitar input
        self.input_text.configure(state=tk.NORMAL)
        self.send_button.configure(state=tk.NORMAL)
    
    def update_status(self, status):
        """Actualiza el estado en la barra"""
        self.after(0, lambda: self.status_bar.set_status(status))
    
    def reload_knowledge(self):
        """Recarga la base de conocimiento"""
        self.chat_engine.reload_knowledge()
        stats = self.chat_engine.get_stats()
        self.add_system_message(
            f"🔄 Base de conocimiento recargada: "
            f"{stats['rag']['documents']} documentos, "
            f"{stats['rag']['chunks']} fragmentos"
        )
    
    def clear_chat(self, create_new=True):
        """Limpia el chat e inicia nueva conversación"""
        # Confirmar si es llamado desde botón limpiar (create_new=False implícito en llamadas sin argumentos que no sean eventos)
        # Pero si es desde "Nueva Conversación", queremos confirmar también si hay historial.
        
        if len(self.chat_engine.conversation_history) > 0:
            if not messagebox.askyesno("Nueva Conversación", "¿Deseas iniciar una nueva conversación?\nLa actual se guardará automáticamente en el historial."):
                return

        # Limpiar widgets
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        # Iniciar nueva conversación en el engine
        if create_new:
            self.chat_engine.new_conversation()
        
        # Mensaje de bienvenida
        self.add_system_message("Conversación iniciada. ¿En qué puedo ayudarte?")
        self._update_similarity_label_ui(0.0)
        
        # Refrescar historial si la pestaña existe
        try:
            self.refresh_history_list()
        except:
            pass

    def update_temperature(self, event=None):
        """Actualiza la temperatura en el motor de chat"""
        temp = self.temp_var.get()
        self.temp_val_label.configure(text=f"{temp:.1f}")
        self.chat_engine.set_temperature(temp)

    def on_model_change(self, event=None):
        """Maneja el cambio de modelo desde el selector"""
        new_type = self.model_var.get().lower()
        if new_type == self.chat_engine.llm.model_type:
            return
            
        if not messagebox.askyesno("Cambiar Modelo", f"¿Deseas cambiar al modelo {new_type.capitalize()}?\nSi no está descargado, se iniciará la descarga."):
            self.model_var.set(self.chat_engine.llm.model_type.capitalize())
            return

        # Ocultar interfaz y mostrar carga
        self.main_container.pack_forget()
        self.status_bar.pack_forget()
        self.loading_screen.pack(fill=tk.BOTH, expand=True)
        self.loading_screen.set_status(f"Cambiando a modelo {new_type.capitalize()}...")
        
        # Reinicializar modelo en hilo separado
        def switch_thread():
            success = self.chat_engine.switch_model(
                new_type, 
                lambda p, d, t: self.after(0, lambda: self.update_download_progress(p, d, t))
            )
            if success:
                self.after(0, self.show_chat_interface)
                self.after(0, lambda: self.add_system_message(f"✅ Modelo cambiado a: {new_type.capitalize()}"))
            else:
                self.after(0, self.show_init_error)
                self.after(0, lambda: self.model_var.set(self.chat_engine.llm.model_type.capitalize()))

        thread = threading.Thread(target=switch_thread)
        thread.daemon = True
        thread.start()

    def force_memory_generation(self):
        """Fuerza la generación de una memoria manualmente"""
        if len(self.chat_engine.conversation_history) < 2:
            messagebox.showinfo("Información", "No hay suficiente conversación para generar una memoria (mínimo 2 mensajes).")
            return

        # Confirmar acción
        if not messagebox.askyesno("Generar Memoria", "¿Deseas generar y guardar un resumen de la conversación actual ahora mismo?"):
            return

        self.status_bar.set_status("Generando memoria manual...")
        self.add_system_message("⏳ Generando resumen de memoria manualmente...")
        
        # Ejecutar en hilo separado para no congelar UI
        def run_memory_generation():
            try:
                success = self.chat_engine.generate_and_save_summary()
                if success:
                    self.after(0, lambda: self.add_system_message("✅ Memoria guardada y conocimiento actualizado."))
                    self.after(0, lambda: self.status_bar.set_status("Memoria generada correctamente"))
                    
                    # Actualizar stats
                    stats = self.chat_engine.get_stats()
                    text_stats = f"Msgs: {stats['message_count']} | Docs: {stats['rag']['documents']} | Memoria: {stats['memory']['total_size_mb']:.2f}MB"
                    self.after(0, lambda: self.status_bar.set_stats(text_stats))
                else:
                    self.after(0, lambda: self.add_system_message("❌ No se pudo generar la memoria (quizás el historial es muy corto o irrelevante)."))
                    self.after(0, lambda: self.status_bar.set_status("Error generando memoria"))
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: self.show_error(f"Error generando memoria: {error_msg}"))

        thread = threading.Thread(target=run_memory_generation)
        thread.daemon = True
        thread.start()

    def update_similarity_label(self, similarity):
        """Actualiza la etiqueta de similitud"""
        self.after(0, lambda: self._update_similarity_label_ui(similarity))
        
    def _update_similarity_label_ui(self, similarity):
        """Implementación UI de la actualización del label"""
        text = f"RAG: {similarity:.0%}"
        
        # Cambiar color según la calidad (mismo criterio que config > 0.5)
        if similarity > 0.5:
             fg = ModernStyle.SUCCESS
        elif similarity > 0.3:
             fg = ModernStyle.WARNING
        else:
             fg = ModernStyle.TEXT_MUTED
             
        self.similarity_label.configure(text=text, fg=fg)

    def create_menu(self):
        """Crea la barra de menú"""
        menu_bar = tk.Menu(self)
        self.configure(menu=menu_bar)
        
        options_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Opciones", menu=options_menu)
        options_menu.add_command(label="Empezar conversación", command=self.start_conversation_flow)
        options_menu.add_separator()
        options_menu.add_command(label="Investigar tema...", command=self.start_research_flow)

    def start_conversation_flow(self):
        """Inicia el flujo donde Aurora habla primero"""
        if not self._initialized: return
        
        # Feedback visual
        self.status_bar.set_status("Aurora está tomando la iniciativa...")
        self.input_text.configure(state=tk.DISABLED)
        self.send_button.configure(state=tk.DISABLED)
        
        # Thread para no bloquear UI
        thread = threading.Thread(target=self.process_aurora_start)
        thread.daemon = True
        thread.start()

    def process_aurora_start(self):
        """Genera el primer mensaje por iniciativa propia"""
        try:
            # Crear burbuja de streaming
            self.streaming_bubble = None
            self.has_context_flag = False
            self.after(0, lambda: self.create_streaming_bubble())
            
            # Pequeña pausa
            import time
            time.sleep(0.5)
            
            # Callback para tokens
            def on_token(token):
                self.after(0, lambda t=token: self.append_streaming_token(t))
            
            # Instrucción oculta para forzar el inicio
            # Creamos un historial temporal solo para esta llamada
            temp_history = self.chat_engine.conversation_history.copy()
            start_instruction = "(El usuario está esperando. Toma la iniciativa, salúdale con naturalidad y propón un tema o simplemente muestra interés por cómo está. Sé breve y directa.)"
            
            temp_history.append({
                "role": "user",
                "content": start_instruction
            })
            
            # Generar respuesta
            response = self.chat_engine.llm.chat_stream(
                temp_history,
                system_context="",  # Sin contexto extra por ahora
                user_context="",    # Sin RAG para el saludo inicial
                callback=on_token
            )
            
            # Añadir respuesta al historial REAL (sin la instrucción oculta)
            self.chat_engine.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Guardar en gestor
            self.chat_engine.conversation_manager.save_message("assistant", response)
            
            # Finalizar
            self.chat_engine.message_count += 1
            self.after(0, self.finish_streaming)
            
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.show_error(error_msg))

    def start_research_flow(self):
        """Inicia el flujo de investigación web"""
        topic = simpledialog.askstring("Investigación", "¿Sobre qué tema quieres que investigue en profundidad?")
        
        if not topic:
            return
            
        self.status_bar.set_status(f"Investigando sobre '{topic}' en la web...")
        
        # Deshabilitar UI durante investigación
        # self.input_text.configure(state=tk.DISABLED) # No bloqueamos todo, dejamos que el usuario espere
        
        thread = threading.Thread(target=self.run_research, args=(topic,))
        thread.daemon = True
        thread.start()
        
    def run_research(self, topic):
        """Ejecuta la investigación en segundo plano"""
        try:
            researcher = WebResearcher()
            success, message = researcher.deep_research(topic)
            
            if success:
                # Recargar conocimiento
                self.chat_engine.reload_knowledge()
                
                # Feedback positivo
                self.after(0, lambda: self.add_system_message(f"✅ {message}"))
                self.after(0, lambda: self.status_bar.set_status("Investigación completada"))
                
                # Actualizar stats
                stats = self.chat_engine.get_stats()
                text_stats = f"Msgs: {stats['message_count']} | Docs: {stats['rag']['documents']} | Memoria: {stats['memory']['total_size_mb']:.2f}MB"
                self.after(0, lambda: self.status_bar.set_stats(text_stats))
                
                # Si el chat está vacío, Aurora podría comentar algo sobre lo investigado
                # (Opcional, por ahora solo avisamos)
                
            else:
                self.after(0, lambda: self.show_error(f"Investigación fallida: {message}"))
                self.after(0, lambda: self.status_bar.set_status("Error en investigación"))
                
        except Exception as e:
            self.after(0, lambda: self.show_error(f"Error crítico en investigación: {str(e)}"))
            self.after(0, lambda: self.status_bar.set_status("Error crítico"))

class ApuntesPanel:
    """Panel de edición de apuntes con resaltado Markdown en tiempo real (WYSIWYG-ish)"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.setup_tags()
        self.highlight_markdown()
        
    def setup_ui(self):
        # Contenedor superior para controles
        self.header = tk.Frame(self.parent, bg=ModernStyle.BG_SECONDARY, height=50)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        # Título / Nombre de archivo
        tk.Label(
            self.header, 
            text="Archivo:", 
            bg=ModernStyle.BG_SECONDARY, 
            fg=ModernStyle.TEXT_SECONDARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL)
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.filename_entry = tk.Entry(
            self.header,
            bg=ModernStyle.BG_TERTIARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            width=20
        )
        self.filename_entry.insert(0, "mis_notas.md")
        self.filename_entry.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Selector de tipo
        self.ext_var = tk.StringVar(value=".md")
        ext_md = tk.Radiobutton(
            self.header, text="Markdown", variable=self.ext_var, value=".md",
            bg=ModernStyle.BG_SECONDARY, fg=ModernStyle.TEXT_PRIMARY,
            selectcolor=ModernStyle.BG_TERTIARY, activebackground=ModernStyle.BG_SECONDARY,
            command=self.on_content_change
        )
        ext_md.pack(side=tk.LEFT, padx=5)
        
        ext_txt = tk.Radiobutton(
            self.header, text="Texto Plano", variable=self.ext_var, value=".txt",
            bg=ModernStyle.BG_SECONDARY, fg=ModernStyle.TEXT_PRIMARY,
            selectcolor=ModernStyle.BG_TERTIARY, activebackground=ModernStyle.BG_SECONDARY,
            command=self.on_content_change
        )
        ext_txt.pack(side=tk.LEFT, padx=5)
        
        # Botones Save/Load
        tk.Button(
            self.header, text="💾 Guardar", bg=ModernStyle.ACCENT_PRIMARY, fg=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT, command=self.save_file, cursor="hand2"
        ).pack(side=tk.RIGHT, padx=10)
        
        tk.Button(
            self.header, text="📂 Cargar", bg=ModernStyle.ACCENT_SECONDARY, fg=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT, command=self.load_file, cursor="hand2"
        ).pack(side=tk.RIGHT, padx=5)

        # Editor Unificado
        self.editor_container = tk.Frame(self.parent, bg=ModernStyle.BG_PRIMARY)
        self.editor_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar para el editor
        scrollbar = ttk.Scrollbar(self.editor_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.editor = tk.Text(
            self.editor_container,
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            insertbackground=ModernStyle.TEXT_PRIMARY,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            wrap=tk.WORD,
            undo=True,
            relief=tk.FLAT,
            padx=20,
            pady=20,
            yscrollcommand=scrollbar.set
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        scrollbar.configure(command=self.editor.yview)
        
        self.editor.bind("<KeyRelease>", self.on_content_change)
        
        # Directorio de notas
        self.notes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notas")
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)
            
        # Contenido inicial
        initial_text = "# Mis Apuntes\n\nEscribe aquí tus notas en **Markdown** o *Texto Plano*.\nTodo en un solo lugar.\n\n- Punto 1\n- Punto 2\n\n¡Disfruta!"
        self.editor.insert("1.0", initial_text)

    def setup_tags(self):
        """Configura las etiquetas para el resaltado"""
        self.editor.tag_configure("h1", font=(ModernStyle.FONT_FAMILY, 24, "bold"), foreground=ModernStyle.ACCENT_PRIMARY)
        self.editor.tag_configure("h2", font=(ModernStyle.FONT_FAMILY, 20, "bold"), foreground=ModernStyle.ACCENT_GRADIENT)
        self.editor.tag_configure("h3", font=(ModernStyle.FONT_FAMILY, 18, "bold"), foreground=ModernStyle.ACCENT_SECONDARY)
        self.editor.tag_configure("bold", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"), foreground=ModernStyle.ACCENT_PRIMARY)
        self.editor.tag_configure("italic", font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "italic"), foreground=ModernStyle.ACCENT_GRADIENT)
        self.editor.tag_configure("list_bullet", foreground=ModernStyle.ACCENT_SECONDARY, font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"))
        self.editor.tag_configure("syntax", elide=True) # Tag para ocultar tokens

    def on_content_change(self, event=None):
        self.highlight_markdown()

    def highlight_markdown(self):
        """Aplica resaltado Markdown al editor y oculta la sintaxis en tiempo real"""
        is_markdown = self.ext_var.get() == ".md"
        
        # Limpiar etiquetas existentes
        for tag in ["h1", "h2", "h3", "bold", "italic", "list_bullet", "syntax"]:
            self.editor.tag_remove(tag, "1.0", tk.END)
            
        if not is_markdown:
            return

        # Resaltado por líneas
        content = self.editor.get("1.0", tk.END)
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_idx = i + 1
            
            # Encabezados
            if line.startswith('# '):
                self.editor.tag_add("syntax", f"{line_idx}.0", f"{line_idx}.2") # Oculta "# "
                self.editor.tag_add("h1", f"{line_idx}.2", f"{line_idx}.end")
            elif line.startswith('## '):
                self.editor.tag_add("syntax", f"{line_idx}.0", f"{line_idx}.3") # Oculta "## "
                self.editor.tag_add("h2", f"{line_idx}.3", f"{line_idx}.end")
            elif line.startswith('### '):
                self.editor.tag_add("syntax", f"{line_idx}.0", f"{line_idx}.4") # Oculta "### "
                self.editor.tag_add("h3", f"{line_idx}.4", f"{line_idx}.end")
            
            # Puntos de lista
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                start_offset = line.find('- ') if '- ' in line else line.find('* ')
                # En lugar de ocultar el guión, lo estilizamos como un punto (bullet)
                # O si el usuario quiere ocultarlo totalmente, usamos syntax. 
                # Por ahora, ocultamos el guión y dejamos un espacio o lo estilizamos.
                # Vamos a ocultar el guión y poner un punto virtual si fuera posible, 
                # pero en tk.Text eliding es total. Así que lo estilizamos llamativo.
                self.editor.tag_add("list_bullet", f"{line_idx}.{start_offset}", f"{line_idx}.{start_offset+1}")

        # Resaltado inline (Negrita y Cursiva) con ocultación de tokens
        # Negrita: **texto**
        for match in re.finditer(r'\*\*(.*?)\*\*', content):
            start_pos, end_pos = match.span()
            inner_start = start_pos + 2
            inner_end = end_pos - 2
            
            # Índices para los tokens ** y **
            s1 = self.editor.index(f"1.0 + {start_pos} chars")
            s2 = self.editor.index(f"1.0 + {inner_start} chars")
            e1 = self.editor.index(f"1.0 + {inner_end} chars")
            e2 = self.editor.index(f"1.0 + {end_pos} chars")
            
            self.editor.tag_add("syntax", s1, s2) # Oculta primer **
            self.editor.tag_add("bold", s2, e1)   # Estiliza interior
            self.editor.tag_add("syntax", e1, e2) # Oculta segundo **
            
        # Cursiva: *texto* (evitando los ** de negrita)
        for match in re.finditer(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', content):
            start_pos, end_pos = match.span()
            inner_start = start_pos + 1
            inner_end = end_pos - 1
            
            s1 = self.editor.index(f"1.0 + {start_pos} chars")
            s2 = self.editor.index(f"1.0 + {inner_start} chars")
            e1 = self.editor.index(f"1.0 + {inner_end} chars")
            e2 = self.editor.index(f"1.0 + {end_pos} chars")
            
            self.editor.tag_add("syntax", s1, s2)
            self.editor.tag_add("italic", s2, e1)
            self.editor.tag_add("syntax", e1, e2)

    def save_file(self):
        filename = self.filename_entry.get()
        if not filename:
            messagebox.showwarning("Aviso", "Por favor ingresa un nombre para el archivo.")
            return
            
        if not (filename.endswith('.md') or filename.endswith('.txt')):
            filename += self.ext_var.get()
            
        path = os.path.join(self.notes_dir, filename)
        content = self.editor.get("1.0", tk.END)
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Éxito", f"Archivo guardado correctamente en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def load_file(self):
        filename = self.filename_entry.get()
        if not filename:
            messagebox.showwarning("Aviso", "Por favor ingresa un nombre para cargar.")
            return
            
        path = os.path.join(self.notes_dir, filename)
        if not os.path.exists(path):
            messagebox.showerror("Error", f"El archivo no existe en el directorio de notas.")
            return
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)
            
            # Auto-detectar extensión
            if filename.endswith('.md'):
                self.ext_var.set(".md")
            else:
                self.ext_var.set(".txt")
                
            self.highlight_markdown()
            messagebox.showinfo("Éxito", "Archivo cargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

