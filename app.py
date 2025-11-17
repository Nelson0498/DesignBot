# app.py
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
        "materiales": {
            "MADERA_NOBLE": {"precio_extra": 200.00, "descripcion": "Roble o nogal macizo"},
            "MADERA_MDF": {"precio_extra": 50.00, "descripcion": "MDF lacado"},
            "METAL": {"precio_extra": 100.00, "descripcion": "Acero inoxidable"},
            "VIDRIO": {"precio_extra": 120.00, "descripcion": "Vidrio templado"},
            "BAMBÚ": {"precio_extra": 80.00, "descripcion": "Bambú sostenible"},
            "MADERA_RECICLADA": {"precio_extra": 90.00, "descripcion": "Madera reciclada tratada"}
        },
        "colores": {
            "NATURAL": {"precio_extra": 0.00, "descripcion": "Acabado natural"},
            "BLANCO": {"precio_extra": 30.00, "descripcion": "Acabado blanco mate"},
            "NEGRO": {"precio_extra": 40.00, "descripcion": "Acabado negro brillante"},
            "MADERA_OSCURA": {"precio_extra": 60.00, "descripcion": "Tono caoba o wengué"},
            "GRIS": {"precio_extra": 35.00, "descripcion": "Gris moderno"}
        },
        "dimensiones": {
            "PEQUEÑO": {"factor": 0.8, "descripcion": "Dimensiones reducidas"},
            "ESTÁNDAR": {"factor": 1.0, "descripcion": "Dimensiones estándar"},
            "GRANDE": {"factor": 1.3, "descripcion": "Dimensiones ampliadas"}
        }
    }
    
    PATRONES_ENTRADA = {
        "saludos": ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"],
        "afirmaciones": ["sí", "si", "por favor", "ok", "vale", "correcto", "confirmar"],
        "negaciones": ["no", "n", "cancelar", "reiniciar"],
        "acciones": ["modificar", "cambiar", "eliminar", "quitar", "borrar"]
    }

# --- ESTADOS DEL PEDIDO ---
class EstadoPedido:
    INICIO = "inicio"
    ESPERANDO_TIPO = "esperando_tipo"
    ESPERANDO_MATERIAL = "esperando_material"
    ESPERANDO_COLOR = "esperando_color"
    ESPERANDO_DIMENSION = "esperando_dimension"
    ESPERANDO_CANTIDAD = "esperando_cantidad"
    CONFIRMANDO_ITEM = "confirmando_item"
    AGREGANDO_MAS = "agregando_mas"
    FINALIZANDO = "finalizando"
    ESPERANDO_CONTACTO = "esperando_contacto"
    COMPLETADO = "completado"

# --- CLASES DEL SISTEMA ---
class ItemPedido:
    def __init__(self, tipo_mueble: str, material: str, color: str, dimensiones: str, cantidad: int = 1):
        self.tipo_mueble = tipo_mueble
        self.material = material
        self.color = color
        self.dimensiones = dimensiones
        self.cantidad = cantidad
        self.id = f"{tipo_mueble}_{material}_{color}_{dimensiones}_{cantidad}"
    
    def calcular_precio_unitario(self) -> float:
        precio_base = Configuracion.CATALOGO["tipos_mueble"][self.tipo_mueble]["precio_base"]
        extra_material = Configuracion.CATALOGO["materiales"][self.material]["precio_extra"]
        extra_color = Configuracion.CATALOGO["colores"][self.color]["precio_extra"]
        factor_dimensiones = Configuracion.CATALOGO["dimensiones"][self.dimensiones]["factor"]
        subtotal = precio_base + extra_material + extra_color
        return subtotal * factor_dimensiones

    def calcular_precio_total(self) -> float:
        return self.calcular_precio_unitario() * self.cantidad

    def obtener_descripcion(self) -> str:
        return f"{self.cantidad}x {self.tipo_mueble.title()} {self.dimensiones.title()}"

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
    
    def iniciar_nuevo_item(self, tipo_mueble: str, cantidad: int = 1):
        self.item_actual = {
            'tipo_mueble': tipo_mueble,
            'material': None,
            'color': None,
            'dimensiones': None,
            'cantidad': cantidad
        }

    def actualizar_item_actual(self, campo: str, valor: Any):
        if self.item_actual:
            self.item_actual[campo] = valor

    def agregar_item_actual_al_pedido(self):
        if self.item_actual and all([
            self.item_actual['tipo_mueble'],
            self.item_actual['material'], 
            self.item_actual['color'],
            self.item_actual['dimensiones']
        ]):
            item = ItemPedido(
                self.item_actual['tipo_mueble'],
                self.item_actual['material'],
                self.item_actual['color'], 
                self.item_actual['dimensiones'],
                self.item_actual['cantidad']
            )
            self.items.append(item)
            return True
        return False

    def modificar_cantidad_item(self, index: int, nueva_cantidad: int):
        if 0 <= index < len(self.items):
            self.items[index].cantidad = nueva_cantidad
            return True
        return False

    def eliminar_item(self, index: int):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            return True
        return False

    def calcular_total_pedido(self) -> float:
        return sum(item.calcular_precio_total() for item in self.items)

    def obtener_resumen_detallado(self) -> str:
        if not self.items:
            return "🛒 **Tu pedido está vacío**\n\n¡Agrega algunos productos para comenzar!"
        
        resumen = "📋 **RESUMEN DE TU PEDIDO**\n\n"
        for i, item in enumerate(self.items, 1):
            precio_unitario = item.calcular_precio_unitario()
            precio_total = item.calcular_precio_total()
            resumen += f"{i}. **{item.obtener_descripcion()}**\n"
            resumen += f"   📦 Material: {item.material.replace('_', ' ').title()}\n"
            resumen += f"   🎨 Color: {item.color.replace('_', ' ').title()}\n"
            resumen += f"   💰 ${precio_unitario:.2f} c/u → ${precio_total:.2f} total\n\n"
        
        resumen += f"🎯 **TOTAL DEL PEDIDO: ${self.calcular_total_pedido():.2f}**"
        return resumen

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

# --- DESIGNBOT LLM (CLASE PRINCIPAL) ---
class DesignBotLLM:
    def __init__(self):
        self.pedido_manager = PedidoManager()
        self.ultima_respuesta = None

    def extraer_cantidad(self, texto: str) -> int:
        texto = texto.lower()
        numeros = re.findall(r'\d+', texto)
        if numeros:
            return int(numeros[0])
        
        palabras_cantidad = {
            "una": 1, "un": 1, "uno": 1, "dos": 2, "tres": 3,
            "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
            "ocho": 8, "nueve": 9, "diez": 10
        }
        
        for palabra, cantidad in palabras_cantidad.items():
            if palabra in texto:
                return cantidad
        return 1

    def procesar_modificacion_pedido(self, input_clean: str) -> str:
        """Procesa solicitudes de modificación del pedido"""
        if "eliminar" in input_clean or "quitar" in input_clean:
            numeros = re.findall(r'\d+', input_clean)
            if numeros:
                index = int(numeros[0]) - 1
                if self.pedido_manager.eliminar_item(index):
                    return f"✅ **Item {index + 1} eliminado del pedido**\n\n{self.pedido_manager.obtener_resumen_detallado()}"
        
        if "modificar" in input_clean or "cambiar" in input_clean:
            numeros = re.findall(r'\d+', input_clean)
            if numeros:
                index = int(numeros[0]) - 1
                if 0 <= index < len(self.pedido_manager.items):
                    nueva_cantidad = self.extraer_cantidad(input_clean)
                    if nueva_cantidad > 0:
                        if self.pedido_manager.modificar_cantidad_item(index, nueva_cantidad):
                            return f"✅ **Cantidad modificada**\n\n{self.pedido_manager.obtener_resumen_detallado()}"
        return None

    def procesar_mensaje(self, user_input: str) -> str:
        # Implementación simplificada - puedes copiar tu implementación original aquí
        input_clean = user_input.lower().strip()
        
        # Respuesta básica por estado
        if self.pedido_manager.estado == EstadoPedido.INICIO:
            return "¡Hola! 👋 Soy DesignBot. ¿Te gustaría diseñar algún mueble personalizado? (responde 'sí' para comenzar)"
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_TIPO:
            return "¿Qué tipo de mueble te gustaría? Tenemos: Silla, Mesa, Sofá, Estantería o Escritorio"
        
        return "¿En qué más puedo ayudarte con tu pedido?"

# --- INTERFAZ STREAMLIT ---
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
            if st.button("📋 Resumen", use_container_width=True) and pedido_manager.items:
                st.info(pedido_manager.obtener_resumen_detallado())

def mostrar_chat():
    st.subheader("💬 DesignBot Assistant")
    
    # Contenedor de chat
    chat_container = st.container(height=400)
    
    with chat_container:
        for mensaje in st.session_state.chat_history:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])
                if mensaje.get("timestamp"):
                    st.caption(mensaje["timestamp"])

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
        
        # Input de usuario
        user_input = st.chat_input(
            "Escribe tu pedido aquí... (ej: '2 sillas pequeñas de madera noble')"
        )
        
        if user_input:
            procesar_mensaje_usuario(user_input)

    with col2:
        crear_sidebar()
        panel_control_pedido()
        
        # Información del estado
        st.markdown("---")
        st.subheader("📊 Estado del Sistema")
        
        estados = {
            EstadoPedido.INICIO: "⚪ Esperando inicio",
            EstadoPedido.ESPERANDO_TIPO: "🟡 Eligiendo tipo",
            EstadoPedido.ESPERANDO_MATERIAL: "🟡 Seleccionando material", 
            EstadoPedido.ESPERANDO_COLOR: "🟡 Escogiendo color",
            EstadoPedido.ESPERANDO_DIMENSION: "🟡 Definiendo dimensiones",
            EstadoPedido.AGREGANDO_MAS: "🔵 Agregando más items",
            EstadoPedido.FINALIZANDO: "🟢 Finalizando pedido",
            EstadoPedido.ESPERANDO_CONTACTO: "📝 Esperando contacto",
            EstadoPedido.COMPLETADO: "🎉 Pedido completado"
        }
        
        estado_actual = estados.get(
            st.session_state.designbot.pedido_manager.estado, 
            "⚪ Desconocido"
        )
        st.info(f"**Estado:** {estado_actual}")

if __name__ == "__main__":
    main()
