let sniffer = null;
let previousStatus = null; // Para armazenar o valor anterior da chave "status"

// Função para verificar alterações no JSON
async function checkForStatusUpdates() {
    try {
        const response = await fetch('/file.json', {
            cache: 'no-cache' // Garante que a resposta não será armazenada em cache             
        });

        console.log(response)

        if (!response.ok) {
            console.error('Erro ao buscar o JSON:', response.statusText);
            return;
        }

        const currentData = await response.json();

        // Verifica se a chave "status" existe no JSON
        if (!currentData.hasOwnProperty('status')) {
            console.error('A chave "status" não foi encontrada no JSON.');
            return;
        }

        const currentStatus = currentData.status;

        // Verifica se o valor da chave "status" é 0 ou 1
        if (currentStatus !== 0) {
            console.error('O valor de "status" é:', currentStatus);
            window.location.href = '/timer';
        }
    } catch (error) {
        console.error('Erro ao verificar o JSON:', error);
    }
}

let intervalID = setInterval(checkForStatusUpdates, 250);

async function fetchLastLineFromCSV() {
    try {
        // Faz a requisição para o endpoint /dados.csv
        const response = await fetch('/dados.csv', {
            cache: 'no-cache' // Garante que a resposta não será armazenada em cache
        });

        if (!response.ok) {
            console.error('Erro ao buscar o arquivo CSV:', response.statusText);
            return null;
        }

        // Obtém o conteúdo do CSV como texto
        const csvText = await response.text();

        // Divide o conteúdo em linhas e obtém a última linha não vazia
        const lines = csvText.split('\n').filter(line => line.trim() !== '');
        const lastLine = lines[lines.length - 1];

        console.log('Última linha do CSV:', lastLine);
        return lastLine;
    } catch (error) {
        console.error('Erro ao buscar a última linha do CSV:', error);
        return null;
    }
}

async function encryptAndSendLastLine() {
    
    // Obtém a última linha do CSV
    const line = await fetchLastLineFromCSV();
    if (!line) {
        console.error('Nenhuma linha válida encontrada no CSV.');
        return;
    }

    // Encripta a linha usando a chave pública RSA
    const rsa_public_key = getRsaPublicKey();
    const dataEncrypted = await dbEncryptString(line, rsa_public_key);

    // Cria o payload para o POST
    const payload = new FormData();
    payload.append('line', dataEncrypted);

    console.log('Linha encriptada:', dataEncrypted);

    try {
        // Faz o POST no endpoint /encrypter
        const response = await fetch('/encrypter', {
            method: 'POST',
            body: payload
        });

        if (response.ok) {
            console.log('Linha encriptada enviada com sucesso:', dataEncrypted);
        } else {
            console.error('Erro ao enviar a linha encriptada:', response.statusText);
        }
    } catch (error) {
        console.error('Erro na requisição de salvamento:', error);
    }
}

// Chama a função para buscar, encriptar e enviar a última linha do CSV
encryptAndSendLastLine();
// Chama a função para verificar atualizações no JSON
checkForStatusUpdates();