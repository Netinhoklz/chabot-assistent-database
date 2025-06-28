import requests

# ----------- Função de envio de mensagem ----------- #
def enviar_mensagem_utalk(numero_destino: str, texto_mensagem: str) -> tuple[bool, dict | str]:
    """
    Envia uma mensagem de chat usando a API da uTalk.

    Esta função monta a URL com os parâmetros necessários e faz uma
    requisição GET para o endpoint da API.

    Args:
        numero_destino (str): O número de telefone do destinatário,
                              incluindo o DDI e DDD (ex: "5585999998888").
        texto_mensagem (str): A mensagem a ser enviada.

    Returns:
        tuple[bool, dict | str]: Uma tupla contendo:
                                 - True se a mensagem foi enviada com sucesso, False caso contrário.
                                 - Um dicionário com a resposta da API (se for JSON) ou uma string de erro.
    """
    # --- Constantes da API ---
    # Estes valores parecem ser fixos para a sua automação
    BASE_URL = "COLOQUE SUA BASE DE URL AQUI"
    CMD = "chat"
    ID_AUTOMACAO = "COLOQUE O SEU ID DE AUTOMAÇÃO AQUI"

    # --- Montagem dos parâmetros da requisição ---
    params = {
        "cmd": CMD,
        "id": ID_AUTOMACAO,
        "to": numero_destino,
        "msg": texto_mensagem
    }

    print(f"Tentando enviar para: {numero_destino}...")

    # --- Bloco de execução e tratamento de erros ---
    try:
        response = requests.get(BASE_URL, params=params)

        # Lança uma exceção para códigos de erro HTTP (4xx ou 5xx)
        response.raise_for_status()

        print("✅ Requisição enviada com sucesso!")

        # Tenta decodificar a resposta como JSON, se não conseguir, retorna como texto
        try:
            return (True, response.json())
        except requests.exceptions.JSONDecodeError:
            return (True, response.text)

    except requests.exceptions.HTTPError as http_err:
        erro_msg = f"Erro HTTP: {http_err} - Resposta: {response.text}"
        print(f"❌ {erro_msg}")
        return (False, erro_msg)
    except requests.exceptions.RequestException as err:
        erro_msg = f"Erro de Conexão/Requisição: {err}"
        print(f"❌ {erro_msg}")
        return (False, erro_msg)


# --- EXEMPLO DE COMO USAR A FUNÇÃO ---
if __name__ == "__main__":
    # Substitua com o número para o qual você quer enviar a mensagem
    meu_numero = "5585995545837"
    minha_mensagem = f"Olá! Este é um teste enviado pela minha função Python. (Fortaleza, {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')})"

    # Chama a função para enviar a mensagem
    sucesso, dados_resposta = enviar_mensagem_utalk(meu_numero, minha_mensagem)

    # Verifica o resultado
    if sucesso:
        print("\n--- Resultado ---")
        print("A função retornou 'sucesso'.")
        print("Dados da resposta da API:")
        print(dados_resposta)
    else:
        print("\n--- Resultado ---")
        print("A função retornou 'falha'.")
        print("Detalhes do erro:")
        print(dados_resposta)
