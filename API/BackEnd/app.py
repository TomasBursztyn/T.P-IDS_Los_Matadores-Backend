from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__)
engine = create_engine("mysql+mysqlconnector://@localhost:3306/TP_IDS") #cambiar puerto al de tu base de datos, y nombre despues del /


@app.route('/muestreo', methods = ['GET'])
def users():
    conn = engine.connect()
    
    query = "SELECT * FROM tabla_personas;"
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
        entity['id_reserva'] = row.id_reserva
        entity['nombre'] = row.nombre
        entity['apellido'] = row.apellido
        entity['DNI'] = row.DNI
        entity['email'] = row.email
        entity['total_a_pagar'] = row.total_a_pagar
        data.append(entity)

    return jsonify(data), 200


@app.route('/crear_usuario', methods = ['POST'])
def crear_usuario():
    conn = engine.connect()
    nuevo_usuario = request.get_json()
    #Se crea la query en base a los datos pasados por el endpoint.
    #Los mismos deben viajar en el body en formato JSON
    query = f"""INSERT INTO tabla_personas (id_reserva, nombre, apellido, DNI, email, total_a_pagar) VALUES ('{nuevo_usuario["id_reserva"]}','{nuevo_usuario["nombre"]}', '{nuevo_usuario["apellido"]}', '{nuevo_usuario["DNI"]}', '{nuevo_usuario["email"]}', '{nuevo_usuario["total_a_pagar"]}');"""
    try:
        result = conn.execute(text(query))
        #Una vez ejecutada la consulta, se debe hacer commit de la misma para que
        #se aplique en la base de datos.
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    return jsonify({'message': 'se ha agregado correctamente' + query}), 201


@app.route('/usuario/<id>', methods = ['PATCH'])
def actualizar_usuario(id):
    conn = engine.connect()
    mod_user = request.get_json()
    #De la misma manera que con el metodo POST los datos a modificar deberán
    #Ser enviados por medio del body de la request
    query = f"""UPDATE tabla_personas SET nombre = '{mod_user['nombre']}'
                {f", email = '{mod_user['email']}'" if "email" in mod_user else ""}
                WHERE id_reserva = {id};
            """
    query_validation = f"SELECT * FROM tabla_personas WHERE id_reserva = {id};"
    try:
        val_result = conn.execute(text(query_validation))
        if val_result.rowcount!=0:
            result = conn.execute(text(query))
            conn.commit()
            conn.close()
        else:
            conn.close()
            return jsonify({'message': "El usuario no existe"}), 404
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500

    return jsonify({'message': 'se ha modificado correctamente' + query}), 200


@app.route('/usuario/<id>', methods = ['GET'])
def get_usuario(id):
    conn = engine.connect()
    query = f"""SELECT *
            FROM tabla_personas
            WHERE id_reserva = {id};
            """
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
        data['nombre'] = row[1]
        data['apellido'] = row[2]
        data['DNI'] = row[3]
        data['email'] = row[4]
        data['total_a_pagar'] = row[5]
        return jsonify(data), 200

    return jsonify({"message": "El usuario no existe"}), 404


@app.route('/usuario/<id>', methods = ['DELETE'])
def delete_usuario(id):
    conn = engine.connect()
    query = f"""DELETE FROM tabla_personas
            WHERE id_reserva = {id};
            """
    validation_query = f"SELECT * FROM tabla_personas WHERE id_reserva = {id}"
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

@app.route('/reservas', methods = ['GET']) #Muestra todas las habitaciones de reservas
def reservas():
    conn = engine.connect()
    
    query = "SELECT * FROM tabla_reservas;"
    try:
        result = conn.execute(text(query))
        conn.close() 
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    data = []
    for row in result:
        entity = {}
        entity['id'] = row.id
        entity['check_in'] = row.check_in
        entity['check_out'] = row.check_out
        entity['horario_reserva'] = row.horario_reserva
    #   entity['DNI'] = row.DNI             aca podriamos insertarlas para ver
    #   entity['apellido'] = row.apellido   quien hizo la reserva
        data.append(entity)

    return jsonify(data), 200

@app.route('/reservar', methods = ['POST']) # Crear reserva
def crear_reserva():
    conn = engine.connect()
    nueva_reserva = request.get_json()
    query = f"""INSERT INTO tabla_reservas (id, check_in, check_out, horario_reserva) VALUES ('{nueva_reserva["id"]}','{nueva_reserva["check_in"]}', '{nueva_reserva["check_out"]}', '{nueva_reserva["horario_reserva"]}');"""
    try:
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        return jsonify({'message': 'Se ha producido un error' + str(err.__cause__)}), 500
    
    return jsonify({'message': 'se ha agregado correctamente' + query}), 201

@app.route('/reservas/<id>', methods = ['DELETE'])  # Borrar reserva por id
def delete_reservas(id):
    conn = engine.connect()
    query = f"""DELETE FROM tabla_reservas
            WHERE id = {id};
            """
    validation_query = f"SELECT * FROM tabla_reservas WHERE id = {id}"
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




if __name__ == "__main__":
    app.run("127.0.0.1", port="5000", debug=True)