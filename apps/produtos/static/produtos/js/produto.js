document.addEventListener("DOMContentLoaded", function () {
    const alertBox = document.querySelector(".custom-alert");
    const closeBtn = document.querySelector(".close-btn");

    if (alertBox && closeBtn) {
        closeBtn.addEventListener("click", function () {
            alertBox.classList.add("hide");
        });

        setTimeout(function () {
            alertBox.classList.add("hide");
        }, 3000);
    }
});


// Funcionalidade do carrinho para adicionar o produto 
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('form-adicionar-carrinho');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const url = form.dataset.url;
      const urlFinalizar = form.dataset.urlFinalizar;
      const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: ''
      })
        .then(async response => {
          const contentType = response.headers.get("content-type");
          if (response.ok && contentType && contentType.includes("application/json")) {
            return await response.json();
          } else {
            const errorText = await response.text();
            console.error("Erro na resposta:", errorText);
            throw new Error("Resposta inválida do servidor.");
          }
        })
        .then(data => {
          renderCarrinho(data, urlFinalizar, csrfToken)
           atualizarContadorCarrinho();
        })
        .catch(error => {
          console.error('Erro ao adicionar ao carrinho:', error.message);
        });
    });
  }

  function renderCarrinho(data, urlFinalizar, csrfToken) {
    const carrinhoDiv = document.getElementById('carrinho-itens');
    let html = '';

    if (data.produtos.length > 0) {
      html += '<ul class="list-group align-items-center">';
      data.produtos.forEach(produto => {
        html += `
          <li class="list-group-item d-flex justify-content-between align-items-center list_itens_kart">
            ${produto.name}
            <div>
              <span class="me-2">R$ ${produto.price}</span>
              <button class="btn btn-danger btn-sm btn-remover" data-id="${produto.id}">X</button>
            </div>
          </li>
        `;
      });
      html += '</ul>';
      html += `
        <a href="${urlFinalizar}" class="btn btn-primary mt-3 w-100">Finalizar Compra</a>
      `;
    } else {
      html = '<h6>Seu carrinho está vazio.</h6>';
    }

    carrinhoDiv.innerHTML = html;

    // Adiciona eventos de click nos botões de remover
    document.querySelectorAll('.btn-remover').forEach(botao => {
      botao.addEventListener('click', function () {
        const idProduto = this.dataset.id;

        fetch(`/produtos/remover/${idProduto}`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        })
          .then(res => res.json())
          .then(data => {
            renderCarrinho(data, urlFinalizar, csrfToken);
            atualizarContadorCarrinho();
          })
          .catch(error => {
            console.error('Erro ao remover item:', error.message);
          });
      });
    });
  }

  // Executa ao carregar a página (sem precisar clicar)
const carrinhoDiv = document.getElementById('carrinho-itens');
    if (carrinhoDiv) {
      const urlDetalhado = "/produtos/carrinho/detalhado/";
      const urlFinalizar = "/produtos/finalizar/"; // ou pegue via dataset
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

      fetch(urlDetalhado, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      })
        .then(res => res.json())
        .then(data => {
          if (data.produtos && data.produtos.length > 0) {
            renderCarrinho(data, urlFinalizar, csrfToken);
          }
        });
    }


});


// CONFIGURAÇÕES DO PAGAMENTO 

document.addEventListener('DOMContentLoaded', function () {
    // Captura os pontos diretamente da renderização do template
    let pontos = document.getElementById('pontuacao_atual').innerText
    console.log(pontos)
    const pontosCliente = parseInt(pontos);

    // Referência ao input do tipo "pontuação"
    const inputPontos = document.getElementById('pg_pontos');

    // Se o cliente tem pontos maiores que zero, remove o disabled
    if (pontosCliente > 0 && inputPontos) {
        inputPontos.removeAttribute('disabled');
    }

});

// Finalizar compra e realizar pagamento 
document.addEventListener('DOMContentLoaded', function () {
  // Elementos
  const btnCupom = document.getElementById('btn_cupom');
  const cupomInput = document.getElementById('cupom');
  const totalPgElement = document.getElementById('total_pg');
  const descontoElement = document.querySelector('.description_pg .text-success');
  const valorTotalElement = document.querySelector('.description_pg .text-primary');
  const form = document.querySelector('form');

  // Inputs ocultos para poder mandar a tela de pagar
  const descontoHidden = document.getElementById('desconto_aplicado_hidden');
  const totalHidden = document.getElementById('total_com_desconto');

  // Função de cálculo para aplicar descontos
  function aplicarCupom() {
    const cupom = cupomInput.value.trim().toUpperCase();
    const totalText = totalPgElement.innerText;
    const totalNumber = parseFloat(totalText.replace(/[^\d,.-]/g, '').replace(',', '.'));

    let desconto = 0;

    switch (cupom) {
      case "DEV10":
        desconto = totalNumber * 0.10;
        break;
      case "DEV20":
        desconto = totalNumber * 0.20;
        break;
      case "DEV30":
        desconto = totalNumber * 0.30;
        break;
      default:
        desconto = 0;
    }

    const novoTotal = totalNumber - desconto;

    // Atualizar a tela
    descontoElement.innerText = `R$ ${desconto.toFixed(2)}`;
    valorTotalElement.innerText = `R$ ${novoTotal.toFixed(2)}`;

    // Atualizar inputs ocultos 
      descontoHidden.value = desconto.toFixed(2);
      totalHidden.value = novoTotal.toFixed(2);
  }

  // Botão aplicar cupom
  btnCupom.addEventListener('click', aplicarCupom);

  // Quando o formulário for enviado (clicar em "Finalizar")
  form.addEventListener('submit', aplicarCupom);
});

document.querySelectorAll('input[name="flexRadioDefault"]').forEach(function (radio) {
  radio.addEventListener('change', function () {
    const formaSelecionada = this.value;
    document.getElementById('forma_pagamento').value = formaSelecionada;
    liberar_pagamento(formaSelecionada);
  });
});


  function liberar_pagamento(pg){
    forma = pg 
    if(forma == "boleto"){
        pagamento_boleto()
    }else if(forma == "pix"){
      pagamento_pix()
    }else if(forma == "cartao"){
      pagamento_cartao()
    }else if(forma == "pontos"){
      liberar_pg_por_pontos()
    }
  }
  
  function pagamento_cartao(){
    document.getElementById('pg_cartao').style.display = "block"
    document.getElementById('pg_pix').style.display = "none"
    document.getElementById('pg_boleto').style.display = "none"
    getLoading()
  }
  
  function pagamento_pix(){
    document.getElementById('pg_pix').style.display = "block"
    document.getElementById('pg_cartao').style.display = "none"
    document.getElementById('pg_boleto').style.display = "none"
    getLoading()
  }
  function pagamento_boleto(){
    document.getElementById('pg_boleto').style.display = "block"
    document.getElementById('pg_pix').style.display = "none"
    document.getElementById('pg_cartao').style.display = "none"
    getLoading()
  }


 function liberar_btn(){
    setTimeout(() => {
      document.getElementById('concluir_compra').disabled = false;
    }, 5000);
    
  }
   function liberar_pg_por_pontos(){
      document.getElementById('concluir_compra').disabled = false;
  }

  function getLoading(){
     // Espera 5 segundos antes de mostrar o loading
     setTimeout(function () {
    
       showLoading();
       liberar_btn();

          setTimeout(function () {
            hideLoading();  
            showModal(); 
    
          }, 3000);  

    }, 5000);  
  }

  // Funções de mostrar e esconder o loading
function showLoading() {
    document.getElementById('loading').style.display = 'flex'; // Exibe o loading
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none'; // Esconde o loading
}

let myModal;
 
  function showModal(){
    
    myModal = new bootstrap.Modal(document.getElementById('paymentSuccessModal'));
    myModal.show();
  
    setTimeout(function () {
     closeModal()
    }, 2000);  
  }

  function closeModal(){
    myModal.hide();
  }
