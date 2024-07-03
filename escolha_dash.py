import sqlite3


def get_data_from_db(date):
    conn = sqlite3.connect('dados_experimentos.db')
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
            SELECT id, T0, T1, T2, T3, P0, P1, P2, P3, B1, B2, B3 FROM '{date}'
        ''')
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        conn.close()
        return None
    conn.close()

    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'T0': row[1],
            'T1': row[2],
            'T2': row[3],
            'T3': row[4],
            'P0': row[5],
            'P1': row[6],
            'P2': row[7],
            'P3': row[8],
            'B1': row[9],
            'B2': row[10],
            'B3': row[11]
        })
    return data

