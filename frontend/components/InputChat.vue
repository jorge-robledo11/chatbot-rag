<script setup>
import { ref, computed, onMounted } from 'vue'
import { sharedState } from '../state'
import VoiceRecord from './utils/VoiceRecord.vue'
import Attachment from './utils/Attachment.vue'

const emit = defineEmits(['send-message'])

const messageText = ref('')
const isRecording = ref(false)
const showAttachment = ref(false)

const canSend = computed(() => {
    return messageText.value.trim().length > 0
})

const sendMessage = () => {
    console.log('🔥 sendMessage ejecutado')
    if (canSend.value) {
        console.log('🚀 Emitiendo mensaje:', messageText.value)
        emit('pushed_message', {
            type: 'text',
            data: messageText.value.trim()
        })
        messageText.value = ''
    }
}

const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        sendMessage()
    }
}

onMounted(() => {
    // Focus en el input al cargar
    const input = document.querySelector('.message-input')
    if (input) {
        input.focus()
    }
})
</script>

<template>
    <div class="input-container">
        <div class="input-wrapper">
            <div class="message-input-container">
                <input 
                    v-model="messageText"
                    @keypress="handleKeyPress"
                    type="text" 
                    class="message-input"
                    placeholder="Escribe tu mensaje aquí..."
                    :disabled="sharedState.isLoading"
                />
            </div>
            
            <div class="input-controls-right">
                <button 
                    class="control-btn send-btn"
                    :class="{ active: canSend }"
                    @click="sendMessage"
                    :disabled="!canSend || sharedState.isLoading"
                    title="Enviar mensaje"
                >
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 2L9 11M18 2L12 18L9 11M18 2L2 8L9 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
        </div>
        
        <div class="input-footer">
            <p class="footer-text">
                Powered by <strong>Ajover</strong> • Asistente Virtual Corporativo
            </p>
        </div>
    </div>
</template>

<style scoped>
.input-container {
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(8px);
    border-top: 1px solid rgba(30, 77, 139, 0.1);
    position: relative;
}

.input-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 20px;
    right: 20px;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, var(--accent-red) 30%, var(--primary-blue) 70%, transparent 100%);
}

.input-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px;
    padding-bottom: calc(env(safe-area-inset-bottom) + 20px);
}

.message-input-container {
    flex: 1;
    position: relative;
}

.message-input {
    width: 100%;
    padding: 14px 20px;
    border: 2px solid #e5e7eb;
    border-radius: 25px;
    font-size: 0.875rem;
    font-family: inherit;
    background: var(--white);
    color: var(--dark-gray);
    transition: all 0.3s ease;
    box-sizing: border-box;
}

.message-input:focus {
    outline: none;
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 3px rgba(30, 77, 139, 0.1);
    background: rgba(30, 77, 139, 0.02);
}

.message-input::placeholder {
    color: var(--medium-gray);
    font-style: italic;
}

.input-controls-right {
    display: flex;
    align-items: center;
}

.control-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
}

.send-btn {
    background: var(--light-gray);
    color: var(--medium-gray);
    border: 1px solid rgba(107, 114, 128, 0.3);
    transition: all 0.3s ease;
}

.send-btn.active {
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
    color: var(--white);
    border-color: var(--primary-blue);
    box-shadow: var(--shadow-light);
}

.send-btn.active:hover {
    transform: scale(1.05);
    box-shadow: var(--shadow-medium);
}

.send-btn:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}

.input-footer {
    padding: 8px 20px 12px;
    text-align: center;
}

.footer-text {
    font-size: 0.75rem;
    color: var(--medium-gray);
    margin: 0;
    font-weight: 400;
}

.footer-text strong {
    color: var(--primary-blue);
    font-weight: 600;
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .input-wrapper {
        padding: 16px;
        gap: 10px;
        padding-bottom: calc(env(safe-area-inset-bottom) + 16px);
    }
    
    .message-input {
        padding: 12px 16px;
        font-size: 0.875rem;
    }
    
    .control-btn {
        width: 40px;
        height: 40px;
    }
    
    .input-footer {
        padding: 6px 16px 10px;
    }
    
    .footer-text {
        font-size: 0.625rem;
    }
}

@media (max-width: 480px) {
    .input-wrapper {
        padding: 12px;
        gap: 8px;
    }
    
    .control-btn {
        width: 36px;
        height: 36px;
    }
    
    .message-input {
        padding: 10px 14px;
        border-radius: 20px;
    }
}
</style>