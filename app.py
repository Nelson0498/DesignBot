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

# --- DESIGNBOT LLM (CON LÓGICA COMPLETA) ---
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
        input_clean = user_input.lower().strip()
        
        # Evitar procesar si es la misma respuesta
        if self.ultima_respuesta and user_input.strip() == "":
            return self.ultima_respuesta

        # 1. SALUDOS
        if any(saludo in input_clean for saludo in ["hola", "hi", "hello", "buenos días", "buenas"]):
            if "me llamo" in input_clean or "soy" in input_clean or "nombre" in input_clean:
                if "me llamo" in input_clean:
                    nombre = input_clean.split("me llamo")[1].strip()
                elif "soy" in input_clean:
                    nombre = input_clean.split("soy")[1].strip()
                else:
                    nombre = "cliente"
                self.pedido_manager.nombre_cliente = nombre.split()[0].title()
                respuesta = f"¡Hola {self.pedido_manager.nombre_cliente}! 👋 Soy DesignBot. ¿Te gustaría diseñar algún mueble personalizado?"
                self.ultima_respuesta = respuesta
                return respuesta
            
            respuesta = "¡Hola! 👋 Soy DesignBot, tu asistente para diseño de muebles personalizados. ¿Te gustaría diseñar algún mueble?"
            self.ultima_respuesta = respuesta
            return respuesta

        # 2. INICIAR PEDIDO
        if (any(frase in input_clean for frase in ["sí", "si", "por favor", "quiero", "diseñar", "mueble", "personalizar", "empezar", "comenzar"]) 
            and self.pedido_manager.estado == EstadoPedido.INICIO):
            
            self.pedido_manager.estado = EstadoPedido.ESPERANDO_TIPO
            respuesta = "¡Excelente! 🛋️ ¿Qué tipo de mueble te gustaría diseñar?\n\n" + \
                       "• Silla\n• Mesa\n• Sofá\n• Estantería\n• Escritorio"
            self.ultima_respuesta = respuesta
            return respuesta

        # 3. DETECCIÓN DE TIPO DE MUEBLE
        tipos = {
            "silla": "SILLA", "sillas": "SILLA",
            "mesa": "MESA", "mesas": "MESA", 
            "sofá": "SOFÁ", "sofa": "SOFÁ", "sofas": "SOFÁ",
            "estantería": "ESTANTERÍA", "estanteria": "ESTANTERÍA", "estanterías": "ESTANTERÍA",
            "escritorio": "ESCRITORIO", "escritorios": "ESCRITORIO"
        }

        for tipo_key, tipo_val in tipos.items():
            if tipo_key in input_clean:
                if self.pedido_manager.estado in [EstadoPedido.INICIO, EstadoPedido.ESPERANDO_TIPO, EstadoPedido.AGREGANDO_MAS]:
                    cantidad = self.extraer_cantidad(input_clean)
                    self.pedido_manager.iniciar_nuevo_item(tipo_val, cantidad)
                    self.pedido_manager.estado = EstadoPedido.ESPERANDO_MATERIAL
                    cantidad_texto = f" ({cantidad} unidad{'es' if cantidad > 1 else ''})" if cantidad > 1 else ""
                    respuesta = f"✅ **{tipo_val.title()}{cantidad_texto} seleccionado**\n\n" + \
                               "¿Qué material prefieres?\n\n" + \
                               "• Madera noble\n• Madera MDF\n• Metal\n• Vidrio\n• Bambú\n• Madera reciclada"
                    self.ultima_respuesta = respuesta
                    return respuesta

        # 4. DETECCIÓN DE MATERIAL
        materiales = {
            "madera noble": "MADERA_NOBLE", "roble": "MADERA_NOBLE", "nogal": "MADERA_NOBLE", 
            "madera": "MADERA_NOBLE", "noble": "MADERA_NOBLE",
            "mdf": "MADERA_MDF", "madera mdf": "MADERA_MDF",
            "metal": "METAL", "acero": "METAL", "metálico": "METAL",
            "vidrio": "VIDRIO", "cristal": "VIDRIO",
            "bambú": "BAMBÚ", "bambu": "BAMBÚ",
            "madera reciclada": "MADERA_RECICLADA", "reciclada": "MADERA_RECICLADA"
        }

        for material_key, material_val in materiales.items():
            if material_key in input_clean and self.pedido_manager.estado == EstadoPedido.ESPERANDO_MATERIAL:
                self.pedido_manager.actualizar_item_actual('material', material_val)
                self.pedido_manager.estado = EstadoPedido.ESPERANDO_COLOR
                respuesta = f"✅ **Material {material_val.replace('_', ' ').title()} seleccionado**\n\n" + \
                           "¿Qué color prefieres?\n\n" + \
                           "• Natural\n• Blanco\n• Negro\n• Madera oscura\n• Gris"
                self.ultima_respuesta = respuesta
                return respuesta

        # 5. DETECCIÓN DE COLOR
        colores = {
            "natural": "NATURAL", "color natural": "NATURAL", "sin color": "NATURAL",
            "blanco": "BLANCO", "color blanco": "BLANCO",
            "negro": "NEGRO", "color negro": "NEGRO",
            "madera oscura": "MADERA_OSCURA", "oscuro": "MADERA_OSCURA", "caoba": "MADERA_OSCURA", "wengué": "MADERA_OSCURA",
            "gris": "GRIS", "color gris": "GRIS"
        }

        for color_key, color_val in colores.items():
            if color_key in input_clean and self.pedido_manager.estado == EstadoPedido.ESPERANDO_COLOR:
                self.pedido_manager.actualizar_item_actual('color', color_val)
                self.pedido_manager.estado = EstadoPedido.ESPERANDO_DIMENSION
                respuesta = f"✅ **Color {color_key.title()} seleccionado**\n\n" + \
                           "¿Qué dimensiones prefieres?\n\n" + \
                           "• Pequeño\n• Estándar\n• Grande"
                self.ultima_respuesta = respuesta
                return respuesta

        # 6. DETECCIÓN DE DIMENSIONES
        dimensiones_map = {
            "pequeño": "PEQUEÑO", "pequeña": "PEQUEÑO", "pequeno": "PEQUEÑO", "chico": "PEQUEÑO", "s": "PEQUEÑO",
            "estándar": "ESTÁNDAR", "estandar": "ESTÁNDAR", "normal": "ESTÁNDAR", "mediano": "ESTÁNDAR", "m": "ESTÁNDAR",
            "grande": "GRANDE", "grand": "GRANDE", "l": "GRANDE"
        }

        for dim_key, dim_val in dimensiones_map.items():
            if dim_key in input_clean and self.pedido_manager.estado == EstadoPedido.ESPERANDO_DIMENSION:
                self.pedido_manager.actualizar_item_actual('dimensiones', dim_val)
                if self.pedido_manager.agregar_item_actual_al_pedido():
                    self.pedido_manager.estado = EstadoPedido.AGREGANDO_MAS
                    respuesta = f"✅ **{dim_val.title()} agregado al pedido!** 🎉\n\n" + \
                               f"{self.pedido_manager.obtener_resumen_detallado()}\n\n" + \
                               "¿Te gustaría agregar otro mueble? (responde 'sí' para agregar más o 'no' para finalizar)"
                    self.ultima_respuesta = respuesta
                    return respuesta

        # 7. MANEJO DE "¿QUIERES AGREGAR MÁS?"
        if self.pedido_manager.estado == EstadoPedido.AGREGANDO_MAS:
            if any(palabra in input_clean for palabra in ["sí", "si", "s", "quiero", "agregar", "otro", "más", "mas", "otra"]):
                self.pedido_manager.estado = EstadoPedido.ESPERANDO_TIPO
                respuesta = "¡Perfecto! ¿Qué otro mueble te gustaría agregar?\n\n" + \
                           "• Silla\n• Mesa\n• Sofá\n• Estantería\n• Escritorio"
                self.ultima_respuesta = respuesta
                return respuesta
            elif any(palabra in input_clean for palabra in ["no", "n", "listo", "terminar", "finalizar", "eso es todo"]):
                self.pedido_manager.estado = EstadoPedido.FINALIZANDO
                respuesta = f"📦 **PEDIDO COMPLETO**\n\n{self.pedido_manager.obtener_resumen_detallado()}\n\n" + \
                           "¿Todo correcto? (responde 'sí' para confirmar o 'modificar' para hacer cambios)"
                self.ultima_respuesta = respuesta
                return respuesta

        # 8. CONFIRMACIÓN FINAL
        if (any(palabra in input_clean for palabra in ["sí", "si", "confirmar", "correcto", "ok", "vale"]) 
            and self.pedido_manager.estado == EstadoPedido.FINALIZANDO):
            
            self.pedido_manager.estado = EstadoPedido.ESPERANDO_CONTACTO
            nombre_cliente = f", {self.pedido_manager.nombre_cliente}" if self.pedido_manager.nombre_cliente else ""
            respuesta = f"📧 **INFORMACIÓN DE CONTACTO**{nombre_cliente}:\n\n" + \
                       "¡Perfecto! Por favor, compártenos tu email para contactarte:"
            self.ultima_respuesta = respuesta
            return respuesta

        # 9. FINALIZACIÓN
        if self.pedido_manager.estado == EstadoPedido.ESPERANDO_CONTACTO:
            # Validar email básico
            if "@" in user_input and "." in user_input:
                self.pedido_manager.estado = EstadoPedido.COMPLETADO
                total = self.pedido_manager.calcular_total_pedido()
                nombre_cliente = f", {self.pedido_manager.nombre_cliente}" if self.pedido_manager.nombre_cliente else ""
                respuesta = f"""🎉 **¡PEDIDO CONFIRMADO!** 🎉{nombre_cliente}

{self.pedido_manager.obtener_resumen_detallado()}

📧 **Email de contacto:** {user_input}

📅 **Proceso:**
1. Confirmación por email en 24 horas
2. Diseño técnico (2-3 días)  
3. Fabricación (7-10 días)
4. Entrega programada

¡Gracias por tu pedido! 🛋️"""
                # Reiniciar para nuevo pedido
                self.pedido_manager.reiniciar_pedido()
                self.ultima_respuesta = respuesta
                return respuesta
            else:
                respuesta = "Por favor, ingresa un email válido:"
                self.ultima_respuesta = respuesta
                return respuesta

        # 10. PROCESAR MODIFICACIONES AL PEDIDO
        if self.pedido_manager.items and any(palabra in input_clean for palabra in ["modificar", "cambiar", "eliminar", "quitar", "quita", "borrar"]):
            resultado_modificacion = self.procesar_modificacion_pedido(input_clean)
            if resultado_modificacion:
                self.ultima_respuesta = resultado_modificacion
                return resultado_modificacion

        # 11. CONSULTA DE RESUMEN
        if any(palabra in input_clean for palabra in ["resumen", "pedido", "carrito", "qué tengo", "ver pedido"]):
            if self.pedido_manager.items:
                respuesta = f"📋 **TU PEDIDO ACTUAL:**\n\n{self.pedido_manager.obtener_resumen_detallado()}\n\n" + \
                           "¿Quieres agregar algo más o finalizar?"
                self.ultima_respuesta = respuesta
                return respuesta
            else:
                respuesta = "🛒 Tu pedido está vacío. ¿Te gustaría agregar algún mueble?"
                self.ultima_respuesta = respuesta
                return respuesta

        # 12. CANCELAR
        if any(palabra in input_clean for palabra in ["cancelar", "reiniciar", "empezar de nuevo"]):
            self.pedido_manager.reiniciar_pedido()
            respuesta = "🔄 **Pedido cancelado**. ¿Te gustaría comenzar un nuevo diseño?"
            self.ultima_respuesta = respuesta
            return respuesta

        # --- RESPUESTAS POR ESTADO ---
        if self.pedido_manager.estado == EstadoPedido.INICIO:
            respuesta = "¡Hola! ¿Te gustaría diseñar un mueble personalizado? (responde 'sí' para comenzar)"
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_TIPO:
            respuesta = "Por favor, elige el tipo de mueble: Silla, Mesa, Sofá, Estantería o Escritorio"
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_MATERIAL:
            respuesta = "¿Qué material prefieres? (Madera noble, MDF, Metal, Vidrio, Bambú o Madera reciclada)"
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_COLOR:
            respuesta = "¿Qué color te gustaría? (Natural, Blanco, Negro, Madera oscura o Gris)"
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_DIMENSION:
            respuesta = "¿Qué dimensiones prefieres? (Pequeño, Estándar o Grande)"
        elif self.pedido_manager.estado == EstadoPedido.AGREGANDO_MAS:
            respuesta = f"{self.pedido_manager.obtener_resumen_detallado()}\n\n¿Quieres agregar otro mueble? (sí/no)"
        elif self.pedido_manager.estado == EstadoPedido.FINALIZANDO:
            respuesta = f"📦 **PEDIDO COMPLETO**\n\n{self.pedido_manager.obtener_resumen_detallado()}\n\n¿Confirmamos? (sí/no)"
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_CONTACTO:
            respuesta = "Por favor, ingresa tu email para contactarte:"
        else:
            respuesta = "¿En qué más puedo ayudarte con tu pedido de muebles?"

        self.ultima_respuesta = respuesta
        return respuesta

# --- INTERFAZ STREAMLIT ---
def inicializar_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'designbot' not in st.session_state:
        st.session_state.designbot = DesignBotLLM()

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
    chat_container = st.container(height=500)
    
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
