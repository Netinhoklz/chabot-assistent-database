from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from F_envio_mensagens import *
from F_editar_sqlite import *
from typing import Tuple

# Carregando API KEY
load_dotenv()
apinumber = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=apinumber)
# Modelo escolhido
MODELO_GPT = 'o4-mini'
tools_agenda_de_contatos = [
    # 1. Adicionar Contato
    {
        "type": "function",
        "function": {
            "name": "adicionar_contato_sql",
            "description": "Adiciona um novo contato ao banco de dados. Funciona com pelo menos um, mas ideal que seja totalmente preenchido com todos os campos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "O nome completo do contato."},
                    "telefone": {"type": "string", "description": "O número de telefone do contato (ex: 5585999998888)."},
                    "endereco": {"type": "string", "description": "O endereço do contato (ex: Ceará-Fortaleza, Bairro José Walter rua 56,750)."},
                },
                "required": ["nome","telefone","endereco"],
            },
        },
    },
    # 2. Excluir Contato
    {
        "type": "function",
        "function": {
            "name": "excluir_contato_sql",
            "description": "Exclui um contato do banco de dados usando o número de telefone como identificador.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_de_telefone": {"type": "string", "description": "O telefone do contato a ser excluído."},
                },
                "required": ["numero_de_telefone"],
            },
        },
    },
    # 3. Alterar Contato
    {
        "type": "function",
        "function": {
            "name": "alterar_contato_sql",
            "description": "Altera dados de um contato existente, identificado pelo seu telefone atual. Pelo menos um dos campos 'novo' (nome, telefone ou endereço) deve ser fornecido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "telefone_atual": {"type": "string", "description": "O telefone atual do contato que será modificado."},
                    "novo_nome": {"type": "string", "description": "O novo nome para o contato."},
                    "novo_telefone": {"type": "string", "description": "O novo número de telefone para o contato."},
                    "novo_endereco": {"type": "string", "description": "O novo endereço para o contato."},
                },
                "required": ["telefone_atual"],
            },
        },
    },
    # 4. Buscar por Nome
    {
        "type": "function",
        "function": {
            "name": "buscar_por_nome_com_sugestoes_sql",
            "description": "Busca contatos no banco de dados pelo nome. Retorna correspondências diretas ou sugestões.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_query": {"type": "string", "description": "O nome ou parte do nome a ser pesquisado."},
                    "quant_max_amostras": {"type": "integer", "description": "O número máximo de contatos a serem retornados (padrão: 10)."}
                },
                "required": ["nome_query"],
            },
        },
    },
    # 5. Buscar por Telefone
    {
        "type": "function",
        "function": {
            "name": "buscar_por_telefone_com_sugestoes_sql",
            "description": "Busca contatos no banco de dados pelo telefone. Retorna correspondências diretas ou sugestões.",
            "parameters": {
                "type": "object",
                "properties": {
                    "telefone_query": {"type": "string", "description": "O número de telefone a ser pesquisado."},
                    "quant_max_amostras": {"type": "integer", "description": "O número máximo de contatos a serem retornados (padrão: 10)."}
                },
                "required": ["telefone_query"],
            },
        },
    },
    # 6. Buscar por Endereço
    {
        "type": "function",
        "function": {
            "name": "buscar_por_endereco_com_sugestoes_sql",
            "description": "Busca contatos no banco de dados pelo endereço. Retorna correspondências diretas ou sugestões.",
            "parameters": {
                "type": "object",
                "properties": {
                    "endereco_query": {"type": "string", "description": "O endereço ou parte do endereço a ser pesquisado."},
                    "quant_max_amostras": {"type": "integer", "description": "O número máximo de contatos a serem retornados (padrão: 10)."}
                },
                "required": ["endereco_query"],
            },
        },
    },
    # 7. Enviar Mensagem via uTalk
    {
        "type": "function",
        "function": {
            "name": "enviar_mensagem_utalk",
            "description": "Envia uma mensagem de texto (chat) para um número de telefone usando a API uTalk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_destino": {"type": "string", "description": "O número do destinatário (ex: 5585999998888)."},
                    "texto_mensagem": {"type": "string", "description": "O conteúdo da mensagem a ser enviada."},
                },
                "required": ["numero_destino", "texto_mensagem"],
            },
        },
    }
]


def assistente_gerenciador_de_contatos(
        conn: sqlite3.Connection,
        texto_user: str,
        historico_conversa: list
) -> Tuple[str, bool]:  # ALTERADO: A função agora retorna uma tupla (string, booleano)
    """
    Função principal que gerencia a conversa e aciona as ferramentas de contato.

    Returns:
        Uma tupla contendo:
        - A resposta final do assistente em formato de string.
        - Um booleano 'True' se o banco de dados foi modificado, senão 'False'.
    """
    # NOVO: Variável para rastrear se o banco de dados foi modificado.
    banco_foi_alterado = False

    # NOVO: Um conjunto com os nomes das funções que escrevem no banco.
    # Usar um conjunto (set) é mais eficiente para verificar a existência.
    funcoes_de_escrita = {"adicionar_contato_sql", "excluir_contato_sql", "alterar_contato_sql"}

    funcoes_disponiveis = {
        "adicionar_contato_sql": lambda **kwargs: adicionar_contato_sql(conn, **kwargs),
        "excluir_contato_sql": lambda **kwargs: excluir_contato_sql(conn, **kwargs),
        "alterar_contato_sql": lambda **kwargs: alterar_contato_sql(conn, **kwargs),
        "buscar_por_nome_com_sugestoes_sql": lambda **kwargs: buscar_por_nome_com_sugestoes_sql(conn, **kwargs),
        "buscar_por_telefone_com_sugestoes_sql": lambda **kwargs: buscar_por_telefone_com_sugestoes_sql(conn, **kwargs),
        "buscar_por_endereco_com_sugestoes_sql": lambda **kwargs: buscar_por_endereco_com_sugestoes_sql(conn, **kwargs),
        "enviar_mensagem_utalk": lambda **kwargs: enviar_mensagem_utalk(**kwargs)
    }

    historico_conversa.append({"role": "user", "content": texto_user})

    resposta = client.chat.completions.create(
        model=MODELO_GPT,
        messages=historico_conversa,
        tools=tools_agenda_de_contatos,
        tool_choice="auto",
    )
    mensagem_resposta = resposta.choices[0].message
    tool_calls = mensagem_resposta.tool_calls

    if tool_calls:
        historico_conversa.append(mensagem_resposta)

        for tool_call in tool_calls:
            nome_funcao = tool_call.function.name

            if nome_funcao not in funcoes_disponiveis:
                resultado_formatado = json.dumps(
                    {"status": "erro", "mensagem": f"Função '{nome_funcao}' não encontrada."})
            else:
                funcao_para_chamar = funcoes_disponiveis[nome_funcao]
                argumentos_funcao = json.loads(tool_call.function.arguments)
                resultado_funcao = funcao_para_chamar(**argumentos_funcao)

                # NOVO: Bloco para verificar se uma função de escrita foi bem-sucedida
                if nome_funcao in funcoes_de_escrita:
                    sucesso = False
                    if isinstance(resultado_funcao, tuple):  # ex: (True, "Contato adicionado")
                        sucesso = resultado_funcao[0]
                    elif isinstance(resultado_funcao, bool):  # ex: True para excluir_contato_sql
                        sucesso = resultado_funcao

                    if sucesso:
                        banco_foi_alterado = True  # <--- ATUALIZAMOS NOSSO SINALIZADOR!

                # ... (o resto da sua lógica de formatação continua igual)
                if isinstance(resultado_funcao, tuple):
                    resultado_formatado = json.dumps({"sucesso": resultado_funcao[0], "dados": resultado_funcao[1]})
                elif isinstance(resultado_funcao, bool):
                    resultado_formatado = json.dumps({"sucesso": resultado_funcao})
                else:
                    resultado_formatado = json.dumps(resultado_funcao)

            historico_conversa.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": nome_funcao,
                "content": resultado_formatado,
            })

        segunda_resposta = client.chat.completions.create(
            model=MODELO_GPT,
            messages=historico_conversa,
        )
        resposta_final = segunda_resposta.choices[0].message.content
        historico_conversa.append({"role": "assistant", "content": resposta_final})

        # ALTERADO: Retorna a resposta final E o nosso sinalizador.
        return resposta_final, banco_foi_alterado
    else:
        resposta_final = mensagem_resposta.content
        historico_conversa.append({"role": "assistant", "content": resposta_final})

        # ALTERADO: Se nenhuma ferramenta foi chamada, o banco não foi alterado.
        return resposta_final, False


def assistente_sem_memoria(texto_user: str,prompt_comand:str = "Você é um assistente", modelo: str = "o4-mini") -> str:
    """
    Função que analisa um texto fornecido pelo usuário, utilizando a API da OpenAI.

    Args:
        texto (str): Texto a ser analisado.
        modelo (str): Modelo da OpenAI a ser utilizado (padrão: "o4-mini").

    Returns:
        str: Resultado da análise do texto.
    """

    resposta = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": prompt_comand},
            {"role": "user", "content": texto_user}
        ]
    )

    return resposta.choices[0].message.content.strip()

if __name__ == "__main__":
    prompt_test = '''Você é um assitente virtual'''
    historico = [
        {"role": "system",
         "content": prompt_test}
    ]
    while True:
        user_input = input("Você: ")
        if user_input.strip().lower() == "sair":
            print("Encerrando...")
            break
        resposta = assistente_gerenciador_de_contatos(texto_user=user_input,historico_conversa=historico)
        print("Assistente:", resposta)
        print(base_json)
