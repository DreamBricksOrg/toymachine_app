let timeout;

function resetTimer() {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        window.location.href = '/';
    }, 45000); // 45 segundos (45000 ms)
}

// Eventos para detectar atividade do usuário
['click', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
    window.addEventListener(event, resetTimer);
});

// Inicializa o temporizador ao carregar a página
resetTimer();
