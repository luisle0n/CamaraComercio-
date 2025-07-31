// Funciones principales del sitio
document.addEventListener('DOMContentLoaded', function() {
    // Eliminar inicialización duplicada del chatbot para evitar errores en vistas públicas
    
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Animaciones al hacer scroll
    initScrollAnimations();
    
    // Validación de formularios
    initFormValidation();
});

// Chatbot functionality
function initChatbot() {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotInput = document.getElementById('chatbot-input');
    
    if (!chatbotToggle || !chatbotWindow) return;
    
    // Toggle chatbot window
    chatbotToggle.addEventListener('click', function() {
        chatbotWindow.style.display = chatbotWindow.style.display === 'none' || 
                                     chatbotWindow.style.display === '' ? 'block' : 'none';
    });
    
    // Close chatbot
    if (chatbotClose) {
        chatbotClose.addEventListener('click', function() {
            chatbotWindow.style.display = 'none';
        });
    }
    
    // Handle chatbot form submission
    if (chatbotForm) {
        chatbotForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const mensaje = chatbotInput.value.trim();
            if (!mensaje) return;
            
            // Add user message
            addChatMessage(mensaje, 'user');
            
            // Clear input
            chatbotInput.value = '';
            
            // Usar solo el JS local para responder
            if (typeof getBotResponse === 'function') {
                showTyping && showTyping();
                setTimeout(function() {
                    hideTyping && hideTyping();
                    var respuesta = getBotResponse(mensaje);
                    addChatMessage(respuesta, 'bot');
                }, 900);
            } else {
                addChatMessage('No se pudo procesar la respuesta. Consulta con soporte.', 'bot');
            }
        });
    }
    
    // Welcome message
    if (chatbotMessages) {
        addChatMessage('¡Hola! Soy el asistente virtual de la Cámara de Comercio de Loja. ¿En qué puedo ayudarte?', 'bot');
    }
}

function addChatMessage(message, sender) {
    const chatbotMessages = document.getElementById('chatbot-messages');
    if (!chatbotMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = message;
    
    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

// Get CSRF token for AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Scroll animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Confirm delete action
function confirmDelete(message = '¿Estás seguro de que quieres eliminar este elemento?') {
    return confirm(message);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-EC', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('es-EC', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchResults) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
}

function performSearch(query) {
    // Implementar búsqueda según necesidades
    console.log('Searching for:', query);
}

// Print functionality
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const printWindow = window.open('', '', 'width=800,height=600');
    printWindow.document.write(`
        <html>
            <head>
                <title>Imprimir</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .no-print { display: none; }
                </style>
            </head>
            <body>
                ${element.innerHTML}
            </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
    printWindow.close();
}

// Export data
function exportData(data, filename, type = 'csv') {
    const blob = new Blob([data], { type: `text/${type}` });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Load more content (pagination)
function loadMoreContent(url, container) {
    fetch(url)
        .then(response => response.text())
        .then(html => {
            document.getElementById(container).innerHTML += html;
        })
        .catch(error => {
            console.error('Error loading content:', error);
            showNotification('Error al cargar el contenido', 'danger');
        });
}

// Image lazy loading
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize all functionality
function initAll() {
    initChatbot();
    initScrollAnimations();
    initFormValidation();
    initSearch();
    initLazyLoading();
}

// Call init on page load
document.addEventListener('DOMContentLoaded', initAll);