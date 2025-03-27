let timeout;
let inactivityTime;

// Fetch inactivity time from server
function fetchInactivityTime() {
    return fetch('/file.json')
        .then(response => response.json())
        .then(data => {
            inactivityTime = data.inactivity_time;
            console.log('Inactivity time:', inactivityTime);
            resetTimer();
        })
        .catch(error => {
            console.error('Error fetching inactivity time:', error);
        });
}

function resetTimer() {
    if (!inactivityTime) return;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        window.location.href = '/';
    }, inactivityTime);
    console.log('Timer reset with:', inactivityTime);
}

// Eventos para detectar atividade do usuário
['click', 'mousemove', 'keypress', 'scroll', 'touchstart', 'input'].forEach(event => {
    window.addEventListener(event, resetTimer);
});

// Inicia o fetch
fetchInactivityTime();
