// Mascará para o CEP do form 

document.addEventListener("DOMContentLoaded", function(){
  const cepInput = document.getElementById('cep');
  if (cepInput){
    IMask(cepInput,{
      mask: '00000-000'
    })
  }

});


document.addEventListener('DOMContentLoaded', function(){
  const phoneInput = document.getElementById('phone');
  if (phoneInput){
    IMask(phoneInput,{
      mask: '(00) 00000-0000'
    })
  }

});

// Bnt da tela area do cliente 
 document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll("nav button");
  const contents = document.querySelectorAll(".tab-content");

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      // Ativar botão clicado
      buttons.forEach(btn => btn.classList.remove("active"));
      button.classList.add("active");

      // Mostrar conteúdo correspondente
      const target = button.getAttribute("data-target");
      contents.forEach(content => {
        content.classList.remove("active");
        if (content.id === target) {
          content.classList.add("active");
        }
      });
    });
  });
});


// Form de update user 
document.addEventListener('DOMContentLoaded', function () {
    const btnEditar = document.getElementById('btn-editar');
    const btnSalvar = document.getElementById('btn-salvar');
    const btnCancelar = document.getElementById('btn-cancelar');
    const campos = document.querySelectorAll('#form-cadastro input');

    btnEditar.addEventListener('click', function () {
        campos.forEach(campo => campo.disabled = false);
        btnEditar.classList.add('d-none');
        btnSalvar.classList.remove('d-none');
        btnCancelar.classList.remove('d-none');
    });

    btnCancelar.addEventListener('click', function () {
        campos.forEach(campo => campo.disabled = true);
        btnEditar.classList.remove('d-none');
        btnSalvar.classList.add('d-none');
        btnCancelar.classList.add('d-none');
    });
});

