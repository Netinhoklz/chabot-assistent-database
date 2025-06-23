Claro! Criei um arquivo `README.md` que é ao mesmo tempo conciso, profissional e visualmente agradável, perfeito para a página inicial do seu repositório no GitHub.

---

# Assistente IA para Gerenciamento de Contatos 🤖

Este projeto é uma aplicação web completa construída com **Python** e **Flask** que funciona como um sistema inteligente de gerenciamento de contatos. A principal inovação é sua **interface de usuário dupla**:
1.  Uma **interface visual tradicional** com tabelas e formulários.
2.  Uma **interface conversacional** alimentada por um assistente de IA que utiliza a API da OpenAI.

O usuário pode interagir com a agenda de contatos de forma intuitiva, seja clicando em botões ou simplesmente digitando comandos em linguagem natural, como "Adicione a Ana ao meu catálogo" ou "Qual o endereço do escritório?".

## 🏛️ Arquitetura e Funcionamento

O sistema utiliza o recurso de **"Tool Calling"** da OpenAI. Isso permite que a IA não apenas converse, mas também execute ações no sistema.

O fluxo é simples:
1.  A interface web (Flask) recebe o comando do usuário.
2.  O módulo de IA (`F_chat_gpt.py`) interpreta a intenção do usuário.
3.  A IA decide qual "ferramenta" usar:
    - Funções do banco de dados (`F_editar_sqlite.py`) para buscar, adicionar ou deletar contatos.
    - Funções de comunicação (`F_envio_mensagens.py`) para enviar mensagens via APIs externas.
4.  Após a execução da ferramenta, a IA formula uma resposta em linguagem natural e a envia de volta ao usuário.

## ✨ Features Principais

-   **Interface Conversacional com IA:** Gerencie seus contatos usando linguagem natural.
-   **CRUD Completo:** Adicione, visualize, edite e delete contatos através da interface visual ou do chat.
-   **Busca Inteligente:** O sistema encontra contatos mesmo com pequenos erros de digitação.
-   **Integração Externa:** Capaz de se conectar com APIs de terceiros para enviar mensagens (ex: uTalk).
-   **Interface Dinâmica:** O front-end se atualiza em tempo real sem a necessidade de recarregar a página.

## 🛠️ Tecnologias Utilizadas

-   **Backend:** Python, Flask
-   **Inteligência Artificial:** OpenAI API (GPT-4 / o4-mini)
-   **Banco de Dados:** SQLite
-   **Frontend:** HTML, CSS, JavaScript (com chamadas `fetch` para a API)

## 🚀 Começando

Siga os passos abaixo para executar o projeto em sua máquina local.

### Pré-requisitos

-   Python 3.9 ou superior
-   Uma chave de API da [OpenAI](https://platform.openai.com/api-keys)

### Instalação

1.  **Clone o repositório:**
    ```sh
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  **(Recomendado) Crie e ative um ambiente virtual:**
    ```sh
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure suas credenciais:**
    -   Crie um arquivo chamado `.env` na raiz do projeto.
    -   Adicione sua chave da OpenAI a este arquivo:
        ```env
        OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        ```

5.  **Execute a aplicação:**
    ```sh
    python app_flask.py
    ```

6.  Abra seu navegador e acesse `http://127.0.0.1:5000` para ver a aplicação funcionando!

## 💬 Exemplos de Uso com o Assistente

Você pode usar comandos como:
-   `"Adicione o contato João Silva, telefone 5511987654321, endereço Rua das Flores, 123"`
-   `"Qual o telefone da Ana Paula?"`
-   `"Busque por contatos que moram na Avenida Paulista"`
-   `"Exclua o contato com o telefone 5511987654321"`
-   `"Encontre o telefone do João e envie uma mensagem dizendo 'Olá, tudo bem?'"`

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
