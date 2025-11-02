<script setup>
import { ref, onMounted } from 'vue';
import { sharedState } from '../state'

import Header from '../components/Header.vue';
import ContentChat from '../components/ContentChat.vue';
import InputChat from '../components/InputChat.vue';
import api from '../api'

const ContentChatRef = ref(null);

const UpChat = (newMessage) => {
    if (newMessage.type === 'audio') {
        ContentChatRef.value.addMessage(true, true, '')
        fetchAUDIO(newMessage.data, newMessage.url)
    } else if (newMessage.type === 'text') {
        fetchCHAT(newMessage.data)
    }
}

const fetchCHAT = async (msg) => {
    ContentChatRef.value.addMessage(true, false, msg);
    ContentChatRef.value.addMessage(false, true, '');

    // Obtener session_id del localStorage, pero NO crearlo aquí
    let sessionId = localStorage.getItem("session_id");
    
    // Si no hay session_id, enviar undefined para que el backend cree uno nuevo
    let data = {
        "query": String(msg)
    };
    
    // Solo agregar session_id si existe y tiene el formato correcto (empieza con 'sess_')
    if (sessionId && sessionId.startsWith('sess_')) {
        data.session_id = sessionId;
    }

    console.log("Enviando a la API:", data);

    try {
        let result = await api.requestCHAT(data);
        console.log("Respuesta de la API:", result);

        // Guardar el session_id que devuelve el backend
        if (result.session_id) {
            localStorage.setItem("session_id", result.session_id);
        }

        // Procesar respuesta correctamente
        const processedResult = {
            text: result.response,
            id: Math.random(),
            isUser: false,
            sources: result.sources || []
        };
        
        ContentChatRef.value.addMessage(false, false, processedResult);
    } catch (error) {
        console.error('API error fetchCHAT:', error.response?.data || error.message);
        
        // Mostrar mensaje de error
        ContentChatRef.value.addMessage(false, false, {
            text: "Lo siento, ha ocurrido un error. Por favor, intenta de nuevo.",
            id: Math.random(),
            isUser: false,
            isError: true
        });
    }
};

// const fetchAUDIO = async (formData, urlData) => {
//     try {
//         const result = await api.requestWhisper(formData)
//         fetchCHAT(`audio@${result.text}#${urlData}`)
//     } catch (error) {
//         console.error('API Error fetchAUDIO:', error);
//     }
// }

const fetchVote = async (data) => {
    try {
        const result = await api.requestVote(data);
        console.log(result)
    } catch (error) {
        console.error('API error fetchVote:', error);
    }
}

const loadAttachment = async (data) => {
    ContentChatRef.value.addMessage(true, false, `file@${data?.file.name}`)
    ContentChatRef.value.addMessage(false, true, '')
    const formData = new FormData();
    console.log(data.file.name)
    formData.append("file", data.file);
    try {
        const result = await api.requestAttachment(formData)
        result['isUser'] = false
        ContentChatRef.value.addMessage(false, false, result)

    } catch (error) {
        console.error('API error loadAttachment:', error);
    }
}

const cleanChat = () => {
    ContentChatRef.value.cleanMessages();
    localStorage.removeItem("session_id");
    console.log("Chat y session_id eliminados");
};

onMounted(() => {
    localStorage.setItem('transcription', 'null');

    // NO crear session_id aquí, dejar que el backend lo maneje
    // Si existe un session_id válido, lo mantenemos
    const existingSessionId = localStorage.getItem("session_id");
    if (existingSessionId && !existingSessionId.startsWith('sess_')) {
        // Si el session_id no tiene el formato correcto, eliminarlo
        localStorage.removeItem("session_id");
    }

    ContentChatRef.value.addMessage(false, false, { 
        text: "¡Hola! 👋 Soy tu asistente virtual, listo para ayudarte en lo que necesites.", 
        id: Math.random(), 
        isUser: false 
    });
});
</script>

<template>
    <div class="cardContent">
        <div class="cardContent-content">
            <Header @clean="cleanChat"/>
            <ContentChat ref="ContentChatRef" @pushed_vote="fetchVote" />
            <InputChat @pushed_message="UpChat" @file_loaded="loadAttachment" />
        </div>
    </div>
</template>

<style scoped>
.cardContent {
    display: flex;
    flex-direction: column;
    height: 100%;
    /* Fondo con colores de Ajover */
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--accent-red) 100%);
    /* O solo azul: background: var(--primary-blue); */
    backdrop-filter: blur(5px);
    overflow: hidden;
    position: relative;
}

.cardContent::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--accent-red) 0%, var(--primary-blue) 50%, var(--secondary-blue) 100%);
    z-index: 1;
}

.cardContent-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
    z-index: 0;
    /* Fondo blanco para la tarjeta central si lo necesitas */
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    margin: 24px;
    box-shadow: 0 6px 24px rgba(30,77,139,0.08);
}

@media (max-width: 768px) {
    .cardContent {
        border-radius: 0;
    }
    .cardContent-content {
        margin: 0;
        border-radius: 0;
    }
}
</style>
