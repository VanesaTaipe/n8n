import streamlit as st
import requests
import base64
from audio_recorder_streamlit import audio_recorder
import uuid

# URL del webhook de n8n
WEBHOOK_URL = "https://nelsy.app.n8n.cloud/webhook/api-agent"

# Inicializar session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Configuración de la página
st.set_page_config(page_title="Agente Conversacional", page_icon="🤖")

# Título
st.title("🤖 Agente Conversacional")
st.caption(f"Usuario: {st.session_state.user_id[:8]}...")

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Tabs para texto y audio
tab1, tab2 = st.tabs(["💬 Texto", "🎤 Audio"])

with tab1:
    # Input de texto
    if prompt := st.chat_input("Escribe tu mensaje..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Enviar al webhook
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    response = requests.post(
                        WEBHOOK_URL,
                        json={
                            "text": prompt,
                            "userId": st.session_state.user_id
                        },
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        assistant_message = result.get("output", "No recibí respuesta")
                        st.markdown(assistant_message)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")

with tab2:
    st.write("Graba tu mensaje de audio:")
    
    # Grabador de audio
    audio_bytes = audio_recorder(
        text="Haz clic para grabar",
        recording_color="#e74c3c",
        neutral_color="#3498db",
        icon_name="microphone",
        icon_size="2x"
    )
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        if st.button("Enviar Audio"):
            # Convertir audio a base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            with st.spinner("Procesando audio..."):
                try:
                    response = requests.post(
                        WEBHOOK_URL,
                        json={
                            "audioBase64": audio_base64,
                            "userId": st.session_state.user_id
                        },
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        assistant_message = result.get("output", "No recibí respuesta")
                        
                        st.session_state.messages.append({
                            "role": "user",
                            "content": "🎤 [Mensaje de audio]"
                        })
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                        
                        st.success("Audio procesado!")
                        st.rerun()
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")

# Botón para limpiar conversación
if st.sidebar.button("🗑️ Limpiar Conversación"):
    st.session_state.messages = []
    st.session_state.user_id = str(uuid.uuid4())
    st.rerun()
