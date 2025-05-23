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
        closeLoadingPopup();
    }
};

function errorHighlight(form_error) {
    console.log("Erro recebido: " + form_error);
    let cpfelement = document.getElementById("cpf-container");
    let cellphoneelement = document.getElementById("cellphone-container");
    let email = document.getElementById("email-container");
    let nameElement = document.getElementById("user-container");

    if (form_error === "CPF") {
        cpfelement.style.border = "1px solid #F44336";
        cpfelement.style.backgroundColor = "#FFCDD2";
    } else if (form_error === "Celular") {
        cellphoneelement.style.border = "1px solid #F44336";
        cellphoneelement.style.backgroundColor = "#FFCDD2";
    } else if (form_error === "Email") {
        email.style.border = "1px solid #F44336";
        email.style.backgroundColor = "#FFCDD2";
    } else if (form_error === "Nome") {
        nameElement.style.border = "1px solid #F44336";
        nameElement.style.backgroundColor = "#FFCDD2";
    }
    
}

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

const nameContainer = document.getElementById("user-container");
const emailContainer = document.getElementById("email-container");
const cellphoneContainer = document.getElementById("cellphone-container");
const cpfContainer = document.getElementById("cpf-container");
const emailInput = document.getElementById("email");
const emailButtons = document.querySelector(".email-buttons");
const nextFieldButton = document.getElementById('next-button');
const cellphoneInput = document.getElementById('cellphone');
const cpfInput = document.getElementById('cpf');
let nextField = document.getElementById('cellphone');

let isFocusing = false;

// Exibir botões ao clicar no input de email
emailInput.addEventListener("focus", function() {
    emailButtons.style.display = "flex";
    nextFieldButton.style.display = "flex";
    nextField = cellphoneInput;
});

// Ocultar nome e email ao clicar no input de WhatsApp
cellphoneInput.addEventListener("focus", function() {
    nextFieldButton.style.display = "flex";
    nextFieldButton.style.top = "190px"
    nameContainer.style.display = "none";
    emailContainer.style.display = "none";
    nextField = cpfInput;
    isFocusing = true;
});

// Exibir botões ao clicar no input de WhatsApp
cpfInput.addEventListener("focus", function() {
    nextFieldButton.style.display = "none";
    nameContainer.style.display = "none";
    emailContainer.style.display = "none";
    // cellphoneContainer.style.display = "none";
});

// Exibir botões ao digitar
emailInput.addEventListener("input", function() {
        emailButtons.style.display = "flex";
        nextFieldButton.style.display = "flex";
});

// Ocultar botões ao clicar fora
emailInput.addEventListener("focusout", function() {
    setTimeout(() => {
        emailButtons.style.display = "none";
        nextFieldButton.style.display = "none";
    }, 100);
});

cellphoneInput.addEventListener("focusout", function() {
    setTimeout(() => {
        if (!isFocusing) {
            nameContainer.style.display = "flex";
            emailContainer.style.display = "flex";
            nextFieldButton.style.display = "none";
        }
    }, 100);
});

cpfInput.addEventListener("focusout", function() {
    setTimeout(() => {
        nameContainer.style.display = "flex";
        emailContainer.style.display = "flex";
        cellphoneContainer.style.display = "flex";
        nextFieldButton.style.display = "none";
    }, 100);
});

// Função para focar no próximo campo
nextFieldButton.addEventListener('click', function() {
    if (cellphoneInput.value.length > 0) {
        cpfInput.focus();
    } else if (emailInput.value.length > 0) {
        cellphoneInput.focus();
    }
    emailButtons.style.display = "none";
    nextFieldButton.style.display = "none";
});

// Adicionar domínio ao e-mail
function addEmailDomain(domain) {
    if (!emailInput.value.includes("@")) {
        emailInput.value += domain;
    } else if (emailInput.value.includes("@")) {
        const parts = emailInput.value.split("@");
        console.log(parts[0]);
        console.log(parts[1]);
        emailInput.value = parts[0] + domain;
    }
    emailButtons.style.display = "none";
}


async function openLoadingPopup(event) {
    event.preventDefault(); // Temporarily prevent form submission
    document.getElementById("loading").style.display = "flex";

    let protectChecked = false;
    let toscheckbox = document.getElementById("toscheckbox");
    let protectcheckboxes = document.querySelectorAll("input[id='protecoes']");
    let checkbox = document.getElementById("termos");
    let protectContainer = document.getElementById("servicos-container");
    // let protectChecked = false;

    protectcheckboxes.forEach(function(checkbox) {
        if (checkbox.checked) {
            protectChecked = true;
        }
    });

    if (!protectChecked && !toscheckbox.checked) {
        checkbox.style.color = "#F44336";
        checkbox.style.border = "1px solid #F44336";
        checkbox.style.backgroundColor = "#FFCDD2";
        protectContainer.style.color = "#F44336";
        protectContainer.style.border = "1px solid #F44336";
        protectContainer.style.backgroundColor = "#FFCDD2";
        document.querySelectorAll(".checkbox-label").forEach(function(label) {
            label.style.color = "#F44336";
        });
        document.getElementById("loading").style.display = "none";
    } else if (!protectChecked) {
        protectContainer.style.color = "#F44336";
        protectContainer.style.border = "1px solid #F44336";
        protectContainer.style.backgroundColor = "#FFCDD2";
        document.querySelectorAll(".checkbox-label").forEach(function(label) {
            label.style.color = "#F44336";
        });
        document.getElementById("loading").style.display = "none";
    } else if (!toscheckbox.checked) {
        checkbox.style.color = "#F44336";
        checkbox.style.border = "1px solid #F44336";
        checkbox.style.backgroundColor = "#FFCDD2";
        document.getElementById("loading").style.display = "none";
    } else {
        checkbox.style.color = "#1D1D1D";
        checkbox.style.border = "none";
        checkbox.style.backgroundColor = "none";
        document.querySelectorAll(".checkbox-label").forEach(function(label) {
            label.style.color = "#1D1D1D";
        });

        setTimeout(() => {
            document.getElementById("form").submit();
        }, 750); // Change the delay to 1 second
    }
    
}
