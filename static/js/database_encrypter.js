async function encryptCsv(databasePath) {
    if (databasePath) {
        const rsa_public_key = getRsaPublicKey();

        const response = await fetch(databasePath);
        console.log('Response:', response);
        const csvText = await response.text();
        const lines = csvText.split('\n');

        const encryptedLines = [];
        for (const line of lines) {
            if (line.trim() !== '') {
                const dataEncrypted = await dbEncryptString(line, rsa_public_key);
                encryptedLines.push(dataEncrypted);
            }
        }

        console.log('Encrypted CSV:', encryptedLines);

        // Converta as linhas criptografadas de volta para o formato CSV
        const encryptedCsv = encryptedLines.join('\n');

        // Envie o CSV criptografado para o servidor
        await fetch('/encrypter', {
            method: 'POST',
            headers: {
                'Content-Type': 'text/csv'
            },
            body: encryptedCsv
        });

        return encryptedLines;
    }
}

// Chame a função quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    const databasePath = document.getElementById('encryptedText').value;
    console.log('Database path:', databasePath);
    encryptCsv(databasePath);
});