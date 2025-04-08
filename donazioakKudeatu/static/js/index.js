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
    
    donationForm.addEventListener('submit', function(e) {
        e.preventDefault();       
        
        
        document.getElementById('enviar-btn').addEventListener('click', function() {
            let amount = parseFloat(document.getElementById('amount').value);            
            fetch('/donate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': '{{ csrf_token }}'  //Django necesita esto para POST
                },
                body: `amount=${amount}`
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('respuesta').textContent = data.mensaje || data.error;
            });
        });
        
        // Simular envío a RedSys (en un caso real sería una petición AJAX)
        setTimeout(() => {
            // Simular respuesta aleatoria de RedSys (éxito o error)
            const isSuccess = Math.random() > 0.2; // 80% de probabilidad de éxito
            
            if (isSuccess) {
                // Éxito en el pago
                modalTitle.textContent = '¡Donación exitosa!';
                modalMessage.textContent = `Gracias por tu donación de ${amount}€. Tu contribución nos ayuda a seguir con nuestra labor.`;
                modalMessage.className = 'modal-message success';
                
                // Actualizar el progreso (en un caso real esto vendría del backend)
                currentAmount += amount;
                updateProgressBar(currentAmount, goalAmount);
            } else {
                // Error en el pago
                modalTitle.textContent = 'Error en el pago';
                modalMessage.textContent = 'Hubo un problema al procesar tu donación. Por favor, intenta nuevamente o usa otro método de pago.';
                modalMessage.className = 'modal-message error';
            }
            
            // Mostrar el modal
            resultModal.style.display = 'flex';
            
            // Resetear el formulario
            donationForm.reset();
        }, 1500);
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