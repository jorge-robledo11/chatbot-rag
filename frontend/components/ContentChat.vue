<script setup>

import AIMessage from './utils/IAMessage.vue'
import UserMessage from './utils/HumanMessage.vue'
import { ref, inject, nextTick, watch, computed } from 'vue'

const emit = defineEmits(['pushed_vote'])
const scrollContainer = ref(null);

const addMessage = (isUser, isLoading, newMessage) => {
    if (isUser) {
        handleUserMessage(isLoading, newMessage);
    } else {
        handleBotMessage(isLoading, newMessage);
    }
    scrollToBottom();
};

const handleUserMessage = (isLoading, newMessage) => {
    if (isLoading) {
        messages.value.push({ text: "procesando audio...", isUser: true, isLoading });
    } else {
        if (messages.value[messages.value.length - 1]?.isUser) {
            messages.value.pop();
        }
        const message = {
            id: messages.value.length + 1,
            isUser: true,
            text: newMessage,
        };
        messages.value.push(message);
    }

};

const handleBotMessage = (isLoading, newMessage) => {
    if (isLoading) {
        messages.value.push({ isUser: false, isLoading });
    } else {
        if (messages.value.length === 0) {
            newMessage.isFirst = true;
        } else {
            newMessage.isFirst = false;
        }
        messages.value.pop();
        messages.value.push(newMessage);
    }
};

const handleVote = (vote) => {
    emit('pushed_vote', vote)
}

const scrollToBottom = async () => {
    await nextTick()
    const container = scrollContainer.value;
    container.scrollTop = container.scrollHeight;
};

const cleanMessages = () => {
    if (messages.value.length > 1) {
        messages.value = []
        addMessage(false, false, { text: "¡Hola! 👋 Soy tu asistente virtual, listo para ayudarte en lo que necesites.", id: Math.random(), isUser: false })
    }
}

defineExpose({
    addMessage,
    cleanMessages
});

const messages = ref([])

</script>

<template>
    <div class="chat-container">
        <div class="brand-watermark">
            <div class="watermark-content">
                <img src="/assets/logo_ajover.png" alt="Logo Ajover" class="watermark-logo-img" />
                <div class="watermark-text">
                    <span class="watermark-brand">AJOVER</span>
                    <span class="watermark-subtitle">Asistente Virtual</span>
                </div>
            </div>
        </div>
        
        <div class="messages-container" ref="scrollContainer">
            <div class="message-wrapper" v-for="msg in messages" :key="msg.id">
                <UserMessage :msg="msg" v-if="msg.isUser" />
                <AIMessage :msg="msg" @vote="handleVote" v-else />
            </div>
        </div>
    </div>
</template>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    position: relative;
    background: var(--white);
}

.brand-watermark {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 0;
    pointer-events: none;
    opacity: 0.08;
}

.watermark-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
}

.watermark-logo-img {
    width: 120px;
    height: 120px;
    object-fit: contain;
    filter: grayscale(1) opacity(0.3);
}

.watermark-text {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.watermark-brand {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--primary-blue);
    letter-spacing: 0.1em;
}

.watermark-subtitle {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--medium-gray);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: relative;
    z-index: 1;
    scroll-behavior: smooth;
}

.message-wrapper {
    display: flex;
    flex-direction: column;
    position: relative;
}

.message-wrapper:first-child {
    margin-top: 0;
}

.message-wrapper:last-child {
    margin-bottom: 20px;
}

/* SCROLLBAR PERSONALIZADA PARA EL CHAT */
.messages-container::-webkit-scrollbar {
    width: 6px;
}

.messages-container::-webkit-scrollbar-track {
    background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
    background: var(--medium-gray);
    border-radius: 6px;
    opacity: 0.3;
}

.messages-container::-webkit-scrollbar-thumb:hover {
    background: var(--primary-blue);
    opacity: 0.6;
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .messages-container {
        padding: 16px;
        gap: 12px;
    }
    
    .watermark-logo-img {
        width: 80px;
        height: 80px;
    }
    
    .watermark-brand {
        font-size: 2rem;
    }
    
    .watermark-subtitle {
        font-size: 0.75rem;
    }
    
    .message-wrapper:last-child {
        margin-bottom: 16px;
    }
}

@media (max-width: 480px) {
    .messages-container {
        padding: 12px;
        gap: 10px;
    }
    
    .watermark-logo-img {
        width: 60px;
        height: 60px;
    }
    
    .watermark-brand {
        font-size: 1.5rem;
    }
    
    .watermark-content {
        gap: 12px;
    }
}
</style>