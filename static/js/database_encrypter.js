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
                
                // Create JSON payload
                const currentDate = new Date().toISOString();
                const logData = {
                    status: "JOGOU",
                    project: "67d358c732f32712b51c5aeb",
                    additional: dataEncrypted,
                    timePlayed: currentDate
                };

                // Send log data
                const logserverUploadResponse = await fetch('/encris', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(logData)
                });

                encryptedLines.push(dataEncrypted);
            }
        }

        console.log('Encrypted CSV:', encryptedLines);

        // Create CSV file from encrypted lines
        const encryptedCsv = encryptedLines.join('\n');
        const blob = new Blob([encryptedCsv], { type: 'text/csv' });
        const file = new File([blob], 'dados_encrypted.csv', { type: 'text/csv' });

        // Create FormData and append file
        const formData = new FormData();
        formData.append('file', file);

        // Send encrypted CSV as file
        const uploadResponse = await fetch('/encrypter', {
            method: 'POST',
            body: formData
        });

        if (uploadResponse.ok) {
            console.log('File uploaded successfully');
        } else {
            console.error('Upload failed:', uploadResponse.statusText);
        }

        return encryptedLines;
    }
}

// Chame a função quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    const databasePath = document.getElementById('encryptedText').value;
    console.log('Database path:', databasePath);
    encryptCsv(databasePath);
});