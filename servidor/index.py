
from flask import Flask,jsonify,request,Response,render_template
from datetime import datetime;

API_KEY = 'jW2fwtlHdLabxdxlOxd1fHedTF8DNGADhWumWqlu'


# Darle un nombre a la variable y que se llamara en el main
app = Flask(__name__)

diccionarioRoverCamaras =  {
    "FHAZ":"Front Hazard Avoidance Camera",
    "RHAZ":"Rear Hazard Avoidance Camera",
    "MAST":"Mast Camera",
    "CHEMCAM":"Chemistry and Camera Complex",
    "MAHLI":"Mars Hand Lens Imager",
    "MARDI":"Mars Descent Imager",
    "NAVCAM":"Navigation Camera",
    "PANCAM":"Panoramic Camera",
    "MINITES":"Miniature Thermal Emission Spectrometer (Mini-TES)"	
}

# Para mandar a llamar al el archivo de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Manda a llamar la página de apod: que muestra la imagen del día
@app.route('/apod')
def apod_route():
    # apod() es la función que se encuentra en el archivo apod.py
    return apod()

# Se utiliza en filtrarImagenes.js
@app.route('/llamar_apod/<string:parametro>',methods=['POST'])
def llamar_apod(parametro):
    resultado = photos(parametro)
    return resultado

@app.route('/exploracionPlanetaria')
def explP_route():
    return exploracionPlanetaria()

@app.route('/MarsRover')
def MarsRover_route():
    return render_template('MarsRover/photos.html',diccionarioRoverCamaras=diccionarioRoverCamaras)

@app.route('/galeriaMultimedia')
def galeryMultimedia():
    return render_template('galeriaMultimedia/galeriaMultimedia.html')

@app.route('/galeriaMultimediaFiltrarBusqueda/<string:parametro1>/<string:parametro2>',methods=['POST'])
def galeryMultimedia_route(parametro1,parametro2):
    return buscarGaleriaMultimedia(parametro1,parametro2)

@app.errorhandler(404)
def not_found(error):
    return render_template('error/404.html',error=error)

def apod():
    url = 'https://api.nasa.gov/planetary/apod'
    # obtener fecha actual de mi servidor, NO de la NASA
    fechaActual = datetime.now().strftime('%Y-%m-%d')
    parametros = {'api_key':API_KEY}
    response = request.get(url,params=parametros)
    
    try:
        if response.status_code == 200:
            datos = response.json()
            urlAPOD = datos['url']        
            explanation = datos['explanation']
            titleImage = datos['title']   
            #copyright = datos['copyright']        
            return render_template('APOD.html',explanation=explanation,titleImage=titleImage,urlAPOD=urlAPOD,copyright="No disponible",date=fechaActual)   
        else:
            return render_template('APOD.html',errorAPI="Error en la API")
        # en caso que se coloque un dato que no existe en la API mostrarlo
    except KeyError as e:
        mensaje_error = f"La clave '{e.args[0]}' no existe en el diccionario."
        return jsonify({'error': mensaje_error}), 400

def buscarGaleriaMultimedia(inputBusqueda,tipoBusqueda):
    url ="https://images-api.nasa.gov/search"
    fechaActual = datetime.now().strftime('%Y')
    parametros = {'q':inputBusqueda,'media_type':tipoBusqueda,'year_start':1920,'year_end':fechaActual}
        
    response = request.get(url,params=parametros)
    #try:
    if response.status_code == 200:
        datos = response.json()
                
        # Se envia el diccionario con los datos de la API y en galeriaMultimedia.js se recupera la informacion
        return jsonify(datos)
    elif response.status_code == 400:
        return jsonify({'error':'Parámetro no válido en la API'}), 400
    else:
        return jsonify({'error':'Error en la API'}), 500
        #except KeyError as e:
        #mensaje_error = f"La clave '{e.args[0]}' no existe en el diccionario."
        #return jsonify({'error': mensaje_error}), 400
        #return jsonify({'error':'Parámetro no válido en la API'}), 400

def photos(nombreCamara):
    url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
    #url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos";
    #camar = nombreCamara.lower()
    
    parametros = {'sol':1000,'camera':nombreCamara,'api_key':API_KEY}
    response = request.get(url,params=parametros)
    try:
        if response.status_code == 200:
            datos = response.json()
           
            # https://api.nasa.gov nombres de las camaras

            return datos
        else:
            return render_template('MarsRover/photos.html',errorAPI="Error en la API")
        # en caso que se coloque un dato que no existe en la API mostrarlo
    except KeyError as e:
        mensaje_error = f"La clave '{e.args[0]}' no existe en el diccionario."
        return jsonify({'error': mensaje_error}), 400

def exploracionPlanetaria():
    return render_template('exoplanetArchive.html')

if __name__ == '__main__':
    app.run(debug=True)
