# app.py (versión mejorada)
import streamlit as st
import pandas as pd
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import json

# --- CONFIGURACIÓN MEJORADA ---
class Configuracion:
    CATALOGO = {
        "tipos_mueble": {
            "SILLA": {"precio_base": 150.00, "descripcion": "Silla ergonómica personalizada"},
            "MESA": {"precio_base": 300.00, "descripcion": "Mesa de centro o comedor"},
            "SOFÁ": {"precio_base": 800.00, "descripcion": "Sofá de 3 plazas personalizado"},
            "ESTANTERÍA": {"precio_base": 250.00, "descripcion": "Estantería modular"},
            "ESCRITORIO": {"precio_base": 400.00, "descripcion": "Escritorio de trabajo"}
        },
        # ... (resto del catálogo)
    }
    
    PATRONES_ENTRADA = {
        "saludos": ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"],
        "afirmaciones": ["sí", "si", "por favor", "ok", "vale", "correcto", "confirmar"],
        "negaciones": ["no", "n", "cancelar", "reiniciar"],
        "acciones": ["modificar", "cambiar", "eliminar", "quitar", "borrar"]
    }

# --- CLASES MEJORADAS ---
class ItemPedido:
    def __init__(self, tipo_mueble: str, material: str, color: str, dimensiones: str, cantidad: int = 1):
        self.tipo_mueble = tipo_mueble
        self.material = material
        self.color = color
        self.dimensiones = dimensiones
        self.cantidad = cantidad
        self.id = f"{tipo_mueble}_{material}_{color}_{dimensiones}_{cantidad}"
    
    def to_dict(self) -> Dict:
        return {
            'tipo_mueble': self.tipo_mueble,
            'material': self.material,
            'color': self.color,
            'dimensiones': self.dimensiones,
            'cantidad': self.cantidad,
            'precio_unitario': self.calcular_precio_unitario(),
            'precio_total': self.calcular_precio_total()
        }

class PedidoManager:
    def __init__(self):
        self.reiniciar_pedido()
    
    def reiniciar_pedido(self):
        self.items = []
        self.item_actual = None
        self.estado = EstadoPedido.INICIO
        self.nombre_cliente = None
        self.email = None
        self.fecha_creacion = datetime.now()
    
    def exportar_pedido(self) -> Dict:
        return {
            'cliente': self.nombre_cliente,
            'email': self.email,
            'fecha': self.fecha_creacion.isoformat(),
            'items': [item.to_dict() for item in self.items],
            'total': self.calcular_total_pedido(),
            'estado': self.estado
        }

# --- PROCESAMIENTO DE LENGUAJE NATURAL MEJORADO ---
class ProcesadorLenguajeNatural:
    def __init__(self):
        self.patrones = {
            'cantidad': r'(\d+)\s*(?:unidades?|uds?|x|\*)',
            'dimension_multiple': r'(\d+)\s*(pequeñ[ao]s?|median[ao]s?|grandes?|estándar)',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        }
    
    def extraer_entidades(self, texto: str) -> Dict:
        texto = texto.lower()
        entidades = {
            'cantidades': [],
            'dimensiones': [],
            'tipos_mueble': [],
            'materiales': [],
            'colores': [],
            'acciones': []
        }
        
        # Extraer cantidades
        cantidades = re.findall(self.patrones['cantidad'], texto)
        entidades['cantidades'] = [int(c[0]) for c in cantidades]
        
        # Detectar acciones
        for accion in Configuracion.PATRONES_ENTRADA["acciones"]:
            if accion in texto:
                entidades['acciones'].append(accion)
        
        return entidades

# --- INTERFAZ MEJORADA ---
def inicializar_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'designbot' not in st.session_state:
        st.session_state.designbot = DesignBotLLM()
    if 'procesador_nlp' not in st.session_state:
        st.session_state.nlp = ProcesadorLenguajeNatural()

def crear_sidebar():
    with st.sidebar:
        st.header("🎯 Panel de Control")
        
        # Estadísticas rápidas
        pedido_manager = st.session_state.designbot.pedido_manager
        st.metric("📦 Items en pedido", len(pedido_manager.items))
        st.metric("💰 Total", f"${pedido_manager.calcular_total_pedido():.2f}")
        
        # Acciones rápidas
        st.markdown("---")
        st.subheader("⚡ Acciones Rápidas")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nuevo Pedido", use_container_width=True):
                st.session_state.designbot = DesignBotLLM()
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("💾 Exportar", use_container_width=True) and pedido_manager.items:
                pedido_json = pedido_manager.exportar_pedido()
                st.download_button(
                    label="Descargar JSON",
                    data=json.dumps(pedido_json, indent=2),
                    file_name=f"pedido_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )

def mostrar_chat():
    st.subheader("💬 DesignBot Assistant")
    
    # Contenedor de chat con mejoras visuales
    chat_container = st.container(height=400)
    
    with chat_container:
        for mensaje in st.session_state.chat_history:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])
                if mensaje.get("timestamp"):
                    st.caption(mensaje["timestamp"])
            
            # Separador entre mensajes
            if mensaje != st.session_state.chat_history[-1]:
                st.markdown("---")

def panel_control_pedido():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Gestión de Pedido")
    
    pedido_manager = st.session_state.designbot.pedido_manager
    
    if pedido_manager.items:
        # Editor de items en tiempo real
        st.sidebar.markdown("**✏️ Editar Items:**")
        for i, item in enumerate(pedido_manager.items):
            with st.sidebar.expander(f"Item {i+1}: {item.tipo_mueble.title()}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    nueva_cantidad = st.number_input(
                        "Cantidad:", 
                        min_value=1, 
                        value=item.cantidad,
                        key=f"cant_{i}"
                    )
                with col2:
                    if st.button("🗑️", key=f"del_{i}"):
                        pedido_manager.eliminar_item(i)
                        st.rerun()
                
                if nueva_cantidad != item.cantidad:
                    pedido_manager.modificar_cantidad_item(i, nueva_cantidad)
                    st.rerun()

def main():
    st.set_page_config(
        page_title="DesignBot Pro - Muebles Personalizados",
        page_icon="🛋️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inicialización
    inicializar_session_state()
    
    # Header principal
    st.title("🛋️ DesignBot Pro")
    st.markdown("Sistema inteligente para pedidos de muebles personalizados")
    st.markdown("---")
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mostrar_chat()
        
        # Input de usuario mejorado
        with st.container():
            st.markdown("### 💭 Tu mensaje:")
            user_input = st.chat_input(
                "Escribe tu pedido aquí... (ej: '2 sillas pequeñas de madera noble')",
                key="user_input"
            )
            
            if user_input:
                procesar_mensaje_usuario(user_input)

    with col2:
        crear_sidebar()
        panel_control_pedido()
        
        # Información del catálogo
        st.markdown("---")
        st.subheader("📚 Catálogo Rápido")
        with st.expander("Ver precios y opciones"):
            st.json(Configuracion.CATALOGO)

def procesar_mensaje_usuario(user_input: str):
    """Procesa el mensaje del usuario y actualiza la interfaz"""
    # Agregar mensaje del usuario al historial
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Procesar con DesignBot
    respuesta = st.session_state.designbot.procesar_mensaje(user_input)
    
    # Agregar respuesta del bot
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": respuesta,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    st.rerun()

if __name__ == "__main__":
    main()
