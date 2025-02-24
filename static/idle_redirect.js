let timeout;

function resetTimer() {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        window.location.href = '/';
    }, 15000); // 15 segundos (15000 ms)
}

// Eventos para detectar atividade do usuário
['click', 'mousemove', 'keypress', 'scroll', 'touchstart', 'input'].forEach(event => {
    window.addEventListener(event, resetTimer);
});

// Inicializa o temporizador ao carregar a página
resetTimer();
