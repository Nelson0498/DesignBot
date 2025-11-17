# app_completa.py
import streamlit as st
import pandas as pd
from datetime import datetime
import re
import json
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import requests

# =============================================
# E. STACK TECNOLÓGICO JUSTIFICADO
# =============================================
"""
JUSTIFICACIÓN DEL STACK:

1. spaCy - Para NLP básico: tokenización, POS tagging, NER
2. Scikit-learn - Para similitud de coseno y TF-IDF
3. Streamlit - Para interfaz web rápida
4. Regex - Para patrones específicos
5. No usamos LLMs pesados por: costo, latencia, complejidad
"""

# =============================================
# D. SISTEMA DE INTENCIONES Y ENTIDADES FORMAL
# =============================================
class SistemaIntenciones:
    def __init__(self):
        # D.1 INTENCIONES DEFINIDAS
        self.intenciones = {
            'saludar': [
                "hola", "buenos días", "buenas tardes", "hi", "hello",
                "qué tal", "cómo estás", "saludos"
            ],
            'iniciar_pedido': [
                "quiero un mueble", "diseñar mueble", "hacer pedido",
                "comenzar pedido", "nuevo mueble", "personalizar"
            ],
            'consultar_pedido': [
                "ver pedido", "qué tengo", "resumen", "carrito",
                "mostrar pedido", "qué pedí"
            ],
            'modificar_pedido': [
                "eliminar", "quitar", "modificar", "cambiar",
                "editar pedido", "borrar item"
            ],
            'finalizar_pedido': [
                "terminar", "finalizar", "completar", "listo",
                "eso es todo", "acabar pedido"
            ],
            'preguntar_precio': [
                "cuánto cuesta", "precio", "coste", "valor",
                "qué precio", "cuál es el precio"
            ],
            'despedir': [
                "adiós", "chao", "hasta luego", "nos vemos",
                "gracias", "bye"
            ]
        }
        
        # D.2 ENTIDADES DEFINIDAS
        self.entidades = {
            'nombre': r'(me llamo|soy|mi nombre es)\s+([A-Za-záéíóúñ]+)',
            'tipo_mueble': r'(silla|mesa|sofá|sofa|estantería|estanteria|escritorio)',
            'cantidad': r'(\d+)\s*(unidades?|uds?|x)',
            'material': r'(madera noble|roble|nogal|mdf|metal|acero|vidrio|cristal|bambú|madera reciclada)',
            'color': r'(natural|blanco|negro|madera oscura|oscuro|caoba|gris)',
            'dimension': r'(pequeño|pequeña|chico|estándar|normal|mediano|grande)'
        }
        
        # Entrenar clasificador de intenciones
        self.entrenar_clasificador()
    
    def entrenar_clasificador(self):
        """Entrena un clasificador simple basado en TF-IDF"""
        textos = []
        labels = []
        
        for intencion, ejemplos in self.intenciones.items():
            for ejemplo in ejemplos:
                textos.append(ejemplo)
                labels.append(intencion)
        
        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(textos)
        self.X_train = X
        self.labels_train = labels
    
    def clasificar_intencion(self, texto: str) -> str:
        """Clasifica la intención del texto usando similitud de coseno"""
        if not texto.strip():
            return "desconocido"
            
        # Vectorizar texto de entrada
        X_test = self.vectorizer.transform([texto.lower()])
        
        # Calcular similitud con ejemplos de entrenamiento
        similitudes = cosine_similarity(X_test, self.X_train)
        
        # Obtener intención más similar
        idx_max = np.argmax(similitudes)
        max_sim = similitudes[0, idx_max]
        
        # Umbral de confianza
        if max_sim > 0.3:
            return self.labels_train[idx_max]
        else:
            return "desconocido"
    
    def extraer_entidades(self, texto: str) -> Dict[str, Any]:
        """Extrae entidades del texto usando regex"""
        entidades = {}
        
        for entidad, patron in self.entidades.items():
            matches = re.findall(patron, texto.lower())
            if matches:
                if entidad == 'nombre':
                    entidades[entidad] = matches[0][1]  # Capturar el nombre
                else:
                    entidades[entidad] = matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return entidades

# =============================================
# C. SISTEMA DE MEMORIA
# =============================================
class MemoriaConversacion:
    def __init__(self):
        self.resetear()
    
    def resetear(self):
        self.nombre_usuario = None
        self.preferencias = {
            'material_favorito': None,
            'color_favorito': None, 
            'tipo_favorito': None
        }
        self.historial_pedidos = []
        self.contexto_actual = {}
        self.ultima_intencion = None
    
    def guardar_nombre(self, nombre: str):
        self.nombre_usuario = nombre.title()
    
    def guardar_preferencia(self, tipo: str, valor: str):
        if tipo in self.preferencias:
            self.preferencias[tipo] = valor
    
    def guardar_contexto(self, contexto: Dict):
        self.contexto_actual.update(contexto)
    
    def personalizar_respuesta(self, respuesta_base: str) -> str:
        """Personaliza respuestas basado en la memoria"""
        respuesta = respuesta_base
        
        if self.nombre_usuario:
            # Insertar nombre en respuestas
            if "¡Hola!" in respuesta:
                respuesta = respuesta.replace("¡Hola!", f"¡Hola {self.nombre_usuario}!")
            elif "Hola" in respuesta and not self.nombre_usuario in respuesta:
                respuesta = f"¡Hola {self.nombre_usuario}! {respuesta}"
        
        # Personalizar basado en preferencias
        if self.preferencias['material_favorito']:
            if "material" in respuesta.lower():
                respuesta += f"\n\nPor cierto, sé que te gusta el {self.preferencias['material_favorito']} 😊"
        
        return respuesta

# =============================================
# CATÁLOGO Y GESTIÓN DE PEDIDOS (Existente)
# =============================================
class Configuracion:
    CATALOGO = {
        "tipos_mueble": {
            "SILLA": {"precio_base": 150.00, "descripcion": "Silla ergonómica personalizada"},
            "MESA": {"precio_base": 300.00, "descripcion": "Mesa de centro o comedor"},
            "SOFÁ": {"precio_base": 800.00, "descripcion": "Sofá de 3 plazas personalizado"},
            "ESTANTERÍA": {"precio_base": 250.00, "descripcion": "Estantería modular"},
            "ESCRITORIO": {"precio_base": 400.00, "descripcion": "Escritorio de trabajo"}
        },
        # ... (resto del catálogo igual)
    }

class EstadoPedido:
    INICIO = "inicio"
    ESPERANDO_TIPO = "esperando_tipo"
    ESPERANDO_MATERIAL = "esperando_material"
    ESPERANDO_COLOR = "esperando_color"
    ESPERANDO_DIMENSION = "esperando_dimension"
    AGREGANDO_MAS = "agregando_mas"
    FINALIZANDO = "finalizando"
    ESPERANDO_CONTACTO = "esperando_contacto"
    COMPLETADO = "completado"

class PedidoManager:
    # ... (implementación igual que antes)
    pass

class ItemPedido:
    # ... (implementación igual que antes)  
    pass

# =============================================
# B. CHATBOT CON MEMORIA E INTELIGENCIA
# =============================================
class DesignBotAvanzado:
    def __init__(self):
        self.pedido_manager = PedidoManager()
        self.sistema_intenciones = SistemaIntenciones()
        self.memoria = MemoriaConversacion()
        self.ultima_respuesta = None
        
        # Mapeos para conversión
        self.mapeo_tipos = {
            "silla": "SILLA", "mesa": "MESA", "sofá": "SOFÁ", "sofa": "SOFÁ",
            "estantería": "ESTANTERÍA", "estanteria": "ESTANTERÍA", "escritorio": "ESCRITORIO"
        }
        
        self.mapeo_materiales = {
            "madera noble": "MADERA_NOBLE", "roble": "MADERA_NOBLE", "nogal": "MADERA_NOBLE",
            "mdf": "MADERA_MDF", "metal": "METAL", "acero": "METAL",
            "vidrio": "VIDRIO", "cristal": "VIDRIO", "bambú": "BAMBÚ",
            "madera reciclada": "MADERA_RECICLADA"
        }

    def procesar_mensaje(self, user_input: str) -> str:
        """Procesa el mensaje usando el sistema de intenciones y memoria"""
        
        # 1. ANALIZAR INTENCIÓN Y ENTIDADES
        intencion = self.sistema_intenciones.clasificar_intencion(user_input)
        entidades = self.sistema_intenciones.extraer_entidades(user_input)
        
        # Guardar en memoria
        self.memoria.ultima_intencion = intencion
        if 'nombre' in entidades:
            self.memoria.guardar_nombre(entidades['nombre'])
        
        # 2. PROCESAR SEGÚN INTENCIÓN
        if intencion == "saludar":
            respuesta = self._procesar_saludo(entidades)
        
        elif intencion == "iniciar_pedido":
            respuesta = self._procesar_inicio_pedido(user_input, entidades)
        
        elif intencion == "consultar_pedido":
            respuesta = self._procesar_consulta_pedido()
        
        elif intencion == "modificar_pedido":
            respuesta = self._procesar_modificacion_pedido(user_input)
        
        elif intencion == "finalizar_pedido":
            respuesta = self._procesar_finalizacion_pedido()
        
        elif intencion == "preguntar_precio":
            respuesta = self._procesar_consulta_precio(user_input, entidades)
        
        elif intencion == "despedir":
            respuesta = self._procesar_despedida()
        
        else:
            respuesta = self._procesar_por_estado(user_input)
        
        # 3. PERSONALIZAR RESPUESTA CON MEMORIA
        respuesta_personalizada = self.memoria.personalizar_respuesta(respuesta)
        self.ultima_respuesta = respuesta_personalizada
        
        return respuesta_personalizada

    def _procesar_saludo(self, entidades: Dict) -> str:
        if self.memoria.nombre_usuario:
            return f"¡Hola {self.memoria.nombre_usuario}! 😊 ¿En qué puedo ayudarte hoy con tus muebles personalizados?"
        else:
            return "¡Hola! 👋 Soy DesignBot, tu asistente para muebles personalizados. ¿Te gustaría diseñar algún mueble?"

    def _procesar_inicio_pedido(self, user_input: str, entidades: Dict) -> str:
        if self.pedido_manager.estado == EstadoPedido.INICIO:
            self.pedido_manager.estado = EstadoPedido.ESPERANDO_TIPO
            
        # Extraer entidades para pedido rápido
        if 'tipo_mueble' in entidades:
            tipo = self.mapeo_tipos.get(entidades['tipo_mueble'])
            if tipo:
                cantidad = int(entidades.get('cantidad', 1)) if 'cantidad' in entidades else 1
                self.pedido_manager.iniciar_nuevo_item(tipo, cantidad)
                self.pedido_manager.estado = EstadoPedido.ESPERANDO_MATERIAL
                return f"✅ **{tipo.title()} seleccionado**\n\n¿Qué material prefieres?\n\n• Madera noble\n• MDF\n• Metal\n• Vidrio\n• Bambú\n• Madera reciclada"
        
        return "¡Excelente! 🛋️ ¿Qué tipo de mueble te gustaría diseñar?\n\n• Silla\n• Mesa\n• Sofá\n• Estantería\n• Escritorio"

    def _procesar_consulta_pedido(self) -> str:
        if self.pedido_manager.items:
            return f"📋 **TU PEDIDO ACTUAL:**\n\n{self.pedido_manager.obtener_resumen_detallado()}\n\n¿Quieres agregar algo más o finalizar?"
        else:
            return "🛒 Tu pedido está vacío. ¿Te gustaría agregar algún mueble?"

    def _procesar_consulta_precio(self, user_input: str, entidades: Dict) -> str:
        if 'tipo_mueble' in entidades:
            tipo = self.mapeo_tipos.get(entidades['tipo_mueble'])
            if tipo and tipo in Configuracion.CATALOGO["tipos_mueble"]:
                precio = Configuracion.CATALOGO["tipos_mueble"][tipo]["precio_base"]
                return f"El precio base para una {tipo.lower()} es ${precio:.2f}. El precio final depende del material, color y dimensiones que elijas."
        
        return "Te puedo ayudar con precios. Los precios base son:\n• Silla: $150\n• Mesa: $300\n• Sofá: $800\n• Estantería: $250\n• Escritorio: $400\n\n¿Te interesa algún tipo en particular?"

    def _procesar_despedida(self) -> str:
        nombre = f", {self.memoria.nombre_usuario}" if self.memoria.nombre_usuario else ""
        return f"¡Ha sido un gusto ayudarte{nombre}! 😊 Espero verte pronto para tu próximo diseño de muebles. ¡Hasta luego!"

    # ... (otros métodos de procesamiento)

# =============================================
# F. INTERFAZ STREAMLIT (MEJORADA)
# =============================================
def main():
    st.set_page_config(
        page_title="DesignBot Pro - Sistema Inteligente",
        page_icon="🛋️",
        layout="wide"
    )
    
    # Inicialización
    if 'designbot' not in st.session_state:
        st.session_state.designbot = DesignBotAvanzado()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Header con información del sistema
    st.title("🛋️ DesignBot Pro - Sistema Inteligente")
    st.markdown("**Chatbot con Memoria, Intenciones y Entidades**")
    st.markdown("---")
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Conversación Inteligente")
        
        # Mostrar historial de chat
        chat_container = st.container(height=400)
        with chat_container:
            for mensaje in st.session_state.chat_history:
                with st.chat_message(mensaje["role"]):
                    st.markdown(mensaje["content"])
                    if mensaje.get("timestamp"):
                        st.caption(mensaje["timestamp"])
        
        # Input de usuario
        user_input = st.chat_input("Escribe tu mensaje aquí...")
        if user_input:
            # Procesar mensaje
            respuesta = st.session_state.designbot.procesar_mensaje(user_input)
            
            # Guardar en historial
            st.session_state.chat_history.extend([
                {
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                },
                {
                    "role": "assistant", 
                    "content": respuesta,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
            ])
            st.rerun()
    
    with col2:
        st.subheader("🧠 Sistema de Memoria")
        
        # Mostrar información de memoria
        memoria = st.session_state.designbot.memoria
        if memoria.nombre_usuario:
            st.success(f"**👤 Nombre:** {memoria.nombre_usuario}")
        else:
            st.info("**👤 Nombre:** No identificado")
        
        st.markdown("**⭐ Preferencias:**")
        for pref, valor in memoria.preferencias.items():
            if valor:
                st.write(f"- {pref.replace('_', ' ').title()}: {valor}")
        
        st.markdown("---")
        st.subheader("🔍 Análisis de Mensajes")
        
        # Mostrar análisis de último mensaje
        if st.session_state.chat_history:
            ultimo_msg = st.session_state.chat_history[-2] if len(st.session_state.chat_history) >= 2 else None
            if ultimo_msg and ultimo_msg["role"] == "user":
                intencion = st.session_state.designbot.sistema_intenciones.clasificar_intencion(ultimo_msg["content"])
                entidades = st.session_state.designbot.sistema_intenciones.extraer_entidades(ultimo_msg["content"])
                
                st.write(f"**Intención:** `{intencion}`")
                if entidades:
                    st.write("**Entidades detectadas:**")
                    for ent, val in entidades.items():
                        st.write(f"- `{ent}`: `{val}`")

if __name__ == "__main__":
    main()
