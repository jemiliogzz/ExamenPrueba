import streamlit as st
import random
from snowflake.snowpark.functions import col

# Limpiar caché
st.cache_data.clear()
st.cache_resource.clear()

# Función para inyectar CSS personalizado
def inject_custom_css():
    st.markdown("""
    <style>
        /* Estilos generales con tema celeste Snowflake */
        .main {
            background: linear-gradient(135deg, #E6F7FF 0%, #F0F9FF 50%, #E0F2FE 100%);
        }
        
        /* Estilo para el contenedor principal */
        .exam-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            border: 2px solid #29B5E8;
        }
        
        /* Estilo para la pregunta */
        .question-box {
            background: linear-gradient(135deg, #E6F7FF 0%, #B3E5FC 100%);
            border-radius: 10px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid #29B5E8;
            box-shadow: 0 2px 4px rgba(41, 181, 232, 0.2);
        }
        
        .question-number {
            color: #0277BD;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .question-text {
            color: #01579B;
            font-size: 16px;
            line-height: 1.6;
            margin-top: 10px;
        }
        
        /* Estilo para las opciones de respuesta */
        .answer-option {
            background: white;
            border: 2px solid #B3E5FC;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .answer-option:hover {
            background: #E1F5FE;
            border-color: #29B5E8;
            transform: translateX(5px);
        }
        
        /* Estilo para el progreso */
        .progress-container {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            border: 2px solid #B3E5FC;
        }
        
        /* Estilo para los botones */
        .stButton > button {
            background: linear-gradient(135deg, #29B5E8 0%, #0277BD 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #0277BD 0%, #01579B 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(41, 181, 232, 0.3);
        }
        
        /* Estilo para los resultados */
        .results-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            border: 2px solid #29B5E8;
        }
        
        .metric-box {
            background: linear-gradient(135deg, #E6F7FF 0%, #B3E5FC 100%);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border: 2px solid #29B5E8;
        }
        
        /* Ocultar elementos de Streamlit por defecto */
        .stMarkdown {
            margin-bottom: 0;
        }
        
        /* Estilo para el título */
        h1 {
            color: #0277BD;
            text-align: center;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

# Inyectar CSS
inject_custom_css()

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Inicializar estado de la sesión
if 'examen_iniciado' not in st.session_state:
    st.session_state.examen_iniciado = False
if 'preguntas' not in st.session_state:
    st.session_state.preguntas = []
if 'respuestas_usuario' not in st.session_state:
    st.session_state.respuestas_usuario = {}
if 'examen_completado' not in st.session_state:
    st.session_state.examen_completado = False
if 'pregunta_actual' not in st.session_state:
    st.session_state.pregunta_actual = 0
if 'respuestas_mezcladas' not in st.session_state:
    st.session_state.respuestas_mezcladas = {}

# Función para obtener preguntas de la tabla bank
def obtener_preguntas():
    try:
        preguntas_df = session.table("bank").collect()
        return preguntas_df
    except Exception as e:
        st.error(f"Error al obtener preguntas: {str(e)}")
        return []

# Función para mezclar respuestas
def mezclar_respuestas(dummy1, dummy2, dummy3, correct):
    respuestas = [dummy1, dummy2, dummy3, correct]
    random.shuffle(respuestas)
    return respuestas

# Función para inicializar respuestas mezcladas
def inicializar_respuestas_mezcladas(preguntas):
    if 'respuestas_mezcladas' not in st.session_state or len(st.session_state.respuestas_mezcladas) == 0:
        st.session_state.respuestas_mezcladas = {}
        for idx, pregunta in enumerate(preguntas):
            respuestas_mezcladas = mezclar_respuestas(
                pregunta.DUMMY1,
                pregunta.DUMMY2,
                pregunta.DUMMY3,
                pregunta.CORRECT
            )
            st.session_state.respuestas_mezcladas[idx] = {
                'respuestas': respuestas_mezcladas,
                'correcta': pregunta.CORRECT,
                'domain_id': pregunta.DOMAIN_ID,
                'subdomain': pregunta.SUBDOMAIN
            }

# Página de inicio
if not st.session_state.examen_iniciado:
    st.markdown("""
    <div style="text-align: center; padding: 40px;">
        <h1 style="color: #0277BD; font-size: 48px; margin-bottom: 20px;">❄️ Examen</h1>
        <p style="color: #01579B; font-size: 20px; margin-bottom: 30px;">
            Responde las preguntas y demuestra tus conocimientos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Iniciar Examen", use_container_width=True):
            preguntas = obtener_preguntas()
            if preguntas:
                st.session_state.preguntas = preguntas
                st.session_state.examen_iniciado = True
                st.session_state.respuestas_usuario = {}
                st.session_state.examen_completado = False
                st.session_state.pregunta_actual = 0
                st.session_state.respuestas_mezcladas = {}
                inicializar_respuestas_mezcladas(preguntas)
                st.rerun()
            else:
                st.error("No se pudieron cargar las preguntas. Verifica la conexión a Snowflake.")

# Mostrar examen (una pregunta a la vez)
if st.session_state.examen_iniciado and not st.session_state.examen_completado:
    preguntas = st.session_state.preguntas
    
    if not preguntas:
        st.error("No hay preguntas disponibles.")
    else:
        pregunta_idx = st.session_state.pregunta_actual
        pregunta = preguntas[pregunta_idx]
        total_preguntas = len(preguntas)
        
        # Barra de progreso
        progreso = (pregunta_idx + 1) / total_preguntas
        st.markdown(f"""
        <div class="progress-container">
            <p style="color: #0277BD; font-weight: bold; margin-bottom: 10px;">
                Progreso: Pregunta {pregunta_idx + 1} de {total_preguntas}
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progreso)
        
        # Contenedor de la pregunta
        st.markdown(f"""
        <div class="exam-container">
            <div class="question-box">
                <div class="question-number">Pregunta {pregunta_idx + 1} de {total_preguntas}</div>
                <div class="question-text">{pregunta.QUESTION}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Obtener respuestas mezcladas para esta pregunta
        respuestas_info = st.session_state.respuestas_mezcladas[pregunta_idx]
        respuestas_mezcladas = respuestas_info['respuestas']
        
        # Obtener respuesta previa si existe
        respuesta_anterior = st.session_state.respuestas_usuario.get(pregunta_idx, None)
        
        # Radio buttons para las respuestas
        respuesta_seleccionada = st.radio(
            "Selecciona tu respuesta:",
            respuestas_mezcladas,
            key=f"respuesta_{pregunta_idx}",
            index=respuestas_mezcladas.index(respuesta_anterior) if respuesta_anterior in respuestas_mezcladas else None
        )
        
        # Guardar respuesta
        st.session_state.respuestas_usuario[pregunta_idx] = respuesta_seleccionada
        
        # Navegación
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("⏮️ Primera", use_container_width=True):
                st.session_state.pregunta_actual = 0
                st.rerun()
        
        with col2:
            if st.button("◀️ Anterior", use_container_width=True, disabled=(pregunta_idx == 0)):
                if pregunta_idx > 0:
                    st.session_state.pregunta_actual -= 1
                    st.rerun()
        
        with col3:
            if st.button("Siguiente ▶️", use_container_width=True, disabled=(pregunta_idx == total_preguntas - 1)):
                if pregunta_idx < total_preguntas - 1:
                    st.session_state.pregunta_actual += 1
                    st.rerun()
        
        with col4:
            if st.button("⏭️ Última", use_container_width=True):
                st.session_state.pregunta_actual = total_preguntas - 1
                st.rerun()
        
        st.divider()
        
        # Botón para finalizar examen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Verificar si todas las preguntas tienen respuesta
            todas_respondidas = len(st.session_state.respuestas_usuario) == total_preguntas
            
            if todas_respondidas:
                if st.button("✅ Finalizar Examen", use_container_width=True, type="primary"):
                    st.session_state.examen_completado = True
                    st.rerun()
            else:
                faltantes = total_preguntas - len(st.session_state.respuestas_usuario)
                st.warning(f"⚠️ Te faltan {faltantes} pregunta(s) por responder")
                if st.button("Finalizar de todas formas", use_container_width=True):
                    st.session_state.examen_completado = True
                    st.rerun()

# Mostrar resultados
if st.session_state.examen_completado:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #0277BD; font-size: 42px; margin-bottom: 10px;">📊 Resultados del Examen</h1>
    </div>
    """, unsafe_allow_html=True)
    
    preguntas = st.session_state.preguntas
    respuestas_usuario = st.session_state.respuestas_usuario
    
    aciertos = 0
    errores = 0
    subdominios_errores = set()
    
    # Calcular resultados
    for idx, pregunta in enumerate(preguntas):
        respuesta_correcta = pregunta.CORRECT
        respuesta_usuario = respuestas_usuario.get(idx, "")
        
        if respuesta_usuario == respuesta_correcta:
            aciertos += 1
        else:
            errores += 1
            # Agregar subdominio en formato 'domain_id'.'subdomain'
            subdominio = f"{pregunta.DOMAIN_ID}.{pregunta.SUBDOMAIN}"
            subdominios_errores.add(subdominio)
    
    # Mostrar estadísticas
    total_preguntas = len(preguntas)
    porcentaje = (aciertos / total_preguntas * 100) if total_preguntas > 0 else 0
    
    st.markdown("""
    <div class="results-container">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #0277BD; margin: 0;">✅ Aciertos</h2>
            <p style="font-size: 36px; font-weight: bold; color: #01579B; margin: 10px 0;">{aciertos}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #0277BD; margin: 0;">❌ Errores</h2>
            <p style="font-size: 36px; font-weight: bold; color: #01579B; margin: 10px 0;">{errores}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #0277BD; margin: 0;">📈 Porcentaje</h2>
            <p style="font-size: 36px; font-weight: bold; color: #01579B; margin: 10px 0;">{porcentaje:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Mostrar subdominios con errores
    st.markdown("""
    <div class="exam-container">
    """, unsafe_allow_html=True)
    
    if subdominios_errores:
        st.subheader("🔍 Subdominios donde te equivocaste:")
        subdominios_ordenados = sorted(subdominios_errores)
        for subdominio in subdominios_ordenados:
            st.markdown(f"""
            <div style="background: #FFE0E0; border-left: 4px solid #D32F2F; padding: 10px; margin: 5px 0; border-radius: 5px;">
                <strong style="color: #C62828;">{subdominio}</strong>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #E8F5E9; border-left: 4px solid #4CAF50; padding: 15px; border-radius: 5px; text-align: center;">
            <p style="color: #2E7D32; font-size: 18px; margin: 0;">🎉 ¡Excelente! No tuviste errores en ningún subdominio.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Detalle de respuestas
    with st.expander("📋 Ver detalle de respuestas", expanded=False):
        for idx, pregunta in enumerate(preguntas):
            respuesta_correcta = pregunta.CORRECT
            respuesta_usuario = respuestas_usuario.get(idx, "")
            es_correcta = respuesta_usuario == respuesta_correcta
            
            if es_correcta:
                st.markdown(f"""
                <div style="background: #E8F5E9; border-left: 4px solid #4CAF50; padding: 15px; margin: 10px 0; border-radius: 5px;">
                    <strong style="color: #2E7D32;">Pregunta {idx + 1}: ✅ Correcta</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #FFE0E0; border-left: 4px solid #D32F2F; padding: 15px; margin: 10px 0; border-radius: 5px;">
                    <strong style="color: #C62828;">Pregunta {idx + 1}: ❌ Incorrecta</strong>
                </div>
                """, unsafe_allow_html=True)
            
            st.write(f"**Pregunta:** {pregunta.QUESTION}")
            st.write(f"**Tu respuesta:** {respuesta_usuario}")
            st.write(f"**Respuesta correcta:** {respuesta_correcta}")
            st.write(f"**Subdominio:** {pregunta.DOMAIN_ID}.{pregunta.SUBDOMAIN}")
            st.divider()
    
    # Botón para reiniciar examen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Reiniciar Examen", use_container_width=True):
            st.session_state.examen_iniciado = False
            st.session_state.preguntas = []
            st.session_state.respuestas_usuario = {}
            st.session_state.examen_completado = False
            st.session_state.pregunta_actual = 0
            st.session_state.respuestas_mezcladas = {}
            # Limpiar estados de preguntas individuales
            for key in list(st.session_state.keys()):
                if key.startswith('pregunta_') or key.startswith('respuesta_'):
                    del st.session_state[key]
            st.rerun()
