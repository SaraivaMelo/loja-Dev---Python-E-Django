function atualizarContadorCarrinho() {
    const badges = document.querySelectorAll('#carrinho-count, .carrinho-count-display');

    fetch("/produtos/carrinho/count/")
        .then(response => response.json())
        .then(data => {
            const total = data.quantidade;
            badges.forEach(badge => {
                if (total > 0) {
                    badge.textContent = total > 99 ? '99+' : total;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            });
        })
        .catch(error => {
            console.error('Erro ao buscar quantidade do carrinho:', error);
            badges.forEach(badge => {
                badge.style.display = 'none';
            });
        });
}

document.addEventListener('DOMContentLoaded', atualizarContadorCarrinho);