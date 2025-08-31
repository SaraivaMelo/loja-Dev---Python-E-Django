document.getElementById('cep').addEventListener('blur', function() {
    const cep = this.value.replace(/\D/g, ''); // remove caracteres não numéricos

    if (cep.length === 8) {
        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => response.json())
            .then(data => {
                if (!data.erro) {
                    document.getElementById('street').value = data.logradouro;
                    document.getElementById('neighborhood').value = data.bairro;
                    document.getElementById('city').value = data.localidade;
                    document.getElementById('state').value = data.uf;
                } else {
                    alert('CEP não encontrado.');
                }
            })
            .catch(error => {
                alert('Erro ao buscar o CEP.');
                console.error(error);
            });
    } else {
        alert('CEP inválido');
    }
});
