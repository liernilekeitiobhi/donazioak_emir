document.addEventListener('DOMContentLoaded', function() {
    // Simular datos de progreso (en un caso real esto vendría del backend)
    const goalAmount = 12000;
    let currentAmount = 4500; // Esto normalmente vendría de la base de datos o de RedSys
    
    // Actualizar la barra de progreso
    updateProgressBar(currentAmount, goalAmount);
    
    // Manejar el envío del formulario
    const donationForm = document.getElementById('donationForm');
    const resultModal = document.getElementById('resultModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalBtn = document.getElementById('modalBtn');
    
    // Al pulsar el botón de donar
    document.getElementById('donationForm').addEventListener('submit', function(e) {
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
                // Redirigir al TPV Virtual de Redsys
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
    
    // Función para actualizar la barra de progreso
    function updateProgressBar(current, goal) {
        const percentage = Math.min((current / goal) * 100, 100);
        const progressFill = document.getElementById('progressFill');
        const currentAmountElement = document.getElementById('currentAmount');
        
        progressFill.style.width = `${percentage}%`;
        progressFill.textContent = `${Math.round(percentage)}%`;
        currentAmountElement.textContent = current.toLocaleString();
    }
});