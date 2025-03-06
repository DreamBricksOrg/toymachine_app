const decryptText = async () => {
    try {
        // Get the file input and read the .pem file
        const fileInput = document.getElementById("decript_key");
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Please select a private key file.');
            return;
        }

        // Read file content
        const reader = new FileReader();
        reader.onload = async (e) => {
            const privateKey = e.target.result;
            const encryptedString = document.getElementById("encryptedText").value;

            console.log('Private key:', privateKey);
            console.log('Encrypted data:', encryptedString);
            console.log('Public key:', rsa_public_key_str);

            try {
                const decryptedString = await dbDecryptString(encryptedString, privateKey);
                console.log('Decrypted data:', decryptedString);
                // TODO: Add logic to display or download decrypted data
            } catch(err) {
                alert('Decryption failed: Invalid private key or corrupted data');
                console.error(err);
            }
        };
        
        reader.readAsText(file);
    } catch(err) {
        alert('Error reading private key file');
        console.error(err);
    }
};