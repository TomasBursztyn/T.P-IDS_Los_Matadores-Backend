from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__)
engine = create_engine("mysql+mysqlconnector://root:123456@localhost:3307/tp_ids_db") #cambiar puerto al de tu base de datos, y nombre despues del /


# -----------------------------------------------------------------------------------------------------------------------------------------------------

# Endpoints:

# Endpoints POST para introducir valores en las tablas:
# POST habitacion
@app.route('/cargar_habitacion', methods = ['POST'])
def cargar_habitacion():
    conn = engine.connect()
    nueva_habitacion = request.get_json()
    #Se crea la query en base a los datos pasados por el endpoint.
    #Los mismos deben viajar en el body en formato JSON
    query = f"""INSERT INTO habitaciones (tipo_habitacion, precio_por_noche, cantidad_personas) VALUES ('{nueva_habitacion["tipo_habitacion"]}','{nueva_habitacion["precio_por_noche"]}', '{nueva_habitacion["cantidad_personas"]}');"""
    try:
        result = conn.execute(text(query))
        #Una vez ejecutada la consulta, se debe hacer commit de la misma para que
        #se aplique en la base de datos.
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    return jsonify({'message': 'se ha agregado correctamente' + query}), 201

# POST cliente
@app.route('/cargar_clientes', methods = ['POST'])
def cargar_cliente():
    conn = engine.connect()
    nuevo_cliente = request.get_json()
    query = f"""INSERT INTO personas (nombre_persona, telefono_persona, email_persona, dni_persona) VALUES ('{nuevo_cliente["nombre_persona"]}', '{nuevo_cliente["telefono_persona"]}', '{nuevo_cliente["email_persona"]}', '{nuevo_cliente["dni_persona"]}');"""
    try:
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    return jsonify({'message': 'se ha agregado correctamente' + query}), 201

#POST reserva
@app.route('/cargar_reserva', methods = ['POST'])
def cargar_reserva():
    conn = engine.connect()
    nueva_reserva = request.get_json()
    salida = nueva_reserva["fecha_salida"].split("-")
    entrada = nueva_reserva["fecha_inicio"].split("-")
    conseguir_precio =  f"""SELECT precio_por_noche FROM habitaciones WHERE id_habitacion = {nueva_reserva["id_habitaciones"]};"""
    
    try:
        result = conn.execute(text(conseguir_precio))
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    if int(salida[1]) > int(entrada[1]):
        cant_noches = (int(salida[1]) - int(entrada[1])) * 30 + int(salida[2]) - int(entrada[2])
    else:
        cant_noches = int(salida[2]) - int(entrada[2])
    #validar first
    nueva_reserva["total_a_pagar"] = cant_noches * result.first()[0]

    query = f"""INSERT INTO reservas (id_habitaciones, id_personas, fecha_inicio, fecha_salida, total_a_pagar) VALUES ('{nueva_reserva["id_habitaciones"]}', '{nueva_reserva["id_personas"]}', '{nueva_reserva["fecha_inicio"]}', '{nueva_reserva["fecha_salida"]}', '{nueva_reserva["total_a_pagar"]}');"""
    try:
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    return jsonify({'message': 'se ha agregado correctamente' + query}), 201


# Endpoints GET para recibir todo lo que contienen las tablas:
# GET habitaciones
@app.route('/mostrar_habitaciones', methods = ['GET'])
def get_habitaciones():
    conn = engine.connect()
    
    query = "SELECT * FROM habitaciones;"
    try:
        #Se debe usar text para poder adecuarla al execute de mysql-connector
        result = conn.execute(text(query))
        #Se hace commit de la consulta (acá no estoy seguro si es necesario para un select, sí es necesario para un insert!)
        conn.close() #Cerramos la conexion con la base de datos
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    #Se preparan los datos para ser mostrador como json
    data = []
    for row in result:
        entity = {}
        entity['id_habitacion'] = row.id_habitacion
        entity['tipo_habitacion'] = row.tipo_habitacion
        entity['precio_por_noche'] = row.precio_por_noche
        entity['cantidad_personas'] = row.cantidad_personas
        data.append(entity)

    return jsonify(data), 200

# GET clientes
@app.route('/mostrar_clientes', methods = ['GET'])
def get_clientes():
    conn = engine.connect()
    
    query = "SELECT * FROM personas;"
    try:
        result = conn.execute(text(query))
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    data = []
    for row in result:
        entity = {}
        entity['id_persona'] = row.id_persona
        entity['nombre_persona'] = row.nombre_persona
        entity['telefono_persona'] = row.telefono_persona
        entity['email_persona'] = row.email_persona
        entity['dni_persona'] = row.dni_persona
        data.append(entity)

    return jsonify(data), 200

# GET reservas
@app.route('/mostrar_reservas', methods = ['GET'])
def get_reservas():
    conn = engine.connect()
    
    query = "SELECT * FROM reservas;"
    try:
        result = conn.execute(text(query))
        conn.close() 
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    data = []
    for row in result:
        entity = {}
        entity['id_reserva'] = row.id_reserva
        entity['id_habitaciones'] = row.id_habitaciones
        entity['id_personas'] = row.id_personas
        entity['fecha_inicio'] = row.fecha_inicio
        entity['fecha_salida'] = row.fecha_salida
        entity['total_a_pagar'] = row.total_a_pagar

        data.append(entity)

    return jsonify(data), 200

# Endpoint GET par abuscar por fechas
#GET fechas reservas

@app.route('/mostrar_reservas/<fecha_inicio>/<fecha_fin>', methods = ['GET'])
def get_reservas_por_fechas(fecha_inicio, fecha_fin):
    conn = engine.connect()
    query = f"""SELECT * FROM reservas WHERE fecha_inicio >= '{fecha_inicio}' AND fecha_salida <= '{fecha_fin}';"""
            
    try:
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    data = []
    for row in result:
        entity = {}
        entity['id_reserva'] = row.id_reserva
        entity['id_habitaciones'] = row.id_habitaciones
        entity['id_personas'] = row.id_personas
        entity['fecha_inicio'] = row.fecha_inicio
        entity['fecha_salida'] = row.fecha_salida
        entity['total_a_pagar'] = row.total_a_pagar

        data.append(entity)

    return jsonify(data), 200


# Endpoints GET para buscar por id
#GET id habitacion
@app.route('/habitacion/<id>', methods = ['GET'])
def get_habitacion(id):
    conn = engine.connect()
    query = f"""SELECT * FROM habitaciones WHERE id_habitacion = {id};"""
            
    try:
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    if result.rowcount !=0:
        data = {}
        row = result.first()
        data['id_habitacion'] = row[0]
        data['tipo_habitacion'] = row[1]
        data['precio_por_noche'] = row[2]
        data['cantidad_personas'] = row[3]
        return jsonify(data), 200

    return jsonify({"message": "La habitación no existe"}), 404

#GET id clientes
@app.route('/clientes/<id>', methods = ['GET'])
def get_clientes_id(id):
    conn = engine.connect()
    query = f"""SELECT * FROM personas WHERE id_persona = {id};"""
            
    try:
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    if result.rowcount !=0:
        data = {}
        row = result.first()
        data['id_persona'] = row[0]
        data['nombre_persona'] = row[1]
        data['telefono_persona'] = row[2]
        data['email_persona'] = row[3]
        data['dni_persona'] = row[4]
        return jsonify(data), 200

    return jsonify({"message": "El usuario no existe"}), 404

#GET dni clientes
@app.route('/clientes_dni/<dni>', methods = ['GET'])
def get_clientes_dni(dni):
    conn = engine.connect()
    query = f"""SELECT * FROM personas WHERE dni_persona = {dni};"""
            
    try:
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    if result.rowcount !=0:
        data = {}
        row = result.first()
        data['id_persona'] = row[0]
        data['nombre_persona'] = row[1]
        data['telefono_persona'] = row[2]
        data['email_persona'] = row[3]
        data['dni_persona'] = row[4]
        return jsonify(data), 200

    return jsonify({"message": "El usuario no existe"}), 404

#GET reserva por dni_persona
@app.route('/reserva_dni/<dni>', methods = ['GET'])
def get_reserva_por_dni(dni):
    conn = engine.connect()
    query = f"""SELECT reservas.*
    FROM reservas
    JOIN personas ON reservas.id_personas = personas.id_persona
    WHERE personas.dni_persona = {dni};
    """
    try:
        result = conn.execute(text(query))
        conn.close()
        if result.rowcount != 0 :
            data = []
            for row in result:
                entity = {}
                entity['id_reserva'] = row.id_reserva
                entity['id_habitaciones'] = row.id_habitaciones
                entity['id_personas'] = row.id_personas
                entity['fecha_inicio'] = row.fecha_inicio
                entity['fecha_salida'] = row.fecha_salida
                entity['total_a_pagar'] = row.total_a_pagar

                data.append(entity)
            return jsonify(data), 200

        else:
            conn.close()
            return None
    except SQLAlchemyError as err:
        return str(err.__cause__)


#GET id reservas
@app.route('/mostrar_reservas/<id>', methods = ['GET'])
def get_reservas_id(id):
    conn = engine.connect()
    query = f"""SELECT * FROM reservas WHERE id_reserva = {id};"""
            
    try:
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    if result.rowcount !=0:
        data = {}
        row = result.first()
        data['id_reserva'] = row[0]
        data['id_habitaciones'] = row[1]
        data['id_personas'] = row[2]
        data['fecha_inicio'] = row[3]
        data['fecha_salida'] = row[4]
        data['total_a_pagar'] = row[5]
        return jsonify(data), 200

    return jsonify({"message": "La reserva no existe"}), 404


# Endpoints DELETE
# Delete de clientes(personas)
@app.route('/clientes/<id>', methods = ['DELETE'])  
def delete_clientes(id):
    conn = engine.connect()
    query = f"""DELETE FROM personas WHERE id_persona = {id};"""
            
    validation_query = f"SELECT * FROM personas WHERE id_persona = {id}"
    try:
        val_result = conn.execute(text(validation_query))
        if val_result.rowcount != 0 :
            result = conn.execute(text(query))
            conn.commit()
            conn.close()
        else:
            conn.close()
            return jsonify({"message": "El usuario no existe"}), 404
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    return jsonify({'message': 'Se ha eliminado correctamente'}), 202


# Endpoint DELETE para eliminar una habitacion de la tabla_habitaciones por medio del id_habitacion
@app.route('/habitaciones/<id>', methods = ['DELETE'])  
def delete_habitaciones(id):
    conn = engine.connect()
    query = f"""DELETE FROM habitaciones WHERE id_habitacion = {id};"""
            
    validation_query = f"SELECT * FROM habitaciones WHERE id_habitacion = {id}"
    try:
        val_result = conn.execute(text(validation_query))
        if val_result.rowcount != 0 :
            result = conn.execute(text(query))
            conn.commit()
            conn.close()
        else:
            conn.close()
            return jsonify({"message": "La habitacion no existe"}), 404
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    return jsonify({'message': 'Se ha eliminado correctamente'}), 202

# Borrar reserva
@app.route('/reservas/<id>', methods = ['DELETE'])  
def delete_reserva(id):
    conn = engine.connect()
    query = f"""DELETE FROM reservas WHERE id_reserva = {id};"""
            
    validation_query = f"SELECT * FROM reservas WHERE id_reserva = {id}"
    try:
        val_result = conn.execute(text(validation_query))
        if val_result.rowcount != 0 :
            result = conn.execute(text(query))
            conn.commit()
            conn.close()
        else:
            conn.close()
            return jsonify({"message": "La reserva no existe"}), 404
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    return jsonify({'message': 'Se ha eliminado correctamente'}), 202


# Endpoints PATCH
# Editar habitacion

@app.route('/editar_habitacion/<id>', methods = ['PATCH'])
def editar_habitacion(id):
    conn = engine.connect()
    datos_habitacion = request.get_json()
    query = f"""
        UPDATE habitaciones
        SET {', '.join([f"{key} = '{value}'" for key, value in datos_habitacion.items()])}
        WHERE id_habitacion = {id};
    """
    
    validation_query = "SELECT * FROM habitaciones WHERE id_habitacion = {id};".format(id=id)
    try:
        val_result = conn.execute(text(validation_query))
        if val_result.rowcount != 0:
            result = conn.execute(text(query))
            conn.commit()
            conn.close()
        else:
            conn.close()
            return jsonify({"message": "La habitación no existe"}), 404
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error: ' + str(err.__cause__)}), 500

    return jsonify({'message': 'Se ha modificado correctamente'}), 200


if __name__ == "__main__":
    app.run("127.0.0.1", port="5000", debug=True)