from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Configura CORS para permitir todas las solicitudes desde cualquier origen y permitir métodos específicos
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

# Configuración de la base de datos
def db_config():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='oddyjachi',
            database='db_foro'
        )
        return connection
    except Error as err:
        print(f"Error connecting to the database: {err}")
        return None

# Buscar usuario por email
def find_user_by_email(email):
    conn = db_config()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Registro de usuario
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    conn = db_config()
    if conn is None:
        return jsonify({'message': 'Conexión a la base de datos fallida'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO users (name, email, password) VALUES (%s, %s, %s)''',
                       (name, email, password))  # Almacenar la contraseña como texto plano (no recomendado)
        conn.commit()
        return jsonify({'message': 'Usuario registrado correctamente'}), 200
    except Error as err:
        return jsonify({'message': f'Error al registrar el usuario: {err}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = find_user_by_email(email)

    if user:
        if user['password'] == password:  # Comprueba la contraseña
            return jsonify({"message": "Inicio de sesión exitoso"}), 200
        else:
            print(f"Contraseña incorrecta para el usuario: {email}")  # Añadir log
            return jsonify({"message": "Credenciales inválidas"}), 401
    else:
        print(f"Usuario no encontrado: {email}")  # Añadir log
        return jsonify({"message": "Credenciales inválidas"}), 401

@app.route('/api/comments', methods=['POST'])
def add_comment():
    data = request.json
    comment = data.get('comment')
    
    if not comment:
        return jsonify({"message": "No comment provided"}), 400
    
    conn = db_config()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO comments (comment) VALUES (%s)', (comment,))
        conn.commit()
        return jsonify({"message": "Comment added successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/comments/view', methods=['GET'])
def get_comments():
    conn = db_config()
    if conn is None:
        return jsonify({"message": "Error connecting to database"}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        # Realizar el JOIN con la tabla de usuarios
        cursor.execute('''
            SELECT c.id, c.comment, u.name 
            FROM comments c 
            LEFT JOIN users u ON c.user_id = u.id
        ''')
        comments = cursor.fetchall()

        # Filtrar solo los comentarios, sus nombres y el id
        filtered_comments = [{'id': c['id'], 'comment': c['comment'], 'user_name': c['name']} for c in comments]
        
        if not filtered_comments:
            return jsonify({"message": "No comments found"}), 404
        
        return jsonify(filtered_comments), 200
    except Exception as e:
        print(f"Error executing query: {str(e)}")  # Imprime el error en la consola
        return jsonify({"message": f"Error executing query: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/comments/<int:comment_id>', methods=['OPTIONS', 'DELETE'])
def delete_comment(comment_id):
    if request.method == 'OPTIONS':
        # Responde a las solicitudes preflight (OPTIONS)
        return jsonify({"message": "OK"}), 200
    
    conn = db_config()
    if conn is None:
        return jsonify({"message": "Error connecting to database"}), 500

    cursor = conn.cursor()

    try:
        # Verificamos si el comentario existe
        cursor.execute('SELECT * FROM comments WHERE id = %s', (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            return jsonify({"message": "Comment not found"}), 404

        # Eliminamos el comentario
        cursor.execute('DELETE FROM comments WHERE id = %s', (comment_id,))
        conn.commit()

        return jsonify({"message": "Comment deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
def edit_comment(comment_id):
    data = request.get_json()
    new_comment = data.get('comment')

    if not new_comment:
        return jsonify({"message": "No comment provided"}), 400

    conn = db_config()
    if conn is None:
        return jsonify({"message": "Error connecting to database"}), 500

    cursor = conn.cursor()

    try:
        # Verificar si el comentario existe
        cursor.execute('SELECT * FROM comments WHERE id = %s', (comment_id,))
        comment = cursor.fetchone()

        if not comment:
            return jsonify({"message": "Comment not found"}), 404

        # Actualizar el comentario
        cursor.execute('UPDATE comments SET comment = %s WHERE id = %s', (new_comment, comment_id))
        conn.commit()

        return jsonify({"message": "Comment updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5009)
