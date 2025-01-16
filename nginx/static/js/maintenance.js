document.addEventListener('DOMContentLoaded', function() {
    const countdownElement = document.getElementById('countdown');
    let timeLeft = 30; // minutos

    function updateCountdown() {
        countdownElement.textContent = timeLeft;
        if (timeLeft <= 0) {
            window.location.reload();
        }
        timeLeft--;
    }

    setInterval(updateCountdown, 60000); // Actualizar cada minuto
});