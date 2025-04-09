document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const donationForm = document.getElementById('donationForm');
    const resultModal = document.getElementById('resultModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalBtn = document.getElementById('modalBtn');
    
    // Función para obtener el token CSRF
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

    // Cargar progreso inicial
    fetchProgress();

    // Actualizar cada 30 segundos
    setInterval(fetchProgress, 30000);

    // Obtener datos del progreso desde Django
    function fetchProgress() {
        fetch('/campaign-progress/')
            .then(response => {
                if (!response.ok) throw new Error('Error en la red');
                return response.json();
            })
            .then(data => {
                updateProgressBar(data.total_raised, data.campaign_goal);
            })
            .catch(error => {
                console.error('Error al cargar el progreso:', error);
                alert('Oraintxe ezin da ikusi zenbait diru donatu den');
            });
    }

    // Función para actualizar la barra de progreso
    function updateProgressBar(current, goal) {
        const percentage = Math.min((current / goal) * 100, 100);
        const progressFill = document.getElementById('progressFill');
        const currentAmountElement = document.getElementById('currentAmount');
        const goalAmountElement = document.getElementById('goalAmount');
        
        progressFill.style.width = `${percentage}%`;
        progressFill.textContent = `${Math.round(percentage)}%`;
        currentAmountElement.textContent = current.toLocaleString('es-ES');
        goalAmountElement.textContent = goal.toLocaleString('es-ES');
    }

    // Valida el formulario antes de enviar
    document.getElementById('donationForm').addEventListener('submit', (e) => {
        const amount = parseFloat(e.target.amount.value);
        if (amount < 1) {
            e.preventDefault();
            alert('La cantidad mínima es 1€');
        }
    });
});