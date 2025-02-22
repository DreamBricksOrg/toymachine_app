// Função para ocultar o botão quando o teclado do Android for exibido
function monitorarTeclado() {
    const botao = document.getElementById("submit-container");
    let alturaInicial = window.innerHeight;

    window.addEventListener("resize", () => {
        if (window.innerHeight < alturaInicial * 0.8) { // Se a altura diminuir significativamente
            botao.style.display = "none";
        } else {
            botao.style.display = "flex";
        }
    });
}

monitorarTeclado();


function openPopup() {
    document.getElementById("tos").style.display = "flex";
}

function closePopup() {
    document.getElementById("tos").style.display = "none";
}

window.onclick = function (event) {
    const modal = document.getElementById('tos');
    if (event.target === modal) {
        closePopup();
    }
};

document.getElementById('cpf').addEventListener('input', function(e) {
    var value = e.target.value;
    var cpfPattern = value.replace(/\D/g, '') // Remove qualquer coisa que não seja número
                            .replace(/(\d{3})(\d)/, '$1.$2') // Adiciona ponto após o terceiro dígito
                            .replace(/(\d{3})(\d)/, '$1.$2') // Adiciona ponto após o sexto dígito
                            .replace(/(\d{3})(\d)/, '$1-$2') // Adiciona traço após o nono dígito
                            .replace(/(-\d{2})\d+?$/, '$1'); // Impede entrada de mais de 11 dígitos
    e.target.value = cpfPattern;
    });
    document.getElementById('cellphone').addEventListener('input', function(e) {
    var value = e.target.value;
    var cellPattern = value.replace(/\D/g, '') // Remove qualquer coisa que não seja número
                            .replace(/(\d{0})(\d)/, '$1($2') // Adiciona ponto após o terceiro dígito
                            .replace(/(\d{2})(\d)/, '$1) $2') // Adiciona ponto após o sexto dígito
                            .replace(/(\d{5})(\d)/, '$1-$2') // Adiciona traço após o nono dígito
                            .replace(/(-\d{4})\d+?$/, '$1'); // Impede entrada de mais de 11 dígitos
    e.target.value = cellPattern;
});

document.getElementById("form").addEventListener("submit", function(event) {
    let toscheckbox = document.getElementById("toscheckbox");
    let checkbox = document.getElementById("termos");
    
    if (!toscheckbox.checked) {
        event.preventDefault(); // Impede o envio do formulário
        checkbox.style.color = "#ff5154";
        checkbox.style.border= "1px solid #ff5154";
        checkbox.style.backgroundColor = "#EBD8D0";
    } else {
        checkbox.style.color = "#1D1D1D";
        checkbox.style.border = "none";
        checkbox.style.backgroundColor = "none";
    }
});