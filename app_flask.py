from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from F_editar_sqlite import *
from F_chat_gpt import *
from F_envio_mensagens import *
from prompt import prompt_comand

# --- Configuração Inicial ---
app = Flask(__name__)
DB_NAME = "base_contatos.db"

historico_chat = [
    {"role": "system",
     "content": prompt_comand}
]

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# --- Rotas da Aplicação Web (Páginas) ---

@app.route('/')
def index():
    conn = get_db_connection()
    contatos = conn.execute('SELECT id, nome, telefone, endereco FROM contatos ORDER BY nome').fetchall()
    conn.close()
    return render_template('index.html', contatos=contatos)


@app.route('/update_manual', methods=['POST'])
def update_manual():
    form_data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()
    ids = form_data.getlist('id')
    nomes = form_data.getlist('nome')
    telefones = form_data.getlist('telefone')
    enderecos = form_data.getlist('endereco')
    for i in range(len(ids)):
        try:
            cursor.execute(
                "UPDATE contatos SET nome = ?, telefone = ?, endereco = ? WHERE id = ?",
                (nomes[i], telefones[i], enderecos[i], ids[i])
            )
        except sqlite3.Error as e:
            print(f"Erro ao atualizar o contato ID {ids[i]}: {e}")
            conn.rollback()
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# --- Endpoints da API para o JavaScript (Ações em tempo real) ---

@app.route('/api/get_contacts', methods=['GET'])
def get_contacts():
    conn = get_db_connection()
    contatos_db = conn.execute('SELECT id, nome, telefone, endereco FROM contatos ORDER BY nome').fetchall()
    conn.close()
    contatos_list = [dict(row) for row in contatos_db]
    return jsonify(contatos_list)


@app.route('/api/chatbot', methods=['POST'])
def handle_chatbot_message():
    data = request.get_json()
    user_message = data.get('message')
    conn = get_db_connection()
    try:
        # 1. Agora capturamos a resposta em texto E o sinalizador
        assistant_response, needs_refresh = assistente_gerenciador_de_contatos(
            conn=conn, texto_user=user_message, historico_conversa=historico_chat
        )

        # 2. Enviamos ambos para o frontend no JSON
        return jsonify({
            'reply': assistant_response,
            'refresh_table': needs_refresh
        })
    except Exception as e:
        return jsonify({'error': str(e), 'refresh_table': False}), 500
    finally:
        conn.close()


# Rota para adicionar um contato
@app.route('/api/add_contact', methods=['POST'])
def add_contact():
    data = request.get_json()
    nome = data.get('nome')
    telefone = data.get('telefone')
    endereco = data.get('endereco')

    if not nome or not telefone:
        return jsonify({'success': False, 'message': 'Nome e Telefone são obrigatórios.'}), 400

    conn = get_db_connection()
    try:
        # Usando sua função já existente!
        success, message = adicionar_contato_sql(conn, nome=nome, telefone=telefone, endereco=endereco)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()


# NOVIDADE: Rota para excluir um contato
@app.route('/api/delete_contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    conn = get_db_connection()
    try:
        # Usando sua função já existente!
        # A função `excluir_contato_sql` espera o telefone, então precisamos buscá-lo primeiro.
        # Seria ideal refatorar `excluir_contato_sql` para aceitar ID, mas vamos manter assim por enquanto.
        cursor = conn.cursor()
        cursor.execute("SELECT telefone FROM contatos WHERE id = ?", (contact_id,))
        contact = cursor.fetchone()

        if not contact:
            return jsonify({'success': False, 'message': 'Contato não encontrado.'}), 404

        # Como sua função `excluir_contato_sql` espera o número, vamos usá-lo.
        # Se você alterá-la para usar o ID, esta busca não seria mais necessária.
        success = excluir_contato_sql(conn, numero_de_telefone=contact['telefone'])

        if success:
            return jsonify({'success': True, 'message': 'Contato excluído com sucesso.'})
        else:
            return jsonify({'success': False, 'message': 'Falha ao excluir o contato.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()


# --- Bloco de Execução ---
if __name__ == '__main__':
    conn = inicializar_banco(DB_NAME)
    conn.close()
    app.run(debug=True)