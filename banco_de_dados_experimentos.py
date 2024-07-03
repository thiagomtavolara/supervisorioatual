import sqlite3

# Função para conectar ao banco de dados
def conectar_banco_dados(nome_banco_de_dados):
    conexao = sqlite3.connect(nome_banco_de_dados)
    return conexao

# Função para ativar cursor ao banco de dados
def cursor_banco_dados(conexao):
    cursor = conexao.cursor()
    return cursor

# Função para criar o banco de dados(se já tiver ele só ignora)
def criar_banco_dados(nome_banco_de_dados, nome_tabela):
    conexao = conectar_banco_dados(nome_banco_de_dados)
    cursor = cursor_banco_dados(conexao)
    
    # Criar uma tabela se não existir
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {nome_tabela} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            T0 REAL NOT NULL,
            T1 REAL NOT NULL,
            T2 REAL NOT NULL,
            T3 REAL NOT NULL,
            P0 REAL NOT NULL,
            P1 REAL NOT NULL,
            P2 REAL NOT NULL,
            P3 REAL NOT NULL,
            B1 REAL NOT NULL,
            B2 REAL NOT NULL,
            B3 REAL NOT NULL
        )
    ''')
    
    conexao.commit()
    conexao.close()

# Função para inserir no banco de dados
def inserir_banco_dados(nome_banco_de_dados, nome_tabela, T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3):
    conexao = conectar_banco_dados(nome_banco_de_dados)
    cursor = cursor_banco_dados(conexao)

    # Obter o ID máximo atual na tabela
    cursor.execute(f'SELECT MAX(id) FROM {nome_tabela}')
    max_id = cursor.fetchone()[0]
    # Se não houver registros na tabela, define max_id como 0
    if max_id is None:
        max_id = 0

    # Incrementa o ID máximo para obter o próximo ID
    next_id = max_id + 1

    # Inserir na tabela com o ID calculado
    cursor.execute(f'''
        INSERT INTO {nome_tabela} (id, T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (next_id, T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3))
    conexao.commit()
    conexao.close()

# Função para consultar o ultimo id no banco de dados
def consultar_ultimo_id_banco_dados(nome_banco_de_dados, nome_tabela):
    conexao = conectar_banco_dados(nome_banco_de_dados)
    cursor = cursor_banco_dados(conexao)
    cursor.execute(f'SELECT T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3 FROM {nome_tabela} ORDER BY id DESC LIMIT 1')
    dados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return dados

# Função para consultar todos os id no banco de dados
def consultar_todos_id_banco_dados(nome_banco_de_dados, nome_tabela):
    conexao = conectar_banco_dados(nome_banco_de_dados)
    cursor = cursor_banco_dados(conexao)
    cursor.execute(f'SELECT * FROM {nome_tabela}')
    dados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return dados

# Função para atualizar no banco de dados
def atualizar_banco_dados(nome_banco_de_dados, nome_tabela, id, T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3):
    conexao = conectar_banco_dados(nome_banco_de_dados)
    cursor = cursor_banco_dados(conexao)
    cursor.execute(f''' 
        UPDATE {nome_tabela} 
        SET T0 = ?, T1 = ?, T2 = ?, T3 = ?, P0 = ?, P1 = ?, P2 = ?, P3 = ?, B1 = ?, B2 = ?, B3 = ? 
        WHERE id = ? 
    ''', (T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3, id))
    conexao.commit()
    cursor.close()
    conexao.close()

# Função para deletar no banco de dados
def deletar_banco_dados(nome_banco_de_dados, nome_tabela, id):
    conexao = conectar_banco_dados(nome_banco_de_dados)
    cursor = cursor_banco_dados(conexao)
    cursor.execute(f'''DELETE FROM {nome_tabela} WHERE id = ?''', (id,))
    # After deletion, update the IDs
    cursor.execute(f'''UPDATE {nome_tabela} SET id = id - 1 WHERE id > ?''', (id,))
    conexao.commit()
    cursor.close()
    conexao.close()

# Função para imprimir todos os id no banco de dados
def imprimir_banco_dados(nome_banco_de_dados, nome_tabela):
    for row in consultar_todos_id_banco_dados(nome_banco_de_dados, nome_tabela):
        print(row)

# Função para obter o numero do último ID
def obter_numero_do_ultimo_id(nome_banco_de_dados, nome_tabela):
    conexao = conectar_banco_dados(nome_banco_de_dados)
    cursor = cursor_banco_dados(conexao)
    cursor.execute(f'SELECT MAX(id) FROM {nome_tabela}')
    ultimo_id = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return ultimo_id

# Exemplo de uso das funções
nome_banco_de_dados = 'dados_experimentos.db'
nome_tabela = '"27-06-2024"'  # Ajuste conforme necessário

#criar_banco_dados(nome_banco_de_dados, nome_tabela)
#inserir_banco_dados(nome_banco_de_dados, nome_tabela, 90, 90, 90, 90, 50, 26, 60, 30, 82, 56, 10)
#imprimir_banco_dados(nome_banco_de_dados, nome_tabela)
