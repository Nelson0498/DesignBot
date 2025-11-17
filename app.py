# app.py
import streamlit as st

# ✅ DEBE SER EL PRIMER COMANDO
st.set_page_config(
    page_title="DesignBot Pro - Muebles Personalizados",
    page_icon="🛋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import json

# =============================================
# E. STACK TECNOLÓGICO JUSTIFICADO
# =============================================
"""
JUSTIFICACIÓN TECNOLÓGICA:
- Streamlit: Para interfaz web interactiva
- Regex: Para procesamiento básico de lenguaje natural
- Sistema de estados: Para manejo de conversación
- No se requieren modelos complejos para el alcance del proyecto
"""

# =============================================
# D. SISTEMA DE INTENCIONES Y ENTIDADES FORMAL
# =============================================
class SistemaIntenciones:
    """Sistema formal de clasificación de intenciones y extracción de entidades"""
    
    def __init__(self):
        # D.1 INTENCIONES DEFINIDAS FORMALMENTE (mínimo 3)
        self.intenciones = {
            'saludar': ["hola", "hi", "hello", "buenos días", "buenas"],
            'iniciar_pedido': ["sí", "si", "quiero", "diseñar", "mueble", "personalizar"],
            'consultar_pedido': ["resumen", "pedido", "carrito", "qué tengo"],
            'modificar_pedido': ["modificar", "cambiar", "eliminar", "quitar"],
            'finalizar_pedido': ["no", "terminar", "finalizar", "listo"]
        }
        
        # D.2 ENTIDADES DEFINIDAS FORMALMENTE (mínimo 2 tipos)
        self.entidades = {
            'nombre': r'(me llamo|soy|mi nombre es)\s+([A-Za-záéíóúñ\s]+)',
            'tipo_mueble': r'\b(silla|mesa|sofá|sofa|estantería|estanteria|escritorio)\b',
            'cantidad': r'(\d+)\s*(unidades?|uds?|x)',
            'material': r'\b(madera noble|roble|nogal|mdf|metal|acero|vidrio|cristal|bambú|madera reciclada)\b',
            'color': r'\b(natural|blanco|negro|madera oscura|oscuro|caoba|gris)\b',
            'dimension': r'\b(pequeño|pequeña|chico|estándar|estandar|normal|mediano|grande)\b'
        }
    
    def clasificar_intencion(self, texto: str) -> str:
        """Clasifica formalmente la intención del usuario"""
        texto_lower = texto.lower()
        
        for intencion, patrones in self.intenciones.items():
            for patron in patrones:
                if patron in texto_lower:
                    return intencion
        return "desconocido"
    
    def extraer_entidades(self, texto: str) -> Dict[str, Any]:
        """Extrae entidades formalmente del texto"""
        entidades = {}
        
        for entidad, patron in self.entidades.items():
            matches = re.findall(patron, texto.lower())
            if matches:
                if entidad == 'nombre':
                    entidades[entidad] = matches[0][1].strip().title()
                elif entidad == 'cantidad':
                    entidades[entidad] = int(matches[0][0])
                else:
                    valor = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    entidades[entidad] = valor
        
        return entidades

# =============================================
# C. SISTEMA DE MEMORIA (REQUISITO CLAVE)
# =============================================
class MemoriaConversacion:
    """Sistema de memoria que recuerda información clave entre interacciones"""
    
    def __init__(self):
        self.resetear()
    
    def resetear(self):
        self.nombre_usuario = None
        # Memoria de preferencias del usuario
        self.preferencias = {
            'material_favorito': None,
            'color_favorito': None,
            'dimension_favorita': None,
            'tipo_favorito': None
        }
        self.historial_interacciones = []
    
    def guardar_nombre(self, nombre: str):
        """Guarda el nombre del usuario en memoria"""
        self.nombre_usuario = nombre
        self._registrar_evento(f"Usuario proporcionó nombre: {nombre}")
    
    def guardar_preferencia(self, tipo: str, valor: str):
        """Guarda preferencias del usuario en memoria"""
        if tipo in self.preferencias:
            self.preferencias[tipo] = valor
            self._registrar_evento(f"Preferencia guardada: {tipo} = {valor}")
    
    def _registrar_evento(self, evento: str):
        """Registra evento en el historial"""
        self.historial_interacciones.append({
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'evento': evento
        })
    
    def personalizar_respuesta(self, respuesta_base: str) -> str:
        """Personaliza respuestas basado en la memoria del usuario"""
        respuesta = respuesta_base
        
        # Personalizar con nombre si está disponible
        if self.nombre_usuario:
            if "¡Hola!" in respuesta:
                respuesta = respuesta.replace("¡Hola!", f"¡Hola {self.nombre_usuario}!")
            elif "Hola" in respuesta and self.nombre_usuario not in respuesta:
                respuesta = f"¡Hola {self.nombre_usuario}! {respuesta}"
        
        # Personalizar con preferencias recordadas
        if self.preferencias['material_favorito'] and "material" in respuesta.lower():
            respuesta += f"\n\n💡 Por cierto, recuerdo que te gusta el {self.preferencias['material_favorito']}"
        
        return respuesta

# --- CONFIGURACIÓN (MANTENIENDO TU ESTRUCTURA) ---
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

# =============================================
# B. CHATBOT MEJORADO CON TODOS LOS REQUISITOS
# =============================================
class DesignBotLLM:
    def __init__(self):
        self.pedido_manager = PedidoManager()
        self.sistema_intenciones = SistemaIntenciones()  # ✅ NUEVO: Sistema formal
        self.memoria = MemoriaConversacion()  # ✅ NUEVO: Sistema de memoria
        self.ultima_respuesta = None
        
        # ✅ CORREGIDO: Mapeo de dimensiones sin conflictos
        self.mapeo_dimensiones_corregido = {
            "pequeño": "PEQUEÑO", "pequeña": "PEQUEÑO", "pequeno": "PEQUEÑO", "chico": "PEQUEÑO",
            "estándar": "ESTÁNDAR", "estandar": "ESTÁNDAR", "normal": "ESTÁNDAR", "mediano": "ESTÁNDAR",
            "grande": "GRANDE", "grand": "GRANDE"
        }

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

    def procesar_mensaje(self, user_input: str) -> str:
        # ✅ NUEVO: Usar sistema formal de intenciones
        intencion = self.sistema_intenciones.clasificar_intencion(user_input)
        entidades = self.sistema_intenciones.extraer_entidades(user_input)
        
        # ✅ NUEVO: Actualizar memoria con entidades detectadas
        if 'nombre' in entidades:
            self.memoria.guardar_nombre(entidades['nombre'])
            self.pedido_manager.nombre_cliente = entidades['nombre']
        
        input_clean = user_input.lower().strip()
        
        # Evitar procesar si es la misma respuesta
        if self.ultima_respuesta and user_input.strip() == "":
            return self.ultima_respuesta

        # 1. SALUDOS (con memoria)
        if intencion == "saludar":
            respuesta = self.memoria.personalizar_respuesta(
                "¡Hola! 👋 Soy DesignBot, tu asistente para diseño de muebles personalizados. ¿Te gustaría diseñar algún mueble?"
            )
            self.ultima_respuesta = respuesta
            return respuesta

        # 2. INICIAR PEDIDO
        if (intencion == "iniciar_pedido" and self.pedido_manager.estado == EstadoPedido.INICIO):
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

        # 4. DETECCIÓN DE MATERIAL (con memoria)
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
                # ✅ NUEVO: Guardar en memoria
                self.memoria.guardar_preferencia('material_favorito', material_key)
                respuesta = f"✅ **Material {material_val.replace('_', ' ').title()} seleccionado**\n\n" + \
                           "¿Qué color prefieres?\n\n" + \
                           "• Natural\n• Blanco\n• Negro\n• Madera oscura\n• Gris"
                self.ultima_respuesta = respuesta
                return respuesta

        # 5. DETECCIÓN DE COLOR (con memoria)
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
                # ✅ NUEVO: Guardar en memoria
                self.memoria.guardar_preferencia('color_favorito', color_key)
                respuesta = f"✅ **Color {color_key.title()} seleccionado**\n\n" + \
                           "¿Qué dimensiones prefieres?\n\n" + \
                           "• Pequeño\n• Estándar\n• Grande"
                self.ultima_respuesta = respuesta
                return respuesta

        # 6. ✅ CORREGIDO: DETECCIÓN DE DIMENSIONES (sin conflictos)
        for dim_key, dim_val in self.mapeo_dimensiones_corregido.items():
            if dim_key in input_clean and self.pedido_manager.estado == EstadoPedido.ESPERANDO_DIMENSION:
                self.pedido_manager.actualizar_item_actual('dimensiones', dim_val)
                # ✅ NUEVO: Guardar en memoria
                self.memoria.guardar_preferencia('dimension_favorita', dim_key)
                if self.pedido_manager.agregar_item_actual_al_pedido():
                    self.pedido_manager.estado = EstadoPedido.AGREGANDO_MAS
                    # ✅ CORREGIDO: Mostrar la dimensión correcta
                    respuesta = f"✅ **{dim_val.title()} agregado al pedido!** 🎉\n\n" + \
                               f"{self.pedido_manager.obtener_resumen_detallado()}\n\n" + \
                               "¿Te gustaría agregar otro mueble? (responde 'sí' para agregar más o 'no' para finalizar)"
                    self.ultima_respuesta = respuesta
                    return respuesta

        # 7. MANEJO DE "¿QUIERES AGREGAR MÁS?"
        if self.pedido_manager.estado == EstadoPedido.AGREGANDO_MAS:
            if intencion == "iniciar_pedido":  # "sí" para agregar más
                self.pedido_manager.estado = EstadoPedido.ESPERANDO_TIPO
                respuesta = "¡Perfecto! ¿Qué otro mueble te gustaría agregar?\n\n" + \
                           "• Silla\n• Mesa\n• Sofá\n• Estantería\n• Escritorio"
                self.ultima_respuesta = respuesta
                return respuesta
            elif intencion == "finalizar_pedido":  # "no" para finalizar
                self.pedido_manager.estado = EstadoPedido.FINALIZANDO
                respuesta = f"📦 **PEDIDO COMPLETO**\n\n{self.pedido_manager.obtener_resumen_detallado()}\n\n" + \
                           "¿Todo correcto? (responde 'sí' para confirmar o 'modificar' para hacer cambios)"
                self.ultima_respuesta = respuesta
                return respuesta

        # 8. CONSULTA DE RESUMEN
        if intencion == "consultar_pedido":
            if self.pedido_manager.items:
                respuesta = f"📋 **TU PEDIDO ACTUAL:**\n\n{self.pedido_manager.obtener_resumen_detallado()}\n\n" + \
                           "¿Quieres agregar algo más o finalizar?"
                self.ultima_respuesta = respuesta
                return respuesta
            else:
                respuesta = "🛒 Tu pedido está vacío. ¿Te gustaría agregar algún mueble?"
                self.ultima_respuesta = respuesta
                return respuesta

        # 9. MODIFICACIONES
        if intencion == "modificar_pedido":
            if "eliminar" in input_clean:
                numeros = re.findall(r'\d+', input_clean)
                if numeros:
                    index = int(numeros[0]) - 1
                    if self.pedido_manager.eliminar_item(index):
                        return f"✅ **Item {index + 1} eliminado del pedido**\n\n{self.pedido_manager.obtener_resumen_detallado()}"

        # ... (resto del código de estados se mantiene igual)

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

        # ✅ NUEVO: Aplicar personalización de memoria a todas las respuestas
        respuesta_personalizada = self.memoria.personalizar_respuesta(respuesta)
        self.ultima_respuesta = respuesta_personalizada
        return respuesta_personalizada

# --- INTERFAZ STREAMLIT (MEJORADA CON INFO DE MEMORIA) ---
def inicializar_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'designbot' not in st.session_state:
        st.session_state.designbot = DesignBotLLM()

def crear_sidebar():
    with st.sidebar:
        st.header("🎯 Panel de Control")
        
        pedido_manager = st.session_state.designbot.pedido_manager
        st.metric("📦 Items en pedido", len(pedido_manager.items))
        st.metric("💰 Total", f"${pedido_manager.calcular_total_pedido():.2f}")
        
        # ✅ NUEVO: Mostrar información de memoria
        st.markdown("---")
        st.subheader("🧠 Memoria del Sistema")
        memoria = st.session_state.designbot.memoria
        if memoria.nombre_usuario:
            st.success(f"**👤 Nombre:** {memoria.nombre_usuario}")
        
        st.markdown("**⭐ Preferencias:**")
        for pref, valor in memoria.preferencias.items():
            if valor:
                st.write(f"- {pref.replace('_', ' ').title()}: {valor}")
        
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
    # ✅ CORREGIDO: Sin parámetro height que causa error
    chat_container = st.container()
    with chat_container:
        for mensaje in st.session_state.chat_history:
            with st.chat_message(mensaje["role"]):
                st.markdown(mensaje["content"])
                if mensaje.get("timestamp"):
                    st.caption(mensaje["timestamp"])

def procesar_mensaje_usuario(user_input: str):
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    respuesta = st.session_state.designbot.procesar_mensaje(user_input)
    
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": respuesta,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    st.rerun()

def main():
    # Inicialización
    inicializar_session_state()
    
    # Header principal
    st.title("🛋️ DesignBot Pro")
    st.markdown("**Sistema inteligente con memoria e intenciones**")
    st.markdown("---")
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mostrar_chat()
    
    with col2:
        crear_sidebar()
        
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

    # ✅ CORREGIDO: st.chat_input() FUERA de las columnas
    user_input = st.chat_input("Escribe tu pedido aquí...")
    if user_input:
        procesar_mensaje_usuario(user_input)

if __name__ == "__main__":
    main()
