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
                updateProgressBar(data.current_amount, data.goal_amount);
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

    // Al pulsar el botón de donar
    donationForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const amount = parseFloat(document.getElementById('amount').value);
        
        fetch('/donate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `amount=${amount}`
        })
        .then(response => response.json())
        .then(data => {
            if(data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Errorea ordainketa prozesuan');
        });
    });

    // Cerrar el modal
    modalBtn.addEventListener('click', function() {
        resultModal.style.display = 'none';
    });
});