from flask import Flask, render_template, request, jsonify,g,redirect,url_for,session,flash
from flask_socketio import SocketIO
#from errores import ErrorHandlers
#from viewsVecino import VecinosView
#from enviarMensajes import *
from auth import auth
#from puertoSerial import *
from flask_session import Session

from database import nombreBaseDatos
from logger import registroLog

import threading
import sqlite3
import os 

from datetime import datetime

app = Flask(__name__)

obtenerFechaHora = datetime.now()
formatearFecha = obtenerFechaHora.strftime("%d_%m_%_Y _%H:_%M:_%S")

#app.config["SECRET_KEY"] = "1234567890"

# almacenar la sesion en el sistema
#app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#app.register_blueprint(VecinosView)
#app.register_blueprint(auth)

#app.register_blueprint(ViewMensajes)

#socketio = SocketIO(app)
#ErrorHandlers.register(app,socketio)
#reading_thread = None

# realizar la consulta de login en sqlite 
def queryLogin(usuario,passwordGuardar):
    conexion = sqlite3.connect(nombreBaseDatos)
    cursor = conexion.cursor()  
    cursor.execute("select * from usuarios where usuario=? and password=?",(usuario,passwordGuardar,))
    ejecutar = cursor.fetchall()
    conexion.close()
    return ejecutar

@app.route('/login',methods=['POST'])
def login():
    if "usuarioSesion" not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        usuario = request.form.get("txtUsuario")
        passwordGuardar = request.form.get("txtPassword")
        ejecutar = queryLogin(usuario,passwordGuardar)

        # validar que el usuario y password sean correctos
        if len(ejecutar) > 0:
            # se crea la sesion de que existe el usuario
            session["usuarioSesion"]=usuario
            # se accede al primer resultado y primera columna
            session["idUsuario"]=ejecutar[0][0]
            usuarioSes = session["usuarioSesion"]
            idUsuarioSes = session["idUsuario"]
            flash("Inicio de sesion exitoso", "success")
            return render_template("main/index.html",registroExitoso=True,usuarioSesion=usuarioSes,idUsuario=idUsuarioSes)
        else:
            flash("Usuario o contraseña incorrectos","error")
            return render_template("auth/login.html",registroExitoso=False)

       
@app.route('/fmrLogin',methods=['GET','POST'])
def frmLogin():
    if "usuarioSesion" in session:
        idUsuarioSes = session["idUsuario"]
        return render_template("main/index.html",idUsuario=idUsuarioSes,usuarioSesion=session["usuarioSesion"])
    else:
        flash("No has iniciado sesión")
        registroLog.info("El usuario no ha iniciado sesion redirigido al login.")
        return render_template("auth/login.html")
    
@app.route('/frmRegistroCuenta',methods=['GET','POST'])
def frmRegistroCuenta():
    return render_template("auth/frmRegistroCuenta.html")

@app.route('/registroCuenta',methods=["POST"])
def registroCuenta():
    if request.method == "POST":
        usuarioGuardar = request.form.get("txtUsuario")
        passwordGuardar = request.form.get("txtPassword")
        
        if not usuarioGuardar or not passwordGuardar:
            flash("Debes ingresar un usuario y una contraseña","error")
            return render_template("auth/frmRegistroCuenta.html")
        else:
            with sqlite3.connect(nombreBaseDatos) as conexion:
                cursor = conexion.cursor()
                cursor.execute("INSERT INTO usuarios(usuario,password) VALUES (?, ?)",(usuarioGuardar,passwordGuardar))
                conexion.commit()
                registroLog.info("El usuario se ha guardado correctamente.")

                return render_template("auth/registroExitoso.html")
    else:
        return render_template("auth/frmRegistroCuenta.html")


# cerrar la sesion del usuario
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop("usuarioSesion",None)
    flash("Se ha cerrado la sesion correctamente","sucess")
    return redirect(url_for("frmLogin"))

@app.route('/',methods=['GET','POST'])
def index():
    if "usuarioSesion" in session:
        idUsuarioSes = session["idUsuario"]
        return render_template("main/index.html",usuarioSesion=session["usuarioSesion"],idUsuario=idUsuarioSes)
    else:
        flash("No has iniciado sesión")
    return render_template("auth/login.html")

if __name__ == '__main__':
    app.run(debug=True)