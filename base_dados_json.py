import random
import json
from F_editar_sqlite import *

# --- 1. VARIÁVEIS COM DADOS PARA GERAÇÃO (POOLS DE DADOS) ---
# Adicione mais opções aqui para aumentar a variedade

primeiros_nomes = [
    "Ana", "Beatriz", "Carla", "Daniela", "Eduarda", "Fernanda", "Gabriela", "Helena",
    "Isabela", "Juliana", "Larissa", "Maria", "Natália", "Olívia", "Patrícia", "Raquel",
    "Sofia", "Tatiana", "Valentina", "Yasmin", "Antônio", "Bruno", "Carlos", "Daniel",
    "Eduardo", "Fábio", "Gustavo", "Henrique", "Igor", "João", "Lucas", "Marcelo",
    "Nicolas", "Otávio", "Pedro", "Rafael", "Sérgio", "Thiago", "Victor", "William"
]

sobrenomes = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
    "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes",
    "Soares", "Fernandes", "Vieira", "Barbosa", "Mendes", "Castro", "Rocha"
]

tipos_logradouro = ["Rua", "Av.", "Travessa", "Alameda"]

nomes_logradouro = [
    "das Flores", "das Acácias", "dos Cravos", "do Sol", "da Paz", "XV de Novembro",
    "Tiradentes", "Dom Manuel", "Santos Dumont", "Padre Cícero", "Borges de Melo",
    "Monsenhor Tabosa", "Barão do Rio Branco", "Duque de Caxias", "da Abolição"
]

bairros_fortaleza = [
    "Aldeota", "Meireles", "Mucuripe", "Praia de Iracema", "Centro", "Varjota",
    "Dionísio Torres", "Joaquim Távora", "Fátima", "Benfica", "Parangaba",
    "Messejana", "Cocó", "Edson Queiroz", "Papicu", "Sapiranga"
]


# --- 2. FUNÇÃO PARA GERAR UM CONTATO (SUBSTITUINDO DADOS FALTANTES POR None) ---

def gerar_contato():
    """Cria e retorna um dicionário de contato, substituindo dados por None para simular ausência."""

    # PASSO A: Gerar todos os dados possíveis primeiro
    nome_completo = f"{random.choice(primeiros_nomes)} {random.choice(sobrenomes)}"
    telefone_completo = f"55859{random.randint(8000, 9999)}{random.randint(1000, 9999)}"
    endereco_completo = (f"{random.choice(tipos_logradouro)} {random.choice(nomes_logradouro)}, "
                         f"{random.randint(1, 2500)} - {random.choice(bairros_fortaleza)}, Fortaleza")

    # PASSO B: Montar o contato com todos os dados
    contato = {
        "nome": nome_completo,
        "telefone": telefone_completo,
        "endereco": endereco_completo
    }

    # PASSO C: Lógica para tornar os dados mais realistas (com valores nulos)
    # A condição será verdadeira em 40% das vezes.
    if random.random() < 0.40:
        # Lista dos campos que podemos "anular" (nunca o nome)
        campos_modificaveis = ['telefone', 'endereco']

        # Sorteia quantos campos modificar: 1 ou 2
        quantidade_a_modificar = random.randint(1, 2)

        # Escolhe aleatoriamente quais campos da lista serão modificados
        campos_para_modificar = random.sample(campos_modificaveis, k=quantidade_a_modificar)

        # ### A MUDANÇA PRINCIPAL ESTÁ AQUI ###
        # Em vez de 'del contato[campo]', agora atribuímos 'None'
        for campo in campos_para_modificar:
            contato[campo] = None

    return contato


# --- 3. GERAÇÃO DA LISTA FINAL DE CONTATOS ---

# Defina aqui quantos contatos você quer gerar.
quantidade_a_gerar = 50

# Cria a lista de contatos chamando a função várias vezes
lista_de_contatos = [gerar_contato() for _ in range(quantidade_a_gerar)]

# Monta o dicionário final no formato solicitado
base_json_gerada = {
    "contatos": lista_de_contatos
}

# --- 4. EXIBIÇÃO DO RESULTADO ---

# Usamos o módulo 'json' para imprimir o resultado de forma organizada.
# O 'None' do Python é automaticamente convertido para 'null' no JSON.
print(json.dumps(base_json_gerada, indent=2, ensure_ascii=False))

conexao = inicializar_banco()
migrar_json_para_sqlite(base_json_gerada,conexao)