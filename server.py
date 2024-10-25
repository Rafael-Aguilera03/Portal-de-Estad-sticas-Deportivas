from flask import Flask, flash, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__, static_url_path='/static')
load_dotenv()

# Conectar a MySQL
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

# Configuración de Flask-Login
app.secret_key = "mysecretkey"
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor inicia sesión para acceder a esta página."

# Modelo de usuario
class User(UserMixin):
    def __init__(self, email, contraseña):
        self.id = email
        self.email = email
        self.contraseña = contraseña

@login_manager.user_loader
def load_user(email):
    with mysql.connection.cursor() as cur:
        cur.execute("SELECT correo, contraseña FROM users WHERE correo = %s", (email,))
        user = cur.fetchone()
        if user:
            return User(user[0], user[1])
    return None

# Rutas

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            with mysql.connection.cursor() as cur:
                cur.execute("SELECT correo, contraseña FROM users WHERE correo = %s", (email,))
                user = cur.fetchone()
                if user:
                    user_obj = User(user[0], user[1])
                    if password == user_obj.contraseña:
                        login_user(user_obj)
                        flash('¡Inicio de sesión exitoso!', 'success')
                        return redirect(url_for('inicio'))
                    else:
                        error = "Credenciales inválidas. Por favor, inténtalo de nuevo."
                else:
                    error = "Usted no está cargado en este sistema"
        except Exception as e:
            error = f"Error al acceder a la base de datos: {str(e)}"
            print(f"Error: {str(e)}")

    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        pais = request.form['pais']
        
        try:
            with mysql.connection.cursor() as cur:
                cur.execute("INSERT INTO users (nombre_user, correo, contraseña, pais) VALUES (%s, %s, %s, %s)",
                            (username, email, password, pais))
                mysql.connection.commit()
            flash('¡Registro exitoso!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error al registrar usuario en la base de datos: {str(e)}")
            flash('Error al registrar usuario', 'error')
    
    return render_template('register.html')


@app.route('/users', methods=['GET'])
@login_required
def manage_users():
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT nombre_user, correo, pais FROM users")
            users = cur.fetchall()
            print(f"Usuarios encontrados: {users}")  
    except Exception as e:
        print(f"Error al obtener usuarios: {str(e)}")
        users = []

    return render_template('users.html', users=users)


@app.route('/edit_user/<correo>', methods=['GET', 'POST'])
@login_required
def edit_user(correo):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        pais = request.form['pais']
        
        try:
            with mysql.connection.cursor() as cur:
                cur.execute("UPDATE users SET nombre_user = %s, correo = %s, pais = %s WHERE correo = %s",
                            (username, email, pais, correo))
                mysql.connection.commit()
            flash('¡Usuario actualizado exitosamente!', 'success')
            return redirect(url_for('manage_users'))
        except Exception as e:
            print(f"Error al actualizar usuario: {str(e)}")
            flash('Error al actualizar usuario', 'error')
            return redirect(url_for('edit_user', correo=correo))  # Volver a mostrar el formulario en caso de error
    
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT nombre_user, correo, pais FROM users WHERE correo = %s", (correo,))
            user = cur.fetchone()
            if user is None:
                flash('Usuario no encontrado', 'error')
                return redirect(url_for('manage_users'))
    except Exception as e:
        print(f"Error al obtener usuario: {str(e)}")
        flash('Error al obtener usuario', 'error')
        return redirect(url_for('manage_users'))

    return render_template('edit_user.html', user=user)


@app.route('/delete_user/<correo>', methods=['GET'])
@login_required
def delete_user(correo):
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("DELETE FROM users WHERE correo = %s", (correo,))
            mysql.connection.commit()
        flash('¡Usuario eliminado exitosamente!', 'success')
    except Exception as e:
        print(f"Error al eliminar usuario: {str(e)}")
        flash('Error al eliminar usuario', 'error')
    
    return redirect(url_for('manage_users'))

@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        pais = request.form['pais']
        
        try:
            with mysql.connection.cursor() as cur:
                cur.execute("INSERT INTO users (nombre_user, correo, contraseña, pais) VALUES (%s, %s, %s, %s)",
                            (username, email, password, pais))
                mysql.connection.commit()
            flash('¡Usuario creado exitosamente!', 'success')
            return redirect(url_for('manage_users'))
        except Exception as e:
            print(f"Error al crear usuario: {str(e)}")
            flash('Error al crear usuario', 'error')
    
    return render_template('create_user.html')

@app.route('/')
def main():
    return redirect(url_for('login'))

# Ruta de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

@app.route('/inicio')
@login_required
def inicio():
    return render_template('inicio.html')

@app.route('/selecciones')
@login_required
def selecciones():
    return render_template('selecciones.html')

@app.route('/jugadores')
@login_required
def jugadores():
    return render_template('jugadores.html')

@app.route('/resultados')
@login_required
def resultados():
    return render_template('resultados.html')

@app.route('/argentina')
@login_required
def argentina():
    return render_template('argentina.html')

@app.route('/brasil')
@login_required
def brasil():
    return render_template('brasil.html')

@app.route('/uruguay')
@login_required
def uruguay():
    return render_template('uruguay.html')

@app.route('/chile')
@login_required
def chile():
    return render_template('chile.html')

@app.route('/colombia')
@login_required
def colombia():
    return render_template('colombia.html')

@app.route('/messi')
@login_required
def messi():
    return render_template('messi.html')

@app.route('/vinicius')
@login_required
def vinicius():
    return render_template('vinicius.html')

@app.route('/valverde')
@login_required
def valverde():
    return render_template('valverde.html')

@app.route('/james')
@login_required
def james():
    return render_template('james.html')

@app.route('/sanchez')
@login_required
def sanchez():
    return render_template('sanchez.html')

@app.route('/caicedo')
@login_required
def caicedo():
    return render_template('caicedo.html')

@app.route('/pulisic')
@login_required
def pulisic():
    return render_template('pulisic.html')

@app.route('/davies')
@login_required
def davies():
    return render_template('davies.html')

@app.route('/alvarez')
@login_required
def alvarez():
    return render_template('alvarez.html')

@app.route('/soteldo')
@login_required
def soteldo():
    return render_template('soteldo.html')



# Iniciar el servidor
if __name__ == '__main__':
    app.run(port=9000, debug=True)
