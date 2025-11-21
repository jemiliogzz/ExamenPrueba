import streamlit as st
import random
from snowflake.snowpark.functions import col

# Limpiar caché
st.cache_data.clear()
st.cache_resource.clear()

# Título de la aplicación
st.title("📝 Examen")
st.write("Responde las siguientes preguntas. Al finalizar verás tus resultados.")

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

# Iniciar examen
if not st.session_state.examen_iniciado:
    if st.button("Iniciar Examen"):
        preguntas = obtener_preguntas()
        if preguntas:
            st.session_state.preguntas = preguntas
            st.session_state.examen_iniciado = True
            st.session_state.respuestas_usuario = {}
            st.session_state.examen_completado = False
            st.rerun()
        else:
            st.error("No se pudieron cargar las preguntas. Verifica la conexión a Snowflake.")

# Mostrar examen
if st.session_state.examen_iniciado and not st.session_state.examen_completado:
    preguntas = st.session_state.preguntas
    
    if not preguntas:
        st.error("No hay preguntas disponibles.")
    else:
        st.write(f"**Total de preguntas:** {len(preguntas)}")
        st.divider()
        
        # Formulario para el examen
        with st.form("formulario_examen"):
            respuestas_seleccionadas = {}
            
            for idx, pregunta in enumerate(preguntas):
                st.write(f"**Pregunta {idx + 1}:**")
                st.write(pregunta.QUESTION)
                
                # Obtener respuestas y mezclarlas
                respuestas_mezcladas = mezclar_respuestas(
                    pregunta.DUMMY1,
                    pregunta.DUMMY2,
                    pregunta.DUMMY3,
                    pregunta.CORRECT
                )
                
                # Guardar el orden de las respuestas mezcladas para poder identificar la correcta
                # Necesitamos saber cuál es la respuesta correcta después de mezclar
                respuesta_correcta = pregunta.CORRECT
                
                # Crear opciones para el selectbox
                opciones = respuestas_mezcladas
                
                # Guardar información de la pregunta en el estado
                if f'pregunta_{idx}' not in st.session_state:
                    st.session_state[f'pregunta_{idx}'] = {
                        'respuestas_mezcladas': respuestas_mezcladas,
                        'respuesta_correcta': respuesta_correcta,
                        'domain_id': pregunta.DOMAIN_ID,
                        'subdomain': pregunta.SUBDOMAIN
                    }
                
                # Selectbox para seleccionar respuesta
                respuesta_seleccionada = st.radio(
                    "Selecciona tu respuesta:",
                    opciones,
                    key=f"respuesta_{idx}"
                )
                
                respuestas_seleccionadas[idx] = respuesta_seleccionada
                st.divider()
            
            # Botón para enviar examen
            enviar = st.form_submit_button("Finalizar Examen")
            
            if enviar:
                st.session_state.respuestas_usuario = respuestas_seleccionadas
                st.session_state.examen_completado = True
                st.rerun()

# Mostrar resultados
if st.session_state.examen_completado:
    st.title("📊 Resultados del Examen")
    
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ Aciertos", aciertos)
    
    with col2:
        st.metric("❌ Errores", errores)
    
    with col3:
        st.metric("📈 Porcentaje", f"{porcentaje:.1f}%")
    
    st.divider()
    
    # Mostrar subdominios con errores
    if subdominios_errores:
        st.subheader("Subdominios donde te equivocaste:")
        subdominios_ordenados = sorted(subdominios_errores)
        for subdominio in subdominios_ordenados:
            st.write(f"- **{subdominio}**")
    else:
        st.success("🎉 ¡Excelente! No tuviste errores en ningún subdominio.")
    
    st.divider()
    
    # Detalle de respuestas
    with st.expander("Ver detalle de respuestas"):
        for idx, pregunta in enumerate(preguntas):
            respuesta_correcta = pregunta.CORRECT
            respuesta_usuario = respuestas_usuario.get(idx, "")
            es_correcta = respuesta_usuario == respuesta_correcta
            
            if es_correcta:
                st.success(f"**Pregunta {idx + 1}:** ✅ Correcta")
            else:
                st.error(f"**Pregunta {idx + 1}:** ❌ Incorrecta")
            
            st.write(f"**Pregunta:** {pregunta.QUESTION}")
            st.write(f"**Tu respuesta:** {respuesta_usuario}")
            st.write(f"**Respuesta correcta:** {respuesta_correcta}")
            st.write(f"**Subdominio:** {pregunta.DOMAIN_ID}.{pregunta.SUBDOMAIN}")
            st.divider()
    
    # Botón para reiniciar examen
    if st.button("🔄 Reiniciar Examen"):
        st.session_state.examen_iniciado = False
        st.session_state.preguntas = []
        st.session_state.respuestas_usuario = {}
        st.session_state.examen_completado = False
        # Limpiar estados de preguntas individuales
        for key in list(st.session_state.keys()):
            if key.startswith('pregunta_') or key.startswith('respuesta_'):
                del st.session_state[key]
        st.rerun()
