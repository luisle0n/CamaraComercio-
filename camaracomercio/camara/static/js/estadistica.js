document.addEventListener('DOMContentLoaded', function() {
    // Estadística 1: Redes sociales más usadas
    if (window.estadistica1) {
        var ctx1 = document.getElementById('estadistica1').getContext('2d');
        new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: window.estadistica1.labels,
                datasets: [{
                    label: 'Cantidad de usuarios',
                    data: window.estadistica1.data,
                    backgroundColor: [
                        '#25D366', // WhatsApp
                        '#4267B2', // Facebook
                        '#E1306C', // Instagram
                        '#FF0000', // YouTube
                        '#010101'  // TikTok
                    ],
                    borderColor: [
                        '#25D366',
                        '#4267B2',
                        '#E1306C',
                        '#FF0000',
                        '#010101'
                    ],
                    borderWidth: 1
                }]
            },
            options: {responsive: true, plugins: {legend: {display: false}}}
        });
    }

    // Estadística 2
    if (window.estadistica2) {
        var ctx2 = document.getElementById('estadistica2').getContext('2d');
        new Chart(ctx2, {
            type: 'pie',
            data: {
                labels: window.estadistica2.labels,
                datasets: [{
                    label: window.estadistica2.label,
                    data: window.estadistica2.data,
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.7)',
                        'rgba(220, 53, 69, 0.7)',
                        'rgba(255, 193, 7, 0.7)'
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(220, 53, 69, 1)',
                        'rgba(255, 193, 7, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {responsive: true}
        });
    }
});
