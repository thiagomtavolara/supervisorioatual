import sqlite3


# Função para conectar ao banco de dados


def conectar_banco_dados():
    conexao = sqlite3.connect('dados_planta.db')
    return conexao

# Função para ativar cursor ao banco de dados


def cursor_banco_dados(conexao):
    cursor = conexao.cursor()
    return cursor


# Função para criar o banco de dados(se já tiver ele só ignora)


def criar_banco_dados():

    conexao = conectar_banco_dados()
    cursor = cursor_banco_dados(conexao)

    # Criar uma tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variaveis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            T0_min REAL NOT NULL,
            T0_max REAL NOT NULL,
            T1_min REAL NOT NULL,
            T1_max REAL NOT NULL,
            T2_min REAL NOT NULL,
            T2_max REAL NOT NULL,
            T3_min REAL NOT NULL,
            T3_max REAL NOT NULL,
            P0_min REAL NOT NULL,
            P0_max REAL NOT NULL,
            P1_min REAL NOT NULL,
            P1_max REAL NOT NULL,
            P2_min REAL NOT NULL,
            P2_max REAL NOT NULL,
            P3_min REAL NOT NULL,
            P3_max REAL NOT NULL,
            B1_min REAL NOT NULL,
            B1_max REAL NOT NULL,
            B2_min REAL NOT NULL,
            B2_max REAL NOT NULL,
            B3_min REAL NOT NULL,
            B3_max REAL NOT NULL,
            Patamar REAL NOT NULL,
            Quanto REAL NOT NULL,
            Tempoparafim REAL NOT NULL,
            Muda_sp REAL NOT NULL 
            
        )
    ''')

    conexao.commit()
    conexao.close()


# Função para inserir no banco de dados


def inserir_banco_dados(T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3):
    conexao = conectar_banco_dados()
    cursor = cursor_banco_dados(conexao)

    # Obter o ID máximo atual na tabela
    cursor.execute('SELECT MAX(id) FROM variaveis')
    max_id = cursor.fetchone()[0]

    # Se não houver registros na tabela, define max_id como 0
    if max_id is None:
        max_id = 0

    # Incrementa o ID máximo para obter o próximo ID
    next_id = max_id + 1

    # Inserir na tabela com o ID calculado
    cursor.execute('''
        INSERT INTO variaveis (id, T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (next_id, T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3))
    conexao.commit()
    conexao.close()


# Função para consultar o ultimo id no banco de dados
def consultar_ultimo_id_banco_dados():
    conexao = conectar_banco_dados()
    cursor = cursor_banco_dados(conexao)
    cursor.execute(
        'SELECT T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3 FROM variaveis ORDER BY id DESC LIMIT 1')
    dados = cursor.fetchall()
    cursor.close()
    conexao.commit()
    conexao.close()
    return dados

# Função para consultar todos os id no banco de dados
def consultar_todos_id_banco_dados():
    conexao = conectar_banco_dados()
    cursor = cursor_banco_dados(conexao)
    cursor.execute('SELECT * FROM variaveis')
    dados = cursor.fetchall()
    cursor.close()
    conexao.commit()
    conexao.close()
    return dados



# Função para atualizar no banco de dados

def atualizar_banco_dados(id, T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3):
    conexao = conectar_banco_dados()
    cursor = cursor_banco_dados(conexao)
    cursor.execute(''' 
        UPDATE variaveis 
        SET T0 = ?, T1 = ?, T2 = ?, T3 = ?, P0 = ?, P1 = ?, P2 = ?, P3 = ?, B1 = ?, B2 = ?, B3 = ? 
        WHERE id = ? 
    ''', (T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3, id))
    conexao.commit()
    cursor.close()
    conexao.close()

# Função para deletar no banco de dados


def deletar_banco_dados(id):
    conexao = conectar_banco_dados()
    cursor = cursor_banco_dados(conexao)
    cursor.execute('''DELETE FROM variaveis WHERE id = ?''', (id,))
    # After deletion, update the IDs
    # Update IDs of subsequent records
    cursor.execute('''UPDATE variaveis SET id = id - 1 WHERE id > ?''', (id,))
    conexao.commit()
    cursor.close()
    conexao.close()

# Função para imprimir todos os id no banco de dados

def imprimir_banco_dados():
    for row in consultar_todos_id_banco_dados():
        print(row)

# Função para obter o numero do último ID
def obter_numero_do_ultimo_id():
    conexao = conectar_banco_dados()
    cursor = cursor_banco_dados(conexao)
    cursor.execute('SELECT MAX(id) FROM variaveis')
    ultimo_id = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return ultimo_id

#criar_banco_dados()
inserir_banco_dados(20, 22, 25.2, 22.8, 10.1, 9.8, 9.9, 10.2, 3.5, 4.0, 3.8)
#atualizar_banco_dados(1, 10, 62, 25.2, 22.8, 10.1, 9.8, 9.9, 10.2, 3.5, 4.0, 3.8)
#deletar_banco_dados(1)
#imprimir_banco_dados()



#print(obter_numero_do_ultimo_id())
