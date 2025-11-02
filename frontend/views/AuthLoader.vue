<template>
    <div class="loader-container">
        <div class="loader-content">
            <div class="brand-section">
                <div class="brand-logo">
                    <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect width="80" height="80" rx="20" fill="var(--primary-blue)"/>
                        <path d="M20 30h40v5H20v-5zm0 10h40v5H20v-5zm0 10h30v5H20v-5z" fill="white"/>
                    </svg>
                </div>
                <div class="brand-text">
                    <h1 class="brand-title">AJOVER</h1>
                    <p class="brand-subtitle">Asistente Virtual Corporativo</p>
                </div>
            </div>
            
            <div class="loading-section">
                <div class="spinner-container">
                    <div class="spinner"></div>
                    <div class="spinner-inner"></div>
                </div>
                <p class="loading-message">{{ message }}</p>
                <div class="loading-dots">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
            </div>
            
            <div class="footer-section">
                <p class="company-info">
                    Más de 60 años ofreciendo productos resistentes y livianos<br>
                    para la construcción de proyectos
                </p>
            </div>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    message: {
        type: String,
        required: true
    }
})
</script>

<style scoped>
.loader-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('/ajover-background.jpg') no-repeat center center/cover;
    background-attachment: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    transition: opacity 0.5s ease;
}

.loader-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(30, 77, 139, 0.1);
    z-index: 0;
}

.loader-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 40px;
    padding: 40px;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(15px);
    border-radius: 24px;
    box-shadow: var(--shadow-heavy);
    max-width: 400px;
    width: 90%;
    text-align: center;
    border: 2px solid rgba(30, 77, 139, 0.1);
    position: relative;
    z-index: 1;
}

.brand-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
}

.brand-logo {
    animation: logoFloat 3s ease-in-out infinite;
}

.brand-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--primary-blue);
    margin: 0;
    letter-spacing: 0.1em;
    text-shadow: 0 2px 4px rgba(30, 77, 139, 0.1);
}

.brand-subtitle {
    font-size: 0.875rem;
    color: var(--medium-gray);
    margin: 0;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.loading-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}

.spinner-container {
    position: relative;
    width: 60px;
    height: 60px;
}

.spinner {
    width: 60px;
    height: 60px;
    border: 4px solid rgba(30, 77, 139, 0.1);
    border-top-color: var(--primary-blue);
    border-radius: 50%;
    animation: spin 1.2s linear infinite;
}

.spinner-inner {
    position: absolute;
    top: 8px;
    left: 8px;
    width: 44px;
    height: 44px;
    border: 3px solid rgba(220, 38, 38, 0.2);
    border-top-color: var(--accent-red);
    border-radius: 50%;
    animation: spin 0.8s linear infinite reverse;
}

.loading-message {
    font-size: 1.125rem;
    color: var(--dark-gray);
    margin: 0;
    font-weight: 500;
}

.loading-dots {
    display: flex;
    gap: 8px;
}

.dot {
    width: 8px;
    height: 8px;
    background: var(--primary-blue);
    border-radius: 50%;
    animation: dotPulse 1.4s ease-in-out infinite;
}

.dot:nth-child(2) {
    animation-delay: 0.2s;
}

.dot:nth-child(3) {
    animation-delay: 0.4s;
}

.footer-section {
    border-top: 1px solid rgba(30, 77, 139, 0.1);
    padding-top: 20px;
}

.company-info {
    font-size: 0.875rem;
    color: var(--medium-gray);
    margin: 0;
    line-height: 1.5;
    font-weight: 400;
}

/* ANIMACIONES */
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@keyframes logoFloat {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-10px);
    }
}

@keyframes dotPulse {
    0%, 80%, 100% {
        transform: scale(0.8);
        opacity: 0.5;
    }
    40% {
        transform: scale(1.2);
        opacity: 1;
    }
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .loader-content {
        padding: 32px 24px;
        gap: 32px;
        max-width: 350px;
    }
    
    .brand-title {
        font-size: 2rem;
    }
    
    .brand-subtitle {
        font-size: 0.75rem;
    }
    
    .loading-message {
        font-size: 1rem;
    }
    
    .spinner-container {
        width: 50px;
        height: 50px;
    }
    
    .spinner {
        width: 50px;
        height: 50px;
    }
    
    .spinner-inner {
        top: 6px;
        left: 6px;
        width: 38px;
        height: 38px;
    }
}

@media (max-width: 480px) {
    .loader-content {
        padding: 24px 20px;
        gap: 24px;
        width: 95%;
    }
    
    .brand-title {
        font-size: 1.75rem;
    }
    
    .company-info {
        font-size: 0.75rem;
    }
}
</style>