======================================================================
     PROJETO: ASSISTENTE DE GERENCIAMENTO DE CONTATOS COM IA
======================================================================

Este documento contém uma descrição completa do projeto e um mapa mental detalhado da estrutura do código.


---------------------------------------------------
 PARTE 1: EXPLICAÇÃO GERAL DO PROJETO
---------------------------------------------------

### 1. VISÃO GERAL

Este é um projeto de aplicação web para gerenciamento de contatos, desenvolvido em Python com o framework Flask. O seu grande diferencial é a combinação de duas formas de interação:

1.  **Interface Visual Tradicional:** Uma tabela dinâmica onde o usuário pode adicionar, editar e excluir contatos diretamente, com as atualizações aparecendo em tempo real.
2.  **Interface Conversacional com IA:** Um assistente de chat inteligente que permite ao usuário gerenciar seus contatos usando comandos em linguagem natural (ex: "Adicione o João com o telefone X" ou "Qual o endereço da Maria?").

A aplicação foi projetada com uma arquitetura modular, onde cada parte do sistema tem uma responsabilidade bem definida, facilitando a manutenção e a adição de novas funcionalidades.


### 2. PRINCIPAIS PONTOS POSITIVOS

*   **Dupla Interface:** Oferece flexibilidade ao usuário, que pode escolher a forma mais conveniente de interagir com seus dados.
*   **Inteligência Artificial Avançada:** Utiliza o recurso de "Tool Calling" da API da OpenAI, permitindo que a IA não apenas converse, mas também execute ações concretas no sistema (como consultar o banco de dados ou enviar uma mensagem).
*   **Busca Tolerante a Erros:** O sistema é capaz de encontrar contatos mesmo com erros de digitação nos nomes, graças a uma combinação de busca SQL e algoritmos de similaridade de texto.
*   **Sincronização Automática:** A interface gráfica é notificada pela IA sempre que uma ação no chat modifica a base de dados, atualizando a tabela de contatos automaticamente e garantindo que o usuário veja sempre os dados mais recentes.
*   **Arquitetura Extensível:** O design modular facilita a integração com outros serviços externos. Atualmente, há um módulo dedicado para se comunicar com uma API de envio de mensagens (uTalk).


### 3. FLUXO DE INTERAÇÃO TÍPICO (EXEMPLO COM A IA)

Para entender como os módulos colaboram, imagine que o usuário digite no chat: **"Encontre o telefone da Ana e envie uma mensagem dizendo 'Olá!'"**

1.  **Frontend (Navegador):** A mensagem é enviada para a API do Flask.
2.  **`app_flask.py` (Controlador):** Recebe a requisição e a repassa para o cérebro da IA.
3.  **`F_chat_gpt.py` (Cérebro da IA):** Envia a conversa para a OpenAI. A IA decide que precisa usar duas ferramentas em sequência.
4.  **Primeira Ação (Busca):** A IA chama a ferramenta de busca.
5.  **`F_editar_sqlite.py` (Memória):** Executa a busca no banco de dados e retorna o telefone da "Ana".
6.  **`F_chat_gpt.py`:** A IA recebe o telefone e prossegue para a segunda ação.
7.  **Segunda Ação (Envio):** A IA chama a ferramenta de envio de mensagem.
8.  **`F_envio_mensagens.py` (Voz):** Envia a mensagem "Olá!" para o telefone encontrado, usando a API externa da uTalk.
9.  **`F_chat_gpt.py`:** A IA recebe a confirmação de que tudo foi executado e formula uma resposta final em linguagem natural, como: "Pronto! Encontrei o telefone da Ana e enviei a mensagem para ela."
10. **`app_flask.py`:** Retorna essa resposta para o frontend, que a exibe na tela do chat.



---------------------------------------------------
 PARTE 2: MAPA MENTAL DO CÓDIGO (ESTRUTURA)
---------------------------------------------------

PROJETO: ASSISTENTE DE CONTATOS
├── 🖥️ **FRONTEND (Interface do Usuário)**
│   └── `index.html` (e JavaScript embutido)
│       ├── Estrutura: Layout de duas colunas (Tabela de Contatos e Chat da IA).
│       ├── Tabela de Contatos:
│       │   ├── Exibe todos os contatos.
│       │   ├── Permite edição "in-place" (direto na célula).
│       │   ├── Botões para Adicionar e Excluir contatos.
│       │   └── Filtro/Busca instantânea na tabela.
│       ├── Chatbot da IA:
│       │   ├── Envia mensagens do usuário para o backend.
│       │   ├── Exibe as respostas da IA.
│       ├── Lógica JavaScript:
│       │   ├── `refreshContactsTable()`: Função central que busca os dados na API e redesenha a tabela.
│       │   ├── Comunicação com a API do Flask (usando `fetch`).
│       │   └── Lógica para verificar o sinalizador `refresh_table` da IA para atualizar a tabela.
│
├── ⚙️ **BACKEND (Servidor Python)**
│   ├── 🐍 **`app_flask.py` (Controlador Principal / Maestro)**
│   │   ├── Função: Gerencia todas as rotas da aplicação (endpoints).
│   │   ├── Rota `GET /`:
│   │   │   └── Ação: Carrega e exibe a página `index.html` inicial.
│   │   ├── Rota `GET /api/get_contacts`:
│   │   │   └── Ação: Busca todos os contatos no BD e retorna como JSON.
│   │   ├── Rota `POST /api/chatbot`:
│   │   │   └── Ação: Recebe a mensagem do chat, chama `F_chat_gpt.py` e retorna a resposta da IA.
│   │   ├── Rota `POST /api/add_contact`:
│   │   │   └── Ação: Adiciona um novo contato no BD.
│   │   └── Rota `POST /api/delete_contact/<id>`:
│   │       └── Ação: Deleta um contato específico pelo seu ID.
│   │
│   ├── 🧠 **`F_chat_gpt.py` (Cérebro da IA / Orquestrador)**
│   │   ├── Função: Orquestra a interação com a API da OpenAI usando "Tool Calling".
│   │   └── Função Principal: `assistente_gerenciador_de_contatos()`
│   │       ├── Parâmetros: Conexão com o BD, texto do usuário, histórico da conversa.
│   │       ├── Lógica:
│   │       │   ├── 1. Envia a conversa e as ferramentas disponíveis para a OpenAI.
│   │       │   ├── 2. Recebe a decisão da IA (chamar uma ferramenta ou responder).
│   │       │   ├── 3. Executa a(s) ferramenta(s) escolhida(s) (funções de outros módulos).
│   │       │   ├── 4. Envia o resultado da ferramenta de volta para a IA.
│   │       │   └── 5. Recebe e retorna a resposta final em linguagem natural.
│   │       └── Retorno Chave: `(string_resposta, boolean_banco_alterado)` -> Informa se a tabela do frontend precisa ser atualizada.
│   │
│   ├── 🗃️ **`F_editar_sqlite.py` (Memória / Acesso ao Banco de Dados)**
│   │   ├── Função: Gerencia todas as operações de CRUD (Criar, Ler, Atualizar, Excluir) no SQLite.
│   │   ├── Função `inicializar_banco()`: Cria a tabela `contatos` se ela não existir.
│   │   ├── Funções de Escrita (CRUD):
│   │   │   ├── `adicionar_contato_sql()`
│   │   │   ├── `excluir_contato_sql()`
│   │   │   └── `alterar_contato_sql()`
│   │   └── Funções de Leitura (Busca Inteligente):
│   │       ├── `buscar_por_nome_com_sugestoes_sql()`
│   │       ├── `buscar_por_telefone_com_sugestoes_sql()`
│   │       └── Lógica de Busca: Primeiro tenta uma busca rápida (SQL `LIKE`), se falhar, usa um cálculo de similaridade de texto para encontrar correspondências com erros de digitação.
│   │
│   └── 🗣️ **`F_envio_mensagens.py` (Voz / Comunicação Externa)**
│       ├── Função: Encapsula a lógica para se comunicar com APIs de terceiros.
│       └── Função Principal: `enviar_mensagem_utalk()`
│           ├── Parâmetros: Número de destino, texto da mensagem.
│           ├── Ação: Monta e envia uma requisição `GET` para a API da uTalk.
│           └── Retorno: Uma tupla `(sucesso, dados_resposta)` com o status do envio e a resposta da API (ou o erro).
│
└── 🌐 **SERVIÇOS EXTERNOS**
    ├── `OpenAI API`: Fornece o modelo de linguagem para o cérebro do chatbot.
    └── `uTalk API`: Serviço utilizado para o envio de mensagens de texto.
