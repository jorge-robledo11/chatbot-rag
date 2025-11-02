<script setup>
import { onMounted, ref } from 'vue';
import { marked } from 'marked';
import Doc from './Doc.vue'

let urlaudio = ref('')
let textaudio = ref('')
const messageHtml = ref('')
const isMarkdown = ref(false)

const props = defineProps({
    msg: {
        type: Object,
        required: true
    },
})

const getFileType = (fileName) => {
    const isFile = fileName.split('@').shift()
    return isFile
};

const getAudio = () => {
    const audio = props.msg.text.split('@').pop().split('#')
    textaudio.value = audio.shift()
    urlaudio.value = audio.pop()
};

const processMessage = () => {
    if (getFileType(props.msg.text) !== 'audio' && getFileType(props.msg.text) !== 'file') {
        // Si no tiene salto de línea NI caracteres especiales de markdown, solo texto plano
        const text = props.msg.text
        const markdownPattern = /[*_`#\-]/;
        if (!text.includes('\n') && !markdownPattern.test(text)) {
            messageHtml.value = text;
            isMarkdown.value = false;
        } else {
            messageHtml.value = marked.parse(text);
            isMarkdown.value = true;
        }
    }
}

onMounted(() => {
    getAudio()
    processMessage()
});
</script>

<template>
    <div class="user-message">
        <div class="message-content">
            <span v-if="getFileType(msg.text) == 'file'" class="file-message">
                <div class="file-indicator">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 1H3a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V7l-6-6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M9 1v6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span>Documento adjunto cargado</span>
                </div>
                <Doc :docPayload="msg.text" />
            </span>
            
            <span v-else-if="getFileType(msg.text) == 'audio'" class="audio-message">
                <div class="audio-text">{{ textaudio }}</div>
                <div class="audio-player">
                    <audio :src="urlaudio" controls preload="metadata"></audio>
                </div>
            </span>
            
            <span v-else class="text-message" :class="{ 'plain': !isMarkdown }" v-html="messageHtml"></span>
        </div>
        
        <div class="message-timestamp">
            {{ new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }) }}
        </div>
    </div>
</template>

<style scoped>
.user-message {
    max-width: 75%;
    align-self: flex-end;
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.message-content {
    padding: 20px 24px;
    border-radius: 18px 18px 4px 18px;
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
    color: var(--white);
    font-size: 0.95rem;
    font-family: 'Inter', 'Roboto', system-ui, sans-serif;
    font-weight: 500;
    line-height: 1.6;
    white-space: pre-wrap;
    overflow: hidden;
    user-select: text;
    text-align: left;
    box-shadow: var(--shadow-light);
    position: relative;
}

.message-content::after {
    content: '';
    position: absolute;
    bottom: -8px;
    right: 12px;
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid var(--secondary-blue);
}

.text-message {
    display: block;
    font-weight: 400;
}
.text-message.plain p {
    margin: 0 !important;
}
.text-message.plain {
    white-space: pre-line;
}

/* --- El resto igual --- */
.file-message {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.file-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 500;
}

.file-indicator svg {
    flex-shrink: 0;
    opacity: 0.8;
}

.audio-message {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.audio-text {
    font-weight: 400;
    margin-bottom: 8px;
}

.audio-player {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px;
}

.audio-player audio {
    width: 100%;
    height: 32px;
    border-radius: 4px;
}

.audio-player audio::-webkit-media-controls-panel {
    background-color: rgba(255, 255, 255, 0.1);
}

.message-timestamp {
    font-size: 0.625rem;
    color: var(--medium-gray);
    text-align: right;
    margin-right: 8px;
    opacity: 0.7;
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .user-message {
        max-width: 85%;
    }
    
    .message-content {
        padding: 14px 16px;
        font-size: 0.90rem;
        border-radius: 16px 16px 4px 16px;
    }
    
    .message-content::after {
        bottom: -6px;
        right: 10px;
        border-top: 6px solid var(--secondary-blue);
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
    }
    
    .file-indicator {
        padding: 6px 10px;
        font-size: 0.6875rem;
    }
    
    .message-timestamp {
        font-size: 0.5625rem;
        margin-right: 6px;
    }
}

@media (max-width: 480px) {
    .user-message {
        max-width: 90%;
    }
    
    .message-content {
        padding: 12px 14px;
        font-size: 0.87rem;
    }
    
    .audio-player audio {
        height: 28px;
    }
}
</style>
