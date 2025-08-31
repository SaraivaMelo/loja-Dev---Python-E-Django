
#Visão Geral

loja/
│
├── apps/
│   ├── core/          # Página inicial (home)
│   ├── clientes/      # Área de cadastro, login, perfil e autenticação
│   └── produtos/      # Cadastro de produtos
│
├── config/            # Configuração do projeto Django
│   ├── settings.py    # Configurações globais (apps, db, etc.)
│   ├── urls.py        # Roteamento global
│   └── templates/     # Templates globais (base.html, home.html, nav_bar.html)
│
├── static/            # Arquivos estáticos globais (css/js/img)
└── venv/              # Ambiente virtual (dependências do projeto)

# FLUXO

config/urls.py

Ponto de entrada de todas as URLs do projeto:

    urlpatterns = [
        path('admin/', admin.site.urls),                     # Admin
        path('', home, name='home'),                         # Página inicial
        path('produtos/', include('apps.produtos.urls')),    # App produtos
        path('clientes/', include('apps.clientes.urls')),    # App clientes
    ]

    - / chama core.views.home
    - /produtos/ delega para as URLs do app produtos
    - /clientes/ delega para as URLs do app clientes

 config/templates/

 O sistema de templates é centralizado com uso de um layout base, onde:

    base.html: é o template base que define o layout HTML, CSS e estrutura geral

    {% block content %}: cada página preenche esse bloco com seu conteúdo

    {% include "nav_bar.html" %}: navegação disponível em todas as páginas

 App core → Página Inicial

    URL / chama apps.core.views.home

    Renderiza o template home.html, que herda de base.html

    Apenas exibe uma mensagem de boas-vindas

App produtos → Cadastro de produtos

URL /produtos/cadastrar/ → views.cadastrar_produto

View cadastrar_produto:

    Carrega ou cria categorias padrão

    Se for POST, valida o formulário ProdutoForm

    Exibe mensagens de sucesso/erro com django.contrib.messages

    Renderiza o template produtos/cadastrar.html

Templates:

    cadastrar.html → herda de base.html

    inclui o formulário form_cadastrar.html com campos HTML puros

    exibe mensagens com alertas customizados (custom-alert)

Modelos envolvidos:

    Categoria: nome único

    Produto: campos como nome, descrição, quantidade, preço, imagem e categoria

App clientes → Login, Cadastro, Área do Cliente

a) Cadastro
    URL: /clientes/cadastro/

    View: cadastro

    Usa três formulários:

    UserRegisterForm → usuário

    AddressForm → endereço

    CustomerProfileForm → telefone

    Cria um User, Address e CustomerProfile associados

    Faz login automático após o cadastro

    Template: cadastro.html + form_cadastro_cliente.html

    Validações e mensagens exibidas diretamente

b) Login
    URL: /clientes/login/

    View: login_cliente

    Busca usuário por e-mail

    Autentica usando User do Django

    Redireciona para clientes/ (área do cliente)

c) Área do cliente
    URL: /clientes/clientes/

    View: clientes (protegida com @login_required)

    Template: area_cliente.html

    Exibe duas seções: Minhas Compras e Meus Dados

    Alterna entre seções com JS (script.js)

# Sobre o cadastro do cliente

Quando o cliente vai se cadastrar, entra em ação 3 tipos de informações diferentes:

Dados do usuário (nome, email, senha)
    Salvo na tabela User do django e tratado no UserRegisterForm
Endereço (CEP, rua, cidade, etc.)
    Salvo na tabela Address do banco e tratado no AddressForm
Perfil do cliente (telefone, pontos)
    Salvo na tabela CustomerProfile do banco e tratado no CustomerProfileForm

 - Cada form cuida de uma tabela/model diferente.
 - Fica mais fácil validar, salvar e controlar os dados.
 - Evita confusão de campos (cada form só tem os campos que precisa).
 - Permite reutilizar formulários separadamente no futuro.

 A classe UserRegisterForm Herda de UserCreationForm, que já cuida de senha, validação, etc, 
 com os campos: email, first_name, last_name, password1, password2
    Porque não tem o username? porque é gerado automaticamente com uuid.
 
 A classe AddressForm está ligado ao seu model Address, com os campos:
    cep, street, number, neighborhood, city, state e Usa widgets para 
    aplicar classes e IDs (para estilizar e fazer máscaras com JS).

 A classe CustomerProfileForm  está ligado ao model CustomerProfile
 com o campo phone. O campo user e o addres  user e address não aparecem 
 no form porque eles são preenchidos manualmente no views.py após o form ser validado.

 Quando o usuário acessa /clientes/cadastro/ O view cadastro(request) carrega os 3 formulários:
    user_form = UserRegisterForm()
    address_form = AddressForm()
    profile_form = CustomerProfileForm()

O template mostra todos os campos juntos (HTML).

Quando o usuário envia (POST) no view, cada formulário salva sua parte:

    user = user_form.save()  # Cria o User
    address = address_form.save()  # Cria o endereço
    profile = profile_form.save(commit=False)
    profile.user = user  # Conecta com User
    profile.address = address  # Conecta com Address
    profile.save()