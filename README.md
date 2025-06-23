<div class="container">
        <h1>🤖 Assistente de Gerenciamento de Contatos com IA</h1>

        <p class="badges">
            <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
            <img src="https://img.shields.io/badge/Flask-2.2%2B-black?style=for-the-badge&logo=flask" alt="Flask">
            <img src="https://img.shields.io/badge/OpenAI-API-green?style=for-the-badge&logo=openai" alt="OpenAI">
            <img src="https://img.shields.io/badge/SQLite-3-blue?style=for-the-badge&logo=sqlite" alt="SQLite">
            <img src="https://img.shields.io/badge/JavaScript-ES6-yellow?style=for-the-badge&logo=javascript" alt="JavaScript">
        </p>

        <p>Este projeto é uma aplicação web completa para gerenciamento de contatos, construída com Python e Flask. Seu grande diferencial é a integração de uma <strong>interface de usuário dupla</strong>: uma visual tradicional, baseada em formulários e tabelas, e outra conversacional, alimentada por um poderoso assistente de Inteligência Artificial.</p>
        <p>O sistema permite que o usuário interaja com sua agenda de contatos de forma intuitiva, seja clicando em botões para editar e excluir, ou simplesmente digitando comandos em linguagem natural, como "Adicione a Ana ao meu catálogo" ou "Qual o endereço do escritório?".</p>

        <h2>✨ Principais Funcionalidades (Pontos Positivos)</h2>
        <ul>
            <li><strong>🧠 Interface Conversacional Inteligente:</strong> Utilize o chat para adicionar, buscar, alterar e deletar contatos usando linguagem natural, graças à integração com a API da OpenAI e a funcionalidade de "Tool Calling".</li>
            <li><strong>💻 Interface Visual Dinâmica:</strong> Adicione, edite e delete contatos diretamente em uma tabela que se atualiza em tempo real, sem a necessidade de recarregar a página.</li>
            <li><strong>🔍 Busca Robusta e Tolerante a Erros:</strong> O sistema de busca combina a velocidade do SQL com algoritmos de similaridade de texto, encontrando contatos mesmo que você cometa erros de digitação.</li>
            <li><strong>🏗️ Arquitetura Modular e Organizada:</strong> O código é dividido em módulos com responsabilidades claras (servidor web, lógica da IA, acesso ao banco de dados, comunicação externa), facilitando a manutenção e a escalabilidade.</li>
            <li><strong>📡 Integração com APIs Externas:</strong> O projeto está preparado para se comunicar com serviços de terceiros, como a API da uTalk para envio de mensagens, demonstrando uma arquitetura extensível.</li>
            <li><strong>🔄 Sincronização Automática:</strong> A interface gráfica é notificada pela IA sempre que uma ação no chat modifica a base de dados, atualizando a tabela de contatos automaticamente e garantindo consistência.</li>
        </ul>

        <h2>🏗️ Arquitetura do Sistema</h2>
        <p>A aplicação é dividida em componentes distintos, cada um com uma responsabilidade clara, orquestrados pelo servidor Flask.</p>
        <ul>
            <li><strong><code>app_flask.py</code> (O Maestro):</strong> O coração da aplicação. Gerencia as requisições web, serve as páginas HTML e expõe uma API JSON para a interface dinâmica.</li>
            <li><strong><code>F_chat_gpt.py</code> (O Cérebro):</strong> Contém a lógica de Inteligência Artificial. Interpreta a intenção do usuário e decide qual ferramenta do sistema executar (buscar contato, enviar mensagem, etc.).</li>
            <li><strong><code>F_editar_sqlite.py</code> (A Memória):</strong> Gerencia todas as operações de CRUD (Criar, Ler, Atualizar, Excluir) no banco de dados SQLite.</li>
            <li><strong><code>F_envio_mensagens.py</code> (A Voz):</strong> É a ponte de comunicação da aplicação com o mundo exterior, consumindo a API da uTalk para enviar mensagens.</li>
        </ul>
        
        <h3>Mapa Mental da Arquitetura</h3>
        <p>O diagrama abaixo ilustra o fluxo de informações e as dependências entre os diferentes componentes do sistema.</p>
        <div class="mermaid">
        graph TD
            %% ----- DEFINIÇÃO DE ESTILOS -----
            classDef frontendStyle fill:#e0f7fa,stroke:#00796b,stroke-width:2px
            classDef serverStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
            classDef aiStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
            classDef dbStyle fill:#dcedc8,stroke:#558b2f,stroke-width:2px
            classDef messagingStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
            classDef externalStyle fill:#ffcdd2,stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5

            %% ----- SUBGRAFOS PARA ORGANIZAÇÃO -----
            subgraph "Frontend (Navegador do Usuário)"
                User(Usuário)
                UI[Página Web - HTML/JS]
            end

            subgraph "Backend (Servidor Python)"
                Flask[app_flask.py <br> Controlador Principal]
                Chat[F_chat_gpt.py <br> Orquestrador IA]
                DB_Module[F_editar_sqlite.py <br> Acesso ao BD]
                MSG_Module[F_envio_mensagens.py <br> Acesso à API de Msg]
                SQLite[(base_contatos.db)]
            end

            subgraph "Serviços Externos"
                OpenAI_API{{OpenAI API}}
                uTalk_API{{uTalk API}}
            end

            %% ----- RELACIONAMENTOS -----
            User -- Interage com --> UI

            UI -- Requisição HTTP <br> (Fetch/AJAX) --> Flask

            %% Fluxo do Chatbot
            Flask -- /api/chatbot --> Chat
            Chat -- 1. Consulta o modelo --> OpenAI_API
            OpenAI_API -- 2. Retorna intenção <br> ('Tool Call') --> Chat
            Chat -- 3a. Chama Ferramenta de BD --> DB_Module
            Chat -- 3b. Chama Ferramenta de Msg --> MSG_Module

            %% Fluxo de Ações Diretas (sem IA)
            Flask -- /api/add_contact <br> /api/delete_contact --> DB_Module

            %% Interações com Módulos e BD
            DB_Module -- Executa CRUD --> SQLite
            MSG_Module -- Envia Mensagem --> uTalk_API

            %% Resposta ao Usuário
            Chat -- 4. Formula resposta final --> Flask
            Flask -- Retorna JSON --> UI
            UI -- Exibe na tela --> User

            %% ----- APLICAÇÃO DOS ESTILOS -----
            class User,UI frontendStyle
            class Flask serverStyle
            class Chat aiStyle
            class DB_Module,SQLite dbStyle
            class MSG_Module messagingStyle
            class OpenAI_API,uTalk_API externalStyle
        </div>

        <h2>🛠️ Tecnologias Utilizadas</h2>
        <ul>
            <li><strong>Backend:</strong> Python, Flask</li>
            <li><strong>Banco de Dados:</strong> SQLite</li>
            <li><strong>Inteligência Artificial:</strong> OpenAI API (GPT-4 / GPT-3.5)</li>
            <li><strong>Frontend:</strong> HTML5, CSS3 (Flexbox), JavaScript (Vanilla)</li>
            <li><strong>Bibliotecas Python:</strong> <code>openai</code>, <code>requests</code>, <code>scikit-learn</code> (para busca por similaridade)</li>
        </ul>

        <h2>⚙️ Como Executar o Projeto</h2>
        <p>Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.</p>

        <h3>1. Clone o Repositório</h3>
        <pre><code>git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio</code></pre>

        <h3>2. Crie e Ative um Ambiente Virtual</h3>
        <pre><code># Para Windows
python -m venv venv
.\\venv\\Scripts\\activate

# Para macOS/Linux
python3 -m venv venv
source venv/bin/activate</code></pre>

        <h3>3. Instale as Dependências</h3>
        <pre><code>pip install -r requirements.txt</code></pre>

        <h3>4. Configure as Variáveis de Ambiente</h3>
        <p>Crie um arquivo chamado <code>.env</code> na raiz do projeto e adicione sua chave da API da OpenAI:</p>
        <pre><code># .env
OPENAI_API_KEY="sua_chave_secreta_aqui"</code></pre>

        <h3>5. Execute a Aplicação</h3>
        <pre><code>flask run
# ou
python app_flask.py</code></pre>
        <p>A aplicação estará disponível em <code>http://127.0.0.1:5000</code>.</p>
    </div>

    <script type="module">
        // Importa e inicializa a biblioteca Mermaid para renderizar o diagrama
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true });
    </script>
