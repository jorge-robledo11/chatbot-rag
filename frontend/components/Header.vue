<script setup>
import { ref } from 'vue'
import { sharedState } from '../state'

const emit = defineEmits(['clean'])

const cleanMessage = () => {
    emit('clean')
}
</script>

<template>
    <div class="header-container">
        <div class="header-brand">
            <div class="brand-logo">
                <img src="/assets/logo_ajover.png" alt="Logo Ajover" class="ajover-logo" />
            </div>
            <div class="brand-text">
                <h2 class="brand-title">Chat Ajover</h2>
                <p class="brand-subtitle">Asistente Virtual Corporativo</p>
            </div>
        </div>
        
        <div class="header-welcome">
            <div class="welcome-message">
                <span class="greeting">¡Hola</span>
                <strong class="user-name">{{ sharedState.name }}</strong>!
            </div>
            <p class="welcome-description">
                Estás usando el asistente virtual de 
                <a href="https://www.ajover.com/" target="_blank" class="company-link">
                    <strong>Ajover</strong>
                </a>
                . Estoy aquí para ayudarte con información sobre nuestros productos y servicios.
            </p>
        </div>
        
        <div class="header-actions">
            <button class="action-btn clean-btn" @click="cleanMessage" title="Limpiar conversación">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M2 4h12M5.333 4V2.667a1.333 1.333 0 011.334-1.334h2.666a1.333 1.333 0 011.334 1.334V4M7.333 7.333v4M8.667 7.333v4M3.333 4h9.334l-.667 8a1.333 1.333 0 01-1.333 1.333H5.333A1.333 1.333 0 014 12.667L3.333 4z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="btn-text">Limpiar</span>
            </button>
        </div>
    </div>
</template>

<style scoped>
.header-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(30, 77, 139, 0.1);
    position: relative;
}

.header-container::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 20px;
    right: 20px;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, var(--accent-red) 30%, var(--primary-blue) 70%, transparent 100%);
}

.header-brand {
    display: flex;
    align-items: center;
    gap: 16px;
}

.brand-logo {
    flex-shrink: 0;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--white);
    border-radius: 12px;
    padding: 8px;
    border: 1px solid rgba(30, 77, 139, 0.1);
    box-shadow: var(--shadow-light);
}

.ajover-logo {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.brand-text {
    flex: 1;
}

.brand-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-blue);
    margin: 0;
    line-height: 1.2;
}

.brand-subtitle {
    font-size: 0.75rem;
    color: var(--medium-gray);
    margin: 0;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.header-welcome {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.welcome-message {
    display: flex;
    align-items: baseline;
    gap: 6px;
    flex-wrap: wrap;
}

.greeting {
    font-size: 1rem;
    color: var(--dark-gray);
    font-weight: 400;
}

.user-name {
    font-size: 1rem;
    color: var(--primary-blue);
    font-weight: 600;
}

.welcome-description {
    font-size: 0.875rem;
    color: var(--medium-gray);
    line-height: 1.5;
    margin: 0;
}

.company-link {
    color: var(--primary-blue);
    font-weight: 600;
    text-decoration: none;
    position: relative;
    transition: color 0.3s ease;
}

.company-link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent-red);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.company-link:hover {
    color: var(--accent-red);
}

.company-link:hover::after {
    transform: scaleX(1);
}

.header-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
}

.action-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 500;
    transition: all 0.3s ease;
    cursor: pointer;
}

.clean-btn {
    color: var(--medium-gray);
    background: transparent;
    border: 1px solid rgba(107, 114, 128, 0.3);
}

.clean-btn:hover {
    color: var(--accent-red);
    background: rgba(220, 38, 38, 0.05);
    border-color: var(--accent-red);
    transform: translateY(-1px);
}

.btn-text {
    font-size: 0.75rem;
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .header-container {
        padding: 16px;
        gap: 12px;
    }
    
    .brand-logo {
        width: 40px;
        height: 40px;
        padding: 6px;
    }
    
    .brand-title {
        font-size: 1.25rem;
    }
    
    .brand-subtitle {
        font-size: 0.625rem;
    }
    
    .welcome-message {
        font-size: 0.875rem;
    }
    
    .welcome-description {
        font-size: 0.75rem;
    }
    
    .header-actions {
        justify-content: center;
    }
    
    .action-btn {
        padding: 6px 10px;
    }
    
    .btn-text {
        display: none;
    }
}

@media (max-width: 480px) {
    .header-brand {
        flex-direction: column;
        align-items: center;
        gap: 12px;
        text-align: center;
    }
    
    .brand-logo {
        width: 56px;
        height: 56px;
        padding: 8px;
    }
    
    .welcome-message {
        flex-direction: column;
        gap: 2px;
        align-items: center;
        text-align: center;
    }
    
    .welcome-description {
        text-align: center;
    }
}
</style>