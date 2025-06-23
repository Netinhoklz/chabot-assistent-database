import sqlite3
import operator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from unidecode import unidecode
import unicodedata
# ------------ FUNÇÕES DE NORMALIZAÇÃO ------------ #
def _normalizar_telefone(telefone_str: str) -> str:
    """Remove todos os caracteres não numéricos de uma string de telefone.

    Esta função é usada para limpar números de telefone, retendo apenas os
    dígitos (0-9) para permitir comparações consistentes.

    Args:
        telefone_str (str): A string do telefone, que pode conter formatação
            como parênteses, hífens e espaços.

    Returns:
        str: Uma string contendo apenas os dígitos do telefone original.

    Example:
        >>> _normalizar_telefone("(85) 98877-6655")
        '85988776655'
        >>> _normalizar_telefone("+55 48 1234.5678")
        '554812345678'
    """
    return re.sub(r'\D', '', telefone_str)

def _normalizar_endereco(endereco_str: str) -> str:
    """Normaliza um endereço para busca e comparação.

       O processo de normalização consiste em três etapas:
       1. Converte toda a string para letras minúsculas.
       2. Remove acentos e caracteres diacríticos (e.g., 'á' -> 'a', 'ç' -> 'c').
       3. Remove todos os caracteres que não sejam letras, números ou espaços.

       Args:
           endereco_str (str): A string do endereço original.

       Returns:
           str: O endereço normalizado, contendo apenas letras minúsculas,
                números e espaços.

       Example:
            _normalizar_endereco("Avenida das Acácias, nº 123 - Bairro: Centro")
           'avenida das acacias no 123 bairro centro'
            _normalizar_endereco("Praça da Sé, S/N")
           'praca da se sn'
       """
    texto_sem_acentos = unidecode(endereco_str.lower())
    return re.sub(r'[^a-z0-9\s]', '', texto_sem_acentos)

def _normalizar_texto(texto: str) -> str:
    """
    Função auxiliar para normalizar texto: remove acentos e converte para minúsculas.
    """
    if not isinstance(texto, str):
        return ""
    # Decompõe os caracteres acentuados (ex: 'á' -> 'a' + ´)
    nfkd_form = unicodedata.normalize('NFKD', texto)
    # Filtra apenas os caracteres não combinantes (as letras base)
    texto_sem_acentos = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return texto_sem_acentos.lower()

# ------------ FUNÇÕES DE GERENCIAMENTO DO BANCO DE DADOS ------------ #

def inicializar_banco(db_name: str = "base_contatos.db") -> sqlite3.Connection:
    """
    Cria e/ou conecta ao banco de dados SQLite.
    Cria a tabela 'contatos' se ela não existir.
    O campo 'telefone' é UNIQUE para evitar duplicatas nativamente.

    Args:
        db_name (str): O nome do arquivo do banco de dados.
                       O padrão é "contatos.db".

    Returns:
        sqlite3.Connection: O objeto de conexão com o banco de dados.
    """
    print(f"Conectando ao banco de dados '{db_name}'...")
    conn = sqlite3.connect(db_name)
    # Permite que os resultados da consulta venham como dicionários
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("Criando a tabela 'contatos' se ela não existir...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos (
            id INTEGER PRIMARY KEY ,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL UNIQUE,
            endereco TEXT
        )
    ''')
    # O commit salva a criação da tabela
    conn.commit()
    print("Tabela 'contatos' pronta para uso.")
    return conn


def migrar_json_para_sqlite(base_json: dict, conn: sqlite3.Connection):
    """
  Migra os contatos de uma estrutura JSON para o banco de dados SQLite.
  Ignora contatos cujo telefone já exista no banco.
  """
    cursor = conn.cursor()
    contatos_para_migrar = base_json.get('contatos', [])

    for contato in contatos_para_migrar:
        try:
            cursor.execute(
                "INSERT INTO contatos (nome, telefone, endereco) VALUES (?, ?, ?)",
                (contato['nome'], contato['telefone'], contato['endereco'])
            )
        except sqlite3.IntegrityError:
            # Esta exceção é acionada pela restrição UNIQUE no telefone
            print(f"Aviso: Telefone '{contato['telefone']}' já existe. Contato não migrado.")

    conn.commit()
    print(f"Migração concluída. {len(contatos_para_migrar)} contatos do JSON processados.")


# ------------ FUNÇÕES DE EDIÇÃO  ------------ #

def adicionar_contato_sql(
    conn: sqlite3.Connection,
    nome: str = "None",
    telefone: str = "None",
    endereco: str = "Não informado"
) -> tuple[bool, str]:
    """
    Adiciona um novo contato ao banco de dados SQLite.

    - Se um campo for uma string vazia ou contiver apenas espaços, ele será salvo como NULL.
    - Exige que PELO MENOS o nome ou o telefone seja fornecido.
    - Retorna uma tupla com (sucesso: bool, mensagem: str).
    """
    # 1. Trata as entradas: transforma strings vazias ou com espaços em None
    # A expressão `valor.strip() or None` é uma forma idiomática em Python para fazer isso.
    # Se `valor.strip()` for uma string vazia (considerada 'Falsy'), a expressão retorna `None`.
    # Caso contrário, retorna a própria string sem espaços nas pontas.
    nome_final = nome.strip() if nome else None
    telefone_final = telefone.strip() if telefone else None
    endereco_final = endereco.strip() if endereco else None

    # 2. Validação: garante que não estamos inserindo um contato "fantasma"
    if not nome_final and not telefone_final:
        return (False, "Erro: É necessário fornecer pelo menos um nome ou um telefone.")

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO contatos (nome, telefone, endereco) VALUES (?, ?, ?)",
            (nome_final, telefone_final, endereco_final)
        )
        conn.commit()
        return (True, "Contato adicionado com sucesso!")
    except sqlite3.IntegrityError:
        # Boa prática: reverter a transação em caso de erro
        conn.rollback()
        # Garante que o telefone não seja None na mensagem de erro
        if telefone_final:
             return (False, f"Erro: O telefone '{telefone_final}' já está cadastrado.")
        return (False, "Erro: Violação de integridade no banco de dados.")
    except Exception as e:
        # Captura outras exceções possíveis para maior robustez
        conn.rollback()
        return (False, f"Erro inesperado: {e}")


def excluir_contato_sql(conn: sqlite3.Connection, numero_de_telefone: str) -> bool:
    """Exclui um contato do banco de dados por correspondência exata do telefone.

    Args:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados SQLite.
        numero_de_telefone (str): Número de telefone exato do contato a ser removido.

    Returns:
        bool: `True` se o contato foi excluído, `False` caso nenhum contato
            com o telefone exato tenha sido encontrado.

    Raises:
        sqlite3.Error: Em caso de erro na consulta ao banco de dados.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contatos WHERE telefone = ?", (numero_de_telefone,))
    conn.commit()
    # cursor.rowcount > 0 significa que uma linha foi de fato apagada
    return cursor.rowcount > 0

def alterar_contato_sql(
    conn: sqlite3.Connection,
    telefone_atual: str,
    novo_nome: str = None,
    novo_telefone: str = None,
    novo_endereco: str = None
) -> tuple[bool, str]:
    """Altera os dados de um contato, localizado por telefone (match exato).

    Pelo menos um novo dado deve ser fornecido. Valida a existência do contato
    e a unicidade do novo telefone.

    Args:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados.
        telefone_atual (str): Telefone exato do contato a ser modificado.
        novo_nome (str, optional): Novo nome para o contato.
        novo_telefone (str, optional): Novo telefone para o contato (deve ser único).
        novo_endereco (str, optional): Novo endereço para o contato.

    Returns:
        tuple[bool, str]: Tupla com (sucesso, mensagem). Retorna `True` em caso
        de sucesso, ou `False` com uma mensagem de erro específica em caso de falha.

    Raises:
        sqlite3.Error: Em caso de erro na consulta ao banco de dados.
    """
    if novo_nome is None and novo_telefone is None and novo_endereco is None:
        return (False, "Nenhuma alteração foi fornecida.")

    cursor = conn.cursor()

    # Verifica se o contato a ser alterado existe
    cursor.execute("SELECT id FROM contatos WHERE telefone = ?", (telefone_atual,))
    if cursor.fetchone() is None:
        return (False, f"Erro: Contato com o telefone '{telefone_atual}' não foi encontrado.")

    # Se um novo telefone for fornecido, verifica se ele já não está em uso
    if novo_telefone:
        cursor.execute("SELECT id FROM contatos WHERE telefone = ? AND telefone != ?", (novo_telefone, telefone_atual))
        if cursor.fetchone() is not None:
            return (False, f"Erro: O novo telefone '{novo_telefone}' já pertence a outro contato.")

    # Constrói a query de UPDATE dinamicamente
    updates = []
    params = []
    if novo_nome is not None:
        updates.append("nome = ?")
        params.append(novo_nome.strip())
    if novo_telefone is not None:
        updates.append("telefone = ?")
        params.append(novo_telefone.strip())
    if novo_endereco is not None:
        updates.append("endereco = ?")
        params.append(novo_endereco.strip())

    query = f"UPDATE contatos SET {', '.join(updates)} WHERE telefone = ?"
    params.append(telefone_atual)

    cursor.execute(query, tuple(params))
    conn.commit()

    return (True, "Contato alterado com sucesso!")


# ------------ FUNÇÕES DE BUSCA (Versão SQL + Similaridade) ------------ #

def buscar_por_nome_com_sugestoes_sql(
        conn: sqlite3.Connection,
        nome_query: str,
        quant_max_amostras: int = 10
) -> dict:
    """
    Busca contatos por nome com performance otimizada, sem a necessidade
    de colunas adicionais e com um fallback eficiente em memória.

    Args:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados SQLite.
        nome_query (str): Termo de busca para o nome do contato.
        quant_max_amostras (int, optional): Nº máximo de itens retornados. Padrão: 10.

    Returns:
        dict: Um dicionário com as chaves "status" e "dados".

    Raises:
        sqlite3.Error: Em caso de erro na consulta ao banco de dados.
    """
    if not nome_query or not nome_query.strip():
        return {"status": "vazio", "dados": []}

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    termo_busca = f"%{nome_query.strip()}%"

    # --- Etapa 1: Busca Direta Otimizada com SQL ---
    # Adicionamos COLLATE NOCASE para buscas case-insensitive e LIMIT para eficiência.
    query_sql_direta = """
                SELECT * FROM contatos 
                WHERE nome LIKE ? COLLATE NOCASE 
                LIMIT ?
            """
    cursor.execute(query_sql_direta, (termo_busca, quant_max_amostras))
    resultados_diretos = [dict(row) for row in cursor.fetchall()]

    if resultados_diretos:
        return {"status": "encontrado", "dados": resultados_diretos}

    # --- Etapa 2: Busca por Similaridade com Fallback Otimizado em Memória ---
    # Só executa se a busca direta não encontrar nada.

    # 2a. Busca apenas os dados necessários para o cálculo (id e nome)
    cursor.execute("SELECT id, nome FROM contatos")
    contatos_para_similaridade = cursor.fetchall()

    if not contatos_para_similaridade:
        return {"status": "vazio", "dados": []}

    nomes_dos_contatos = [contato['nome'] for contato in contatos_para_similaridade]
    vectorizer = TfidfVectorizer(min_df=1, analyzer='char', ngram_range=(2, 3))
    tfidf_matrix = vectorizer.fit_transform(nomes_dos_contatos)
    query_vector = vectorizer.transform([nome_query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    sugestoes_com_score = [
        (cosine_similarities[i], contatos_para_similaridade[i]['id'])
        for i, _ in enumerate(contatos_para_similaridade)
        if cosine_similarities[i] > 0.1
    ]
    sugestoes_com_score.sort(key=operator.itemgetter(0), reverse=True)

    ids_sugeridos = [contact_id for score, contact_id in sugestoes_com_score[:quant_max_amostras]]

    if not ids_sugeridos:
        return {"status": "vazio", "dados": []}

    # 2b. Agora, busca os dados completos APENAS dos contatos sugeridos.
    placeholders = ','.join('?' for _ in ids_sugeridos)
    query_final = f"SELECT * FROM contatos WHERE id IN ({placeholders})"
    cursor.execute(query_final, ids_sugeridos)

    resultados_finais_map = {dict(row)['id']: dict(row) for row in cursor.fetchall()}
    sugestoes_finais_ordenadas = [resultados_finais_map[id] for id in ids_sugeridos if id in resultados_finais_map]

    return {"status": "sugestao", "dados": sugestoes_finais_ordenadas}


def buscar_por_telefone_com_sugestoes_sql(
        conn: sqlite3.Connection,
        telefone_query: str,
        quant_max_amostras: int = 10
) -> dict:
    """
    Busca contatos por telefone com estratégia de dois estágios e limiar de sugestão fixo.

    1. Busca Direta: Realiza uma busca LIKE otimizada em uma coluna indexada
       de telefones normalizados (apenas dígitos).
    2. Fallback com Sugestão: Se nada for encontrado, calcula a similaridade de
       cosseno para sugerir os números mais parecidos, com limiar fixo em 0.3.

    Args:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados SQLite.
        telefone_query (str): Telefone a ser buscado (formatação é ignorada).
        quant_max_amostras (int, optional): Nº máximo de itens retornados. Padrão: 10.

    Returns:
        dict: Um dicionário com "status" ('encontrado', 'sugestao', 'vazio') e "dados".
    """
    if not telefone_query or not telefone_query.strip():
        return {"status": "vazio", "dados": []}

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # --- ETAPA 1: BUSCA DIRETA E OTIMIZADA ---
    query_normalizada = _normalizar_telefone(telefone_query)

    sql_busca_direta = "SELECT * FROM contatos WHERE telefone LIKE ? COLLATE NOCASE LIMIT ?"
    parametros = (f'%{query_normalizada}%', quant_max_amostras)

    cursor.execute(sql_busca_direta, parametros)
    resultados_diretos = [dict(row) for row in cursor.fetchall()]

    if resultados_diretos:
        return {"status": "encontrado", "dados": resultados_diretos}

    # --- ETAPA 2: FALLBACK COM SIMILARIDADE DE COSSENO ---
    cursor.execute("SELECT rowid, telefone FROM contatos")
    lista_de_contatos_para_similaridade = [dict(row) for row in cursor.fetchall()]

    if not lista_de_contatos_para_similaridade:
        return {"status": "vazio", "dados": []}

    telefones_db_normalizados = [
        contato['telefone'] for contato in lista_de_contatos_para_similaridade
    ]

    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 5))
    tfidf_matrix = vectorizer.fit_transform(telefones_db_normalizados)
    query_vector = vectorizer.transform([query_normalizada])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    sugestoes_com_score = []
    for i, contato_simples in enumerate(lista_de_contatos_para_similaridade):
        score = cosine_similarities[i]
        # Limiar de sugestão fixado em 0.3, ideal para dados estruturados como telefones.
        if score > 0.3:
            sugestoes_com_score.append((score, contato_simples['rowid']))

    sugestoes_com_score.sort(key=operator.itemgetter(0), reverse=True)

    sugestoes_finais = []
    for score, rowid in sugestoes_com_score[:quant_max_amostras]:
        cursor.execute("SELECT * FROM contatos WHERE rowid = ?", (rowid,))
        contato_completo = dict(cursor.fetchone())
        sugestoes_finais.append(contato_completo)

    status_final = "sugestao" if sugestoes_finais else "vazio"
    return {"status": status_final, "dados": sugestoes_finais}


def buscar_por_endereco_com_sugestoes_sql(
        conn: sqlite3.Connection,
        endereco_query: str,
        quant_max_amostras: int = 10
) -> dict:
    """
    Busca contatos por endereço de forma otimizada usando SQL.

    A busca direta é feita no banco de dados usando LIKE e COLLATE NOCASE
    para ignorar maiúsculas/minúsculas de forma eficiente. Se a busca direta
    falhar, recorre a uma busca por similaridade de texto em Python.

    Args:
        conn (sqlite3.Connection): Objeto de conexão com o banco de dados SQLite.
        endereco_query (str): Endereço a ser buscado.
        quant_max_amostras (int, optional): Nº máximo de itens retornados. Padrão: 10.

    Returns:
        dict: Um dicionário com as chaves "status" e "dados".

    Raises:
        sqlite3.Error: Em caso de erro na consulta ao banco de dados.
    """
    if not endereco_query or not endereco_query.strip():
        return {"status": "vazio", "dados": []}

    # Configura a conexão para retornar dicionários, facilitando o manuseio dos dados
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query_sql_direta = f"""
                SELECT * FROM contatos 
                WHERE endereco LIKE ? COLLATE NOCASE
                LIMIT ?
            """

    # O termo de busca é envolvido por '%' para encontrar correspondências em qualquer parte do texto.
    termo_de_busca = f"%{endereco_query}%"

    cursor.execute(query_sql_direta, (termo_de_busca, quant_max_amostras))
    resultados_diretos = [dict(row) for row in cursor.fetchall()]

    if resultados_diretos:
        return {"status": "encontrado", "dados": resultados_diretos}

    # --- Etapa 2: Busca por Similaridade (Fallback) ---
    # Esta seção só é executada se a busca direta não encontrar resultados.

    # Buscamos todos os contatos para a análise de similaridade.
    # Esta é a parte computacionalmente mais cara e só é usada quando necessário.
    cursor.execute("SELECT * FROM contatos")
    lista_de_contatos = [dict(row) for row in cursor.fetchall()]

    if not lista_de_contatos:
        return {"status": "vazio", "dados": []}

    query_normalizada = _normalizar_texto(endereco_query)

    # Prepara os dados para a análise de similaridade
    enderecos_db = [contato.get('endereco', '') for contato in lista_de_contatos]
    enderecos_normalizados_db = [_normalizar_texto(end) for end in enderecos_db]

    # Calcula a similaridade usando TF-IDF e Cosseno
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
    tfidf_matrix = vectorizer.fit_transform(enderecos_normalizados_db)
    query_vector = vectorizer.transform([query_normalizada])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    sugestoes_com_score = [
        (cosine_similarities[i], contato)
        for i, contato in enumerate(lista_de_contatos)
        if cosine_similarities[i] > 0.1  # Limiar de similaridade para considerar uma sugestão
    ]

    # Ordena as sugestões pela pontuação de similaridade (mais alta primeiro)
    sugestoes_com_score.sort(key=operator.itemgetter(0), reverse=True)

    # Extrai apenas os dados dos contatos, limitando a quantidade
    sugestoes_finais = [contato for score, contato in sugestoes_com_score[:quant_max_amostras]]

    return {"status": "sugestao" if sugestoes_finais else "vazio", "dados": sugestoes_finais}


# ------------ BLOCO DE EXECUÇÃO PRINCIPAL ------------ #
if __name__ == "__main__":
    DB_FILE = "base_contatos.db"

    print("--- 1. Inicializando o Banco de Dados ---")
    conexao = inicializar_banco(DB_FILE)
    print(f"Banco de dados '{DB_FILE}' pronto para uso.")

    print("\n--- 2. Migrando dados do JSON para o SQLite ---")
    # A base_json vem do seu arquivo importado `base_dados_json.py`
    # migrar_json_para_sqlite(base_json, conexao)

    print("\n--- 3. Testando as Funções do Banco de Dados ---")

    print("\nAdicionando um novo contato:")
    sucesso, msg = adicionar_contato_sql(conexao, "MariaDB da Silva", "85987654321", "Rua dos Códigos, 123")
    print(f"Resultado: {msg}")

    print("\nTentando adicionar um contato com telefone duplicado:")
    sucesso, msg = adicionar_contato_sql(conexao, "Joana", "85987654321", "Avenida das Queries, 404")
    print(f"Resultado: {msg}")

    print("\nAlterando um contato existente:")
    # Assumindo que o telefone "85991604837" (do José Netinho no seu JSON) exista
    sucesso, msg = alterar_contato_sql(conexao, "85991604837", novo_nome="José Netinho de SQL")
    print(f"Resultado: {msg}")

    print("\nExcluindo um contato:")
    # Assumindo que o telefone "8599160454154837" (do João no seu JSON) exista
    excluido = excluir_contato_sql(conexao, "8599160454154837")
    print(f"Contato '8599160454154837' foi excluído? {'Sim' if excluido else 'Não'}")

    print("\nBuscando por nome com sugestão (erro de digitação):")
    resultados = buscar_por_nome_com_sugestoes_sql(conexao, "Jose Nteinho")
    print(f"Status da busca: {resultados['status']}")
    print("Dados encontrados/sugeridos:")
    for r in resultados['dados']:
        print(f"  - ID: {r['id']}, Nome: {r['nome']}, Tel: {r['telefone']}")

    # É crucial fechar a conexão ao final
    conexao.close()
    print("\nConexão com o banco de dados fechada.")
