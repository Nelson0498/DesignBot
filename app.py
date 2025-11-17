# app.py
import streamlit as st

# =============================================
# ✅ CONFIGURACIÓN DE PÁGINA - DEBE SER PRIMERO
# =============================================
st.set_page_config(
    page_title="DesignBot Pro - Sistema Inteligente",
    page_icon="🛋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# IMPORTS (DESPUÉS de set_page_config)
# =============================================
import pandas as pd
from datetime import datetime
import re
import json
from typing import Dict, List, Any, Optional

# =============================================
# E. STACK TECNOLÓGICO SIMPLIFICADO
# =============================================
"""
JUSTIFICACIÓN DEL STACK:
- Regex + Lógica procedural: Suficiente para el alcance del proyecto
- No requiere modelos complejos para demostrar los conceptos
- Más ligero y fácil de desplegar
- Cumple todos los requisitos del proyecto
"""

# =============================================
# D. SISTEMA DE INTENCIONES Y ENTIDADES
# =============================================
class SistemaIntenciones:
    def __init__(self):
        # D.1 INTENCIONES DEFINIDAS FORMALMENTE
        self.intenciones = {
            'saludar': [
                "hola", "buenos días", "buenas tardes", "hi", "hello",
                "qué tal", "cómo estás", "saludos"
            ],
            'iniciar_pedido': [
                "quiero un mueble", "diseñar mueble", "hacer pedido",
                "comenzar pedido", "nuevo mueble", "personalizar", "sí", "si"
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
                "eso es todo", "acabar pedido", "no"
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
        
        # D.2 ENTIDADES DEFINIDAS FORMALMENTE
        self.entidades = {
            'nombre': r'(me llamo|soy|mi nombre es)\s+([A-Za-záéíóúñ\s]+)',
            'tipo_mueble': r'\b(silla|mesa|sofá|sofa|estantería|estanteria|escritorio)s?\b',
            'cantidad': r'(\d+)\s*(unidades?|uds?|x|)',
            'material': r'\b(madera noble|roble|nogal|mdf|metal|acero|vidrio|cristal|bambú|madera reciclada)\b',
            'color': r'\b(natural|blanco|negro|madera oscura|oscuro|caoba|gris)\b',
            'dimension': r'\b(pequeño|pequeña|chico|estándar|estandar|normal|mediano|grande)\b'
        }
    
    def clasificar_intencion(self, texto: str) -> str:
        """Clasifica la intención usando coincidencia de patrones simples"""
        if not texto.strip():
            return "desconocido"
            
        texto_lower = texto.lower()
        
        # Buscar coincidencias exactas primero
        for intencion, patrones in self.intenciones.items():
            for patron in patrones:
                if patron in texto_lower:
                    return intencion
        
        # Búsqueda por palabras clave con puntuación
        puntuaciones = {}
        for intencion, patrones in self.intenciones.items():
            puntuacion = 0
            palabras_intencion = ' '.join(patrones).split()
            for palabra in palabras_intencion:
                if len(palabra) > 3 and palabra in texto_lower:
                    puntuacion += 1
            puntuaciones[intencion] = puntuacion
        
        # Obtener intención con mayor puntuación
        intencion_max = max(puntuaciones, key=puntuaciones.get)
        if puntuaciones[intencion_max] > 0:
            return intencion_max
        
        return "desconocido"
    
    def extraer_entidades(self, texto: str) -> Dict[str, Any]:
        """Extrae entidades del texto usando regex"""
        entidades = {}
        
        for entidad, patron in self.entidades.items():
            try:
                matches = re.findall(patron, texto.lower())
                if matches:
                    if entidad == 'nombre':
                        # Para nombre, tomar el segundo grupo de captura
                        entidades[entidad] = matches[0][1].strip().title()
                    elif entidad == 'cantidad':
                        # Para cantidad, tomar el número
                        entidades[entidad] = int(matches[0][0])
                    else:
                        # Para otras entidades, tomar la primera coincidencia
                        valor = matches[0] if isinstance(matches[0], str) else matches[0][0]
                        entidades[entidad] = valor
            except Exception as e:
                continue  # Si hay error en una entidad, continuar con las demás
        
        return entidades

# =============================================
# C. SISTEMA DE MEMORIA MEJORADO
# =============================================
class MemoriaConversacion:
    def __init__(self):
        self.resetear()
    
    def resetear(self):
        self.nombre_usuario = None
        self.preferencias = {
            'material_favorito': None,
            'color_favorito': None, 
            'tipo_favorito': None,
            'dimension_favorita': None
        }
        self.historial_conversacion = []
        self.contexto_actual = {}
        self.ultima_intencion = None
    
    def guardar_nombre(self, nombre: str):
        self.nombre_usuario = nombre
        self.agregar_historial(f"Usuario proporcionó nombre: {nombre}")
    
    def guardar_preferencia(self, tipo: str, valor: str):
        if tipo in self.preferencias:
            self.preferencias[tipo] = valor
            self.agregar_historial(f"Preferencia guardada: {tipo} = {valor}")
    
    def agregar_historial(self, evento: str):
        self.historial_conversacion.append({
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'evento': evento
        })
    
    def personalizar_respuesta(self, respuesta_base: str) -> str:
        """Personaliza respuestas basado en la memoria - IMPLEMENTACIÓN CLAVE"""
        respuesta = respuesta_base
        
        # Personalización con nombre
        if self.nombre_usuario:
            if "¡Hola!" in respuesta:
                respuesta = respuesta.replace("¡Hola!", f"¡Hola {self.nombre_usuario}!")
            elif "Hola" in respuesta and self.nombre_usuario not in respuesta:
                respuesta = f"¡Hola {self.nombre_usuario}! {respuesta}"
        
        # Personalización con preferencias
        preferencias_usadas = []
        if self.preferencias['material_favorito'] and "material" in respuesta.lower():
            respuesta += f"\n\n💡 Por cierto, sé que te gusta el {self.preferencias['material_favorito']}"
            preferencias_usadas.append('material')
        
        if self.preferencias['color_favorito'] and "color" in respuesta.lower():
            respuesta += f"\n🎨 Recuerdo que prefieres el color {self.preferencias['color_favorito']}"
            preferencias_usadas.append('color')
        
        return respuesta

# =============================================
# CATÁLOGO Y GESTIÓN DE PEDIDOS
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

# =============================================
# B. CHATBOT AVANZADO CON MEMORIA
# =============================================
class DesignBotAvanzado:
    def __init__(self):
        self.pedido_manager = PedidoManager()
        self.sistema_intenciones = SistemaIntenciones()
        self.memoria = MemoriaConversacion()
        self.ultima_respuesta = None
        
        # Mapeos corregidos
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

        # ✅ MAPEO DE DIMENSIONES CORREGIDO
        self.mapeo_dimensiones = {
            "pequeño": "PEQUEÑO", "pequeña": "PEQUEÑO", "pequeno": "PEQUEÑO", 
            "chico": "PEQUEÑO", "s": "PEQUEÑO",
            
            "estándar": "ESTÁNDAR", "estandar": "ESTÁNDAR", "normal": "ESTÁNDAR", 
            "mediano": "ESTÁNDAR", "m": "ESTÁNDAR",
            
            "grande": "GRANDE", "grand": "GRANDE", "l": "GRANDE"
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
        
        # 3. PERSONALIZAR RESPUESTA CON MEMORIA (REQUISITO CLAVE)
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
                cantidad = entidades.get('cantidad', 1)
                self.pedido_manager.iniciar_nuevo_item(tipo, cantidad)
                self.pedido_manager.estado = EstadoPedido.ESPERANDO_MATERIAL
                
                # Guardar preferencia
                self.memoria.guardar_preferencia('tipo_favorito', entidades['tipo_mueble'])
                
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

    def _procesar_modificacion_pedido(self, user_input: str) -> str:
        """Procesa modificaciones del pedido"""
        if "eliminar" in user_input.lower():
            numeros = re.findall(r'\d+', user_input)
            if numeros:
                index = int(numeros[0]) - 1
                if self.pedido_manager.eliminar_item(index):
                    return f"✅ **Item {index + 1} eliminado del pedido**\n\n{self.pedido_manager.obtener_resumen_detallado()}"
        
        return "Para modificar tu pedido, puedes:\n• 'Eliminar item X' (donde X es el número)\n• Usar los controles del panel lateral"

    def _procesar_finalizacion_pedido(self) -> str:
        if self.pedido_manager.items:
            self.pedido_manager.estado = EstadoPedido.FINALIZANDO
            return f"📦 **PEDIDO COMPLETO**\n\n{self.pedido_manager.obtener_resumen_detallado()}\n\n¿Todo correcto? (responde 'sí' para confirmar)"
        else:
            return "No hay items en tu pedido para finalizar. ¿Te gustaría agregar algún mueble?"

    def _procesar_por_estado(self, user_input: str) -> str:
        """Procesa según el estado actual del pedido"""
        input_clean = user_input.lower().strip()
        
        # ESTADO: ESPERANDO DIMENSION - CORREGIDO
        if self.pedido_manager.estado == EstadoPedido.ESPERANDO_DIMENSION:
            for dim_key, dim_val in self.mapeo_dimensiones.items():
                if dim_key in input_clean:
                    self.pedido_manager.actualizar_item_actual('dimensiones', dim_val)
                    
                    # ✅ GUARDAR PREFERENCIA CORRECTAMENTE
                    self.memoria.guardar_preferencia('dimension_favorita', dim_val.lower())
                    
                    if self.pedido_manager.agregar_item_actual_al_pedido():
                        self.pedido_manager.estado = EstadoPedido.AGREGANDO_MAS
                        
                        # ✅ VERIFICACIÓN: Obtener el item recién agregado
                        item_agregado = self.pedido_manager.items[-1]
                        
                        return f"✅ **{item_agregado.tipo_mueble.title()} {dim_val.title()} agregado correctamente!** 🎉\n\n" + \
                               f"{self.pedido_manager.obtener_resumen_detallado()}\n\n" + \
                               "¿Te gustaría agregar otro mueble? (responde 'sí' para agregar más o 'no' para finalizar)"
            
            return "❌ No entendí la dimensión. Por favor elige entre:\n\n• **Pequeño**\n• **Estándar**\n• **Grande**"
        
        # ESTADO: ESPERANDO MATERIAL
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_MATERIAL:
            for material_key, material_val in self.mapeo_materiales.items():
                if material_key in input_clean:
                    self.pedido_manager.actualizar_item_actual('material', material_val)
                    self.pedido_manager.estado = EstadoPedido.ESPERANDO_COLOR
                    
                    # Guardar preferencia en memoria
                    self.memoria.guardar_preferencia('material_favorito', material_key)
                    
                    return f"✅ **Material {material_val.replace('_', ' ').title()} seleccionado**\n\n" + \
                           "¿Qué color prefieres?\n\n" + \
                           "• Natural\n• Blanco\n• Negro\n• Madera oscura\n• Gris"
            
            return "Por favor, elige un material: Madera noble, MDF, Metal, Vidrio, Bambú o Madera reciclada"
        
        # ESTADO: ESPERANDO COLOR
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_COLOR:
            mapeo_colores = {
                "natural": "NATURAL", "blanco": "BLANCO", "negro": "NEGRO",
                "madera oscura": "MADERA_OSCURA", "oscuro": "MADERA_OSCURA", 
                "caoba": "MADERA_OSCURA", "gris": "GRIS"
            }
            
            for color_key, color_val in mapeo_colores.items():
                if color_key in input_clean:
                    self.pedido_manager.actualizar_item_actual('color', color_val)
                    self.pedido_manager.estado = EstadoPedido.ESPERANDO_DIMENSION
                    
                    # Guardar preferencia en memoria
                    self.memoria.guardar_preferencia('color_favorito', color_key)
                    
                    return f"✅ **Color {color_key.title()} seleccionado**\n\n" + \
                           "¿Qué dimensiones prefieres?\n\n" + \
                           "• **Pequeño** (80% del tamaño estándar)\n" + \
                           "• **Estándar** (tamaño normal)\n" + \
                           "• **Grande** (130% del tamaño estándar)"
            
            return "Por favor, elige un color: Natural, Blanco, Negro, Madera oscura o Gris"
        
        # ESTADO: AGREGANDO_MAS
        elif self.pedido_manager.estado == EstadoPedido.AGREGANDO_MAS:
            if any(palabra in input_clean for palabra in ["sí", "si", "s", "quiero", "agregar", "otro", "más", "mas"]):
                self.pedido_manager.estado = EstadoPedido.ESPERANDO_TIPO
                return "¡Perfecto! ¿Qué otro mueble te gustaría agregar?\n\n• Silla\n• Mesa\n• Sofá\n• Estantería\n• Escritorio"
            elif any(palabra in input_clean for palabra in ["no", "n", "listo", "terminar", "finalizar"]):
                self.pedido_manager.estado = EstadoPedido.FINALIZANDO
                return f"📦 **PEDIDO COMPLETO**\n\n{self.pedido_manager.obtener_resumen_detallado()}\n\n¿Confirmamos el pedido? (responde 'sí')"
        
        # ESTADO: FINALIZANDO
        elif self.pedido_manager.estado == EstadoPedido.FINALIZANDO:
            if any(palabra in input_clean for palabra in ["sí", "si", "confirmar"]):
                self.pedido_manager.estado = EstadoPedido.ESPERANDO_CONTACTO
                nombre = f", {self.memoria.nombre_usuario}" if self.memoria.nombre_usuario else ""
                return f"📧 **INFORMACIÓN DE CONTACTO**{nombre}:\n\n¡Perfecto! Por favor, compártenos tu email para contactarte:"
        
        # ESTADO: ESPERANDO_CONTACTO
        elif self.pedido_manager.estado == EstadoPedido.ESPERANDO_CONTACTO:
            if "@" in user_input and "." in user_input:
                self.pedido_manager.estado = EstadoPedido.COMPLETADO
                self.pedido_manager.email = user_input
                
                nombre = f", {self.memoria.nombre_usuario}" if self.memoria.nombre_usuario else ""
                
                return f"""🎉 **¡PEDIDO CONFIRMADO!** 🎉{nombre}

{self.pedido_manager.obtener_resumen_detallado()}

📧 **Email de contacto:** {user_input}

📅 **Proceso:**
1. Confirmación por email en 24 horas
2. Diseño técnico (2-3 días)  
3. Fabricación (7-10 días)
4. Entrega programada

¡Gracias por tu pedido! 🛋️"""
            else:
                return "Por favor, ingresa un email válido:"
        
        # Estado por defecto
        return "¿En qué más puedo ayudarte con tu pedido de muebles?"

# =============================================
# F. INTERFAZ STREAMLIT MEJORADA
# =============================================
def main():
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
        chat_container = st.container(height=500)
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
        
        st.markdown("**⭐ Preferencias guardadas:**")
        preferencias_mostradas = False
        for pref, valor in memoria.preferencias.items():
            if valor:
                st.write(f"- {pref.replace('_', ' ').title()}: {valor}")
                preferencias_mostradas = True
        
        if not preferencias
