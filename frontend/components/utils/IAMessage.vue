<template>
    <div class="ai">
        <div class="typing" v-if="props.msg.isLoading">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </div>
        <div v-else>
            <div class="content">
                <div v-for="(content, index) in extractedContent" :key="index">
                    <div v-if="content.type === 'citations'" class="citations section" v-html="content.value"></div>
                    <div v-else-if="content.type === 'table'" class="table section">
                        <table v-html="content.value"></table>
                    </div>
                    <div v-else-if="content.type === 'code'" class="code">
                        <div class="code-header">
                            <span>{{ content.lang }}</span>
                            <button class="copy-button" @click="copyToClipboard(content.value)">
                                <i class="fa-solid fa-copy"></i>
                            </button>
                        </div>
                        <pre v-html="content.value"></pre>
                    </div>
                    <div v-else-if="content.type === 'chart'" class="section">
                        <component :is="getChartComponent(content.chartType)" :data="content.data"
                            :options="content.options" :style="{ height: '400px' }" />
                    </div>
                    <div v-else-if="content.type === 'card'" class="section">
                        <CardAdaptative :cardPayload="content.value" />
                    </div>
                    <div v-else-if="content.type === 'doc'" class="section">
                        <Doc :docPayload="content.value" />
                    </div>
                    <div v-else-if="content.type === 'map'" class="section">
                        <Map :xy="content.xy" :ubication="content.ubication" />
                    </div>
                    <div v-else-if="content.type === 'image'" class="section">
                        <img :src="content.value" alt="Image Content" />
                    </div>
                    <div v-else v-html="content.value"></div>
                </div>
            </div>
            <div class="feedback" v-if="!msg.isFirst">
                <button @click="handlevote(true)" :class="{ 'voted': selectedVote }" :disabled="selectedVote !== null">
                    <i class="fa-regular fa-thumbs-up"></i>
                </button>
                <button @click="handlevote(false)" :class="{ 'voted': selectedVote === false }"
                    :disabled="selectedVote !== null">
                    <i class="fa-regular fa-thumbs-down"></i>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { inject, computed, ref, onMounted } from 'vue'
import { Chart, BarElement, BarController, PieController, CategoryScale, LinearScale, ArcElement, Tooltip, Legend, LineController, PointElement, LineElement } from 'chart.js';
import { Bar, Pie, Line } from 'vue-chartjs';
import { marked } from 'marked';
import CardAdaptative from './CardAdaptative.vue';
import Doc from './Doc.vue';
import Map from './Map.vue';
import api from '../../api';

Chart.register(BarElement, BarController, PieController, CategoryScale, LinearScale, ArcElement, Tooltip, Legend, LineController, PointElement, LineElement);

const props = defineProps({
    msg: {
        type: Object,
        required: true,
    },
})
const emit = defineEmits(['vote'])

const selectedVote = ref(null);

const regex = /<(citations|table|chart|code|doc|image|card|map)>(.*?)<\/\1>/gs;
const extractedContent = ref([]);

// CAMBIO PRINCIPAL: NO hagas reemplazos manuales de saltos ni bullets
const cleanContent = (content) => {
    return marked.parse(content.trim(), { breaks: true });
};

const chartComponents = {
    'bar': Bar,
    'pie': Pie,
    'line': Line,
};
const getChartComponent = (chartType) => {
    return chartComponents[chartType] || Bar;
};

const typeHandlers = {
    'code': (p2) => {
        const codeMatch = /```(\w*)\n([\s\S]*?)```/.exec(p2);
        return {
            type: 'code',
            value: cleanContent(codeMatch ? codeMatch[2] : p2),
            lang: codeMatch ? codeMatch[1] : 'plain-text',
        };
    },
    'chart': (p2) => {
        const chartData = JSON.parse(p2);
        console.log(chartData.data);
        return {
            type: 'chart',
            chartType: chartData.type,
            data: chartData.data,
            options: chartData.options || {},
        };
    },
    'card': (p2) => {
        const cardData = JSON.parse(p2);
        return {
            type: 'card',
            value: cardData,
        };
    },
    /*'doc': (p2) => {
        const cardData = JSON.parse(p2);
        return {
            type: 'doc',
            value: cardData,
        };
    },*/
    'map': (p2) => {
        const mapData = JSON.parse(p2);
        return {
            type: 'map',
            xy: mapData.xy,
            ubication: mapData.ubication,
        };
    }
    /*'table': (p2) => ({
        type: 'table',
        value: cleanContent(p2),
    }),*/
};

const processMessage = () => {
    const messageText = props.msg.text;
    let lastIndex = 0;

    messageText.replace(regex, (match, p1, p2, offset) => {
        if (offset > lastIndex) {
            extractedContent.value.push({
                type: 'text',
                value: cleanContent(messageText.slice(lastIndex, offset).trim()),
            });
        }

        const handler = typeHandlers[p1] || ((p2) => ({
            type: p1,
            value: cleanContent(p2),
        }));

        extractedContent.value.push(handler(p2));

        lastIndex = offset + match.length;
    });

    if (lastIndex < messageText.length) {
        extractedContent.value.push({
            type: 'text',
            value: cleanContent(messageText.slice(lastIndex).trim())
        });
    }
};


const handlevote = async (vote) => {
    if (selectedVote.value === null) {
        selectedVote.value = vote;
        // Emitimos el evento 'vote' (si es necesario para otros componentes)
        const voteData = {
            "id": String(props.msg.id),
            "thread_id": "User2",
            "rate": vote 
        };
        console.log('Datos enviados:', voteData)
        try {
            // Llamamos a la función requestVote para enviar la solicitud al backend
            await api.requestVote(voteData.id, voteData.rate);
            console.log("Voto enviado con éxito");
        } catch (error) {
            console.error("Error al enviar el voto:", error);
        }
    }
};

const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard');
    }, () => {
        console.log('Failed to copy');
    });
};

onMounted(() => {
    if (props.msg.isLoading) {
        return;
    }
    processMessage();
})
</script>

<style scoped>
.ai {
    max-width: 85%;
    padding: 20px;
    border-radius: 16px;
    background: linear-gradient(135deg, var(--light-gray) 0%, var(--white) 100%);
    margin-bottom: 16px;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    box-shadow: var(--shadow-light);
    border: 1px solid rgba(30, 77, 139, 0.08);
    align-self: flex-start;
}

.ai::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary-blue) 0%, var(--light-blue) 100%);
    border-radius: 16px 16px 0 0;
}

.content {
    white-space: normal;
    overflow: hidden;
    text-align: left;
    margin-bottom: 0; 
    padding-bottom: 0;
    width: 100%;
    color: var(--dark-gray);
    font-size: 0.875rem;
    line-height: 1.6;
}

.content p {
    margin: 0 0 12px 0;
    color: var(--dark-gray);
}

.content strong {
    color: var(--primary-blue);
    font-weight: 600;
}

.content ul, .content ol {
    margin: 8px 0 12px 0;
    padding-left: 20px;
}

.content li {
    margin-bottom: 4px;
    color: var(--dark-gray);
}

.feedback {
    position: absolute;
    right: 16px;
    bottom: -16px;
    display: flex;
    gap: 8px;
    z-index: 10;
}

.feedback button {
    background: var(--white);
    border: 2px solid rgba(30, 77, 139, 0.1);
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    box-shadow: var(--shadow-light);
    transition: all 0.3s ease;
    color: var(--medium-gray);
}

.feedback button:hover {
    background: var(--light-gray);
    border-color: var(--primary-blue);
    color: var(--primary-blue);
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
}

.feedback button.voted {
    background: var(--primary-blue);
    border-color: var(--primary-blue);
    color: var(--white);
    opacity: 0.8;
}

.feedback button:disabled {
    cursor: not-allowed;
    opacity: 0.6;
}

.citations {
    font-size: 0.75rem;
    color: var(--primary-blue);
    margin: 12px 0;
    padding: 12px;
    background: rgba(30, 77, 139, 0.05);
    border-left: 4px solid var(--primary-blue);
    border-radius: 0 8px 8px 0;
}

.section {
    margin-bottom: 16px;
}

.table {
    border: 2px solid rgba(30, 77, 139, 0.1);
    border-radius: 8px;
    margin: 16px 0;
    overflow: hidden;
}

.table table {
    width: 100%;
    border-collapse: collapse;
}

.table th, .table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid rgba(30, 77, 139, 0.1);
    color: var(--dark-gray);
}

.table th {
    background: var(--primary-blue);
    color: var(--white);
    font-weight: 600;
}

.code {
    background: #1e293b;
    color: #e2e8f0;
    border-radius: 12px;
    margin: 16px 0;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-medium);
    border: 1px solid rgba(30, 77, 139, 0.1);
}

.code pre {
    white-space: pre-wrap;
    overflow: auto;
    margin: 0;
    padding: 20px;
    font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
    font-size: 0.875rem;
    line-height: 1.5;
}

.code-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #334155;
    padding: 12px 20px;
    border-bottom: 1px solid #475569;
}

.code-header span {
    color: var(--light-blue);
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.copy-button {
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid var(--light-blue);
    color: var(--light-blue);
    cursor: pointer;
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 6px;
    transition: all 0.3s ease;
    font-weight: 500;
}

.copy-button:hover {
    background: var(--light-blue);
    color: var(--white);
    transform: translateY(-1px);
}

.typing {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.dot {
    width: 8px;
    height: 8px;
    margin: 0 4px;
    background: var(--primary-blue);
    border-radius: 50%;
    animation: blink 1.4s infinite both;
}

.dot:nth-child(1) {
    animation-delay: 0.2s;
}

.dot:nth-child(2) {
    animation-delay: 0.4s;
}

.dot:nth-child(3) {
    animation-delay: 0.6s;
}

@keyframes blink {
    0%, 80%, 100% {
        opacity: 0.3;
        transform: scale(0.8);
    }
    40% {
        opacity: 1;
        transform: scale(1.2);
    }
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .ai {
        max-width: 90%;
        padding: 16px;
        margin-bottom: 12px;
        font-size: 0.875rem;
    }
    
    .feedback {
        right: 12px;
        bottom: -12px;
        gap: 6px;
    }
    
    .feedback button {
        width: 32px;
        height: 32px;
        font-size: 14px;
    }
    
    .code pre {
        padding: 16px;
        font-size: 0.75rem;
    }
    
    .code-header {
        padding: 10px 16px;
    }
    
    .citations {
        font-size: 0.6875rem;
        padding: 10px;
        margin: 10px 0;
    }
}

@media (max-width: 480px) {
    .ai {
        max-width: 95%;
        padding: 12px;
    }
    
    .content {
        font-size: 0.8125rem;
    }
    
    .feedback button {
        width: 28px;
        height: 28px;
        font-size: 12px;
    }
}
</style>
