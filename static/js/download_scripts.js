const decryptText = async () => {
    try {
        const fileInput = document.getElementById("decript_key");
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Por favor, selecione o arquivo da chave privada.');
            return;
        }

        const reader = new FileReader();
        reader.onload = async (e) => {
            console.log('Private key loaded');
            const privateKey = e.target.result;
            
            try {
                // Fetch encrypted data from endpoint
                const response = await fetch('/encrypter');
                const encryptedText = await response.text();
                const encryptedLines = encryptedText.split('\n');
                console.log('Encrypted data loaded');
                console.log(encryptedLines);
                
                // Decrypt each line
                const decryptedLines = [];
                for (const line of encryptedLines) {
                    if (line.trim()) {
                        const decryptedLine = await dbDecryptString(line.trim(), privateKey);
                        decryptedLines.push(decryptedLine);
                    }
                }

                console.log('Decrypted data');
                console.log(decryptedLines);
                
                // Create CSV content
                const csvContent = [
                    ...decryptedLines
                ].join('\n');

                // Create and trigger download
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.setAttribute('href', url);
                link.setAttribute('download', 'dados_maquina.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
            } catch(err) {
                alert('Falha na descriptografia: Chave privada inválida ou dados corrompidos');
                console.error(err);
            }
        };
        
        reader.readAsText(file);
    } catch(err) {
        alert('Erro ao ler arquivo da chave privada');
        console.error(err);
    }
};