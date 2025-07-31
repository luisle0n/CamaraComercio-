const FAQ_RESPONSES = {
    horarios: 'Nuestros horarios de atención son: Lunes a Viernes de 8:00 AM a 5:00 PM, Sábados de 8:00 AM a 12:00 PM.',
    servicios: 'Ofrecemos asesoría empresarial, capacitaciones, salas de reuniones, auditorio y más. ¿Te interesa algún servicio en particular?',
    convenios: 'Tenemos convenios con bancos, hoteles, consultorías, servicios gráficos y más. Visita la sección de convenios para ver todos los beneficios.',
    afiliacion: 'Para afiliarte, completa el formulario de registro empresarial, adjunta los documentos requeridos como comprobante de pago de 20,00$ y espera la aprobación. El proceso toma 5-7 días hábiles.',
    precios: 'Los precios varían según el servicio. Sala de reuniones: $25.000/2h, Auditorio: $80.000/4h, Asesoría: $45.000/h. ¿Necesitas información específica?',
    costo_afiliacion: 'La afiliación natural o jurídica tiene un costo de $20 dólares. Este valor es único por el proceso de afiliación.',
    reservas: 'Puedes hacer reservas desde tu panel de afiliado. Selecciona el servicio, fecha y hora disponible. Te llegará una confirmación por correo.',
    contacto: 'Puedes contactarnos al 07-2570123, por correo a info@ccl.org.ec o visitarnos en Av. Universitaria y Azuay, Loja.',
    eventos: 'Organizamos regularmente foros, ruedas de negocios, capacitaciones y seminarios. Consulta nuestra agenda de eventos.',
    emprendimiento: 'Apoyamos a emprendedores con asesoría, capacitaciones, networking y acceso a financiamiento. ¡Únete a nuestra comunidad emprendedora!',
    default: 'Hola! Soy el asistente virtual de la Cámara de Comercio de Loja. Puedo ayudarte con información sobre horarios, servicios, convenios, afiliación, precios, reservas, eventos y emprendimiento. ¿En qué puedo ayudarte?'
};

document.addEventListener('DOMContentLoaded', function() {
    var toggleBtn = document.getElementById('chatbot-toggle');
    var chatbotWindow = document.getElementById('chatbot-window');
    var closeBtn = document.getElementById('chatbot-close');
    var chatbotForm = document.getElementById('chatbot-form');
    var chatbotMessages = document.getElementById('chatbot-messages');
    var chatbotInput = document.getElementById('chatbot-input');

    // Solo inicializar si existen todos los elementos
    if (toggleBtn && chatbotWindow && closeBtn && chatbotForm && chatbotMessages && chatbotInput) {
        // Inicialmente oculto
        chatbotWindow.style.display = 'none';

        toggleBtn.addEventListener('click', function() {
            chatbotWindow.style.display = 'block';
            toggleBtn.style.display = 'none';
        });

        closeBtn.addEventListener('click', function() {
            chatbotWindow.style.display = 'none';
            toggleBtn.style.display = 'block';
        });

        // Mensaje de bienvenida solo si no existe ya
        if (!chatbotMessages.querySelector('.chat-message-bubble.bot')) {
            addChatMessage('¡Hola! Soy el asistente virtual de la Cámara de Comercio de Loja. ¿En qué puedo ayudarte hoy?', 'bot');
        }

        // Enviar mensaje con Enter
        chatbotInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatbotForm.dispatchEvent(new Event('submit'));
            }
        });

        // Enviar mensaje
        chatbotForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var mensaje = chatbotInput.value.trim();
            if (!mensaje) return;
            addChatMessage(mensaje, 'user');
            chatbotInput.value = '';
            showTyping();
            setTimeout(function() {
                hideTyping();
                var respuesta = getBotResponse(mensaje);
                addChatMessage(respuesta, 'bot');
            }, 900);
        });
    }

    function addChatMessage(message, sender) {
        var div = document.createElement('div');
        div.className = 'chat-message-bubble ' + sender;
        // Alineación derecha para usuario, izquierda para bot
        div.style.display = 'flex';
        div.style.flexDirection = 'column';
        div.style.alignItems = sender === 'user' ? 'flex-end' : 'flex-start';
        var hora = new Date().toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit' });
        div.innerHTML = `
            <div class="bubble-content">
                <span>${message}</span>
                <div class="bubble-meta"><small>${sender === 'bot' ? 'Bot' : 'Tú'} · ${hora}</small></div>
            </div>
        `;
        chatbotMessages.appendChild(div);
        setTimeout(function() {
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }, 50);
    }

window.showTyping = function() {
    var chatbotMessages = document.getElementById('chatbot-messages');
    if (!document.getElementById('typing-indicator') && chatbotMessages) {
        var div = document.createElement('div');
        div.id = 'typing-indicator';
        div.className = 'chat-message-bubble bot';
        div.innerHTML = `<div class="bubble-content"><span><em>Escribiendo...</em></span></div>`;
        chatbotMessages.appendChild(div);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
}

window.hideTyping = function() {
    var typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) typingDiv.remove();
}

// Definir la función global ANTES del DOMContentLoaded
window.getBotResponse = function(message) {
    var lower = message.toLowerCase();
    if (lower.includes('horario') || lower.includes('hora')) return FAQ_RESPONSES.horarios;
    if (lower.includes('servicio') || lower.includes('sala') || lower.includes('auditorio')) return FAQ_RESPONSES.servicios;
    if (lower.includes('convenio') || lower.includes('descuento') || lower.includes('beneficio')) return FAQ_RESPONSES.convenios;
    if (lower.includes('afiliaci') || lower.includes('registro') || lower.includes('inscribi')) return FAQ_RESPONSES.afiliacion;
    if (lower.includes('costo de afiliacion') || lower.includes('costo afiliacion') || lower.includes('valor afiliacion') || lower.includes('afiliacion cuesta') || lower.includes('afiliacion vale') || lower.includes('afiliacion precio')) return FAQ_RESPONSES.costo_afiliacion;
    if (lower.includes('precio') || lower.includes('costo') || lower.includes('tarifa')) return FAQ_RESPONSES.precios;
    if (lower.includes('reserva') || lower.includes('apartar') || lower.includes('reservar')) return FAQ_RESPONSES.reservas;
    if (lower.includes('contacto') || lower.includes('teléfono') || lower.includes('dirección')) return FAQ_RESPONSES.contacto;
    if (lower.includes('evento') || lower.includes('capacitaci') || lower.includes('seminario')) return FAQ_RESPONSES.eventos;
    if (lower.includes('emprend') || lower.includes('negocio') || lower.includes('startup')) return FAQ_RESPONSES.emprendimiento;
    if (lower.includes('hola') || lower.includes('ayuda') || lower.includes('info')) return FAQ_RESPONSES.default;
    return 'No estoy seguro de cómo ayudarte con eso. Puedo ayudarte con información sobre: horarios, servicios, convenios, afiliación, precios, reservas, eventos, costo de afiliacion, emprendimiento y contacto. ¿Sobre qué te gustaría saber?';
}
});

