from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__)

# Constante QUERY que se utiliza a lo largo de la aplicacion
QUERY = ""
# Constante BACKEND_PORT que lo utiliza Flask para correr la aplicacion
BACKEND_PORT = 4000
# Constantes que necesita pythonanywhere que utilice sqlalchemy para poder conectarse bien
# Se hizo con la ayuda de la documentacion:
# https://help.pythonanywhere.com/pages/UsingSQLAlchemywithMySQL
# Hace falta especificar el parametro pool_recycle, en la documentacion se explica
USERNAME = "LOS1MATADORESAPI"
PASSWORD = "databasecontra123#"
HOSTNAME = "LOS1MATADORESAPI.mysql.pythonanywhere-services.com"
DB_NAME = "LOS1MATADORESAPI$default"
# Este seria el engine que se utilizaria en produccion
engine = create_engine(
    f"mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DB_NAME}", pool_recycle=300
)

# Constante DB_PORT necesaria para sqlalchemy pueda conectarse bien en desarrollo
# DB_PORT = "3308"
# Este seria el engine que se utilizaria en desarrollo
# engine = create_engine(f"mysql+mysqlconnector://root:123@localhost:{DB_PORT}/{DB_NAME}")


# POST cargar_habitacion
@app.route("/cargar_habitacion", methods=["POST"])
def cargar_habitacion():
    conn = engine.connect()
    habitacion = request.get_json()
    # Se crea la query en base a los datos pasados por el endpoint.
    # Los mismos deben viajar en el body en formato JSON
    QUERY = f"""INSERT INTO habitaciones (tipo_habitacion, precio_por_noche, cantidad_personas) VALUES ('{habitacion["tipo_habitacion"]}','{habitacion["precio_por_noche"]}', '{habitacion["cantidad_personas"]}');"""

    try:
        conn.execute(text(QUERY))
        # Una vez ejecutada la consulta, se debe hacer commit de la misma para
        # que se aplique en la base de datos.
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un INSERT en cargar_habitacion: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    return jsonify({"message": "Se ha cargado correctamente a la habitacion"}), 201


# POST cargar_clientes
@app.route("/cargar_clientes", methods=["POST"])
def cargar_cliente():
    conn = engine.connect()
    nuevo_cliente = request.get_json()
    QUERY = f"""INSERT INTO personas (nombre_persona, telefono_persona, email_persona, dni_persona) VALUES ('{nuevo_cliente["nombre_persona"]}', '{nuevo_cliente["telefono_persona"]}', '{nuevo_cliente["email_persona"]}', '{nuevo_cliente["dni_persona"]}');"""

    try:
        conn.execute(text(QUERY))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un INSERT en cargar_cliente: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    return jsonify({"message": "Se ha cargado correctamente al cliente"}), 201


# POST cargar_reserva
@app.route("/cargar_reserva", methods=["POST"])
def cargar_reserva():
    conn = engine.connect()
    reserva = request.get_json()
    # Fechas estan en formato ["año", "mes", "dia"]
    fecha_salida = reserva["fecha_salida"].split("-")
    fecha_inicio = reserva["fecha_inicio"].split("-")
    QUERY = f"""SELECT precio_por_noche FROM habitaciones WHERE id_habitacion = {reserva["id_habitaciones"]};"""

    try:
        result = conn.execute(text(QUERY))
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en cargar_reserva: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    # Si estan en distinto mes entonces:
    # Sumar la diferencia de meses multiplicada por 30
    # Sumar los dias de la fecha de salida
    # Restar los dias de la fecha de inicio
    if int(fecha_salida[1]) > int(fecha_inicio[1]):
        cant_noches = (
            (int(fecha_salida[1]) - int(fecha_inicio[1])) * 30
            + int(fecha_salida[2])
            - int(fecha_inicio[2])
        )
    # Si estan en el mismo mes entonces:
    # Restar a los dias de la fecha de salida, los dias de la fecha de inicio
    else:
        cant_noches = int(fecha_salida[2]) - int(fecha_inicio[2])

    # Habria que validar si result.first()[0] existe antes de usarlo
    reserva["total_a_pagar"] = cant_noches * result.first()[0]
    QUERY = f"""INSERT INTO reservas (id_habitaciones, id_personas, fecha_inicio, fecha_salida, total_a_pagar) VALUES ('{reserva["id_habitaciones"]}', '{reserva["id_personas"]}', '{reserva["fecha_inicio"]}', '{reserva["fecha_salida"]}', '{reserva["total_a_pagar"]}');"""

    try:
        conn.execute(text(QUERY))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un INSERT en cargar_reserva: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    return jsonify({"message": "Se ha cargado correctamente la reserva"}), 201


# GET mostrar_habitaciones
@app.route("/mostrar_habitaciones", methods=["GET"])
def get_habitaciones():
    conn = engine.connect()
    QUERY = "SELECT * FROM habitaciones;"

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_habitaciones: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    # Se preparan los datos para ser mostrados como JSON
    data = []
    for row in result:
        entity = {}
        entity["id_habitacion"] = row.id_habitacion
        entity["tipo_habitacion"] = row.tipo_habitacion
        entity["precio_por_noche"] = row.precio_por_noche
        entity["cantidad_personas"] = row.cantidad_personas

        data.append(entity)

    return jsonify(data), 200


# GET mostrar_clientes
@app.route("/mostrar_clientes", methods=["GET"])
def get_clientes():
    conn = engine.connect()
    QUERY = "SELECT * FROM personas;"

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_clientes: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    data = []
    for row in result:
        entity = {}
        entity["id_persona"] = row.id_persona
        entity["nombre_persona"] = row.nombre_persona
        entity["telefono_persona"] = row.telefono_persona
        entity["email_persona"] = row.email_persona
        entity["dni_persona"] = row.dni_persona

        data.append(entity)

    return jsonify(data), 200


# GET mostrar_reservas
@app.route("/mostrar_reservas", methods=["GET"])
def get_reservas():
    conn = engine.connect()
    QUERY = "SELECT * FROM reservas;"

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_reservas: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    data = []
    for row in result:
        entity = {}
        entity["id_reserva"] = row.id_reserva
        entity["id_habitaciones"] = row.id_habitaciones
        entity["id_personas"] = row.id_personas
        entity["fecha_inicio"] = row.fecha_inicio
        entity["fecha_salida"] = row.fecha_salida
        entity["total_a_pagar"] = row.total_a_pagar

        data.append(entity)

    return jsonify(data), 200


# GET mostrar_habitaciones_disponibles por fechas de inicio y fin y cantidad de personas
@app.route(
    "/mostrar_habitaciones_disponibles/<fecha_inicio>/<fecha_fin>/<cantidad_personas>",
    methods=["GET"],
)
def get_habitaciones_disponibles(fecha_inicio, fecha_fin, cantidad_personas):
    conn = engine.connect()
    QUERY = f"""SELECT * FROM habitaciones WHERE cantidad_personas >= {cantidad_personas} AND id_habitacion NOT IN (SELECT id_habitaciones FROM reservas WHERE fecha_inicio <= '{fecha_fin}' AND fecha_salida >= '{fecha_inicio}');"""

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_habitaciones_disponibles: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    if result.rowcount != 0:
        data = []
        for row in result:
            entity = {}
            entity["id_habitacion"] = row.id_habitacion
            entity["tipo_habitacion"] = row.tipo_habitacion
            entity["precio_por_noche"] = row.precio_por_noche
            entity["cantidad_personas"] = row.cantidad_personas

            data.append(entity)

        return jsonify(data), 200

    return []


# GET habitacion por id
@app.route("/habitacion/<id>", methods=["GET"])
def get_habitacion(id):
    conn = engine.connect()
    QUERY = f"""SELECT * FROM habitaciones WHERE id_habitacion = {id};"""

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_habitacion: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    if result.rowcount != 0:
        data = {}
        row = result.first()
        data["id_habitacion"] = row[0]
        data["tipo_habitacion"] = row[1]
        data["precio_por_noche"] = row[2]
        data["cantidad_personas"] = row[3]
        return jsonify(data), 200

    return jsonify({"message": f"La habitación con id {id} no existe"}), 404


# GET clientes por id
@app.route("/clientes/<id>", methods=["GET"])
def get_clientes_id(id):
    conn = engine.connect()
    QUERY = f"""SELECT * FROM personas WHERE id_persona = {id};"""

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_clientes_id: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    if result.rowcount != 0:
        data = {}
        row = result.first()
        data["id_persona"] = row[0]
        data["nombre_persona"] = row[1]
        data["telefono_persona"] = row[2]
        data["email_persona"] = row[3]
        data["dni_persona"] = row[4]
        return jsonify(data), 200

    return jsonify({"message": f"El usuario con id {id} no existe"}), 404


# GET clientes_dni por dni
@app.route("/clientes_dni/<dni>", methods=["GET"])
def get_clientes_dni(dni):
    conn = engine.connect()
    QUERY = f"""SELECT * FROM personas WHERE dni_persona = {dni};"""

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_clientes_dni: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    if result.rowcount != 0:
        data = {}
        row = result.first()
        data["id_persona"] = row[0]
        data["nombre_persona"] = row[1]
        data["telefono_persona"] = row[2]
        data["email_persona"] = row[3]
        data["dni_persona"] = row[4]
        return jsonify(data), 200

    return jsonify({"message": f"El usuario con id {id} no existe"}), 404


# GET reserva_dni por DNI
@app.route("/reserva_dni/<dni>", methods=["GET"])
def get_reserva_por_dni(dni):
    conn = engine.connect()
    QUERY = f"""SELECT reservas.* FROM reservas JOIN personas ON reservas.id_personas = personas.id_persona WHERE personas.dni_persona = {dni};"""

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_reserva_por_dni: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    if result.rowcount != 0:
        data = []
        for row in result:
            entity = {}
            entity["id_reserva"] = row.id_reserva
            entity["id_habitaciones"] = row.id_habitaciones
            entity["id_personas"] = row.id_personas
            entity["fecha_inicio"] = row.fecha_inicio
            entity["fecha_salida"] = row.fecha_salida
            entity["total_a_pagar"] = row.total_a_pagar
            data.append(entity)
        return jsonify(data), 200

    return []


# GET mostrar_reservas por id
@app.route("/mostrar_reservas/<id>", methods=["GET"])
def get_reservas_id(id):
    conn = engine.connect()
    QUERY = f"""SELECT * FROM reservas WHERE id_reserva = {id};"""

    try:
        result = conn.execute(text(QUERY))
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en get_reservas_id: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    if result.rowcount != 0:
        data = {}
        row = result.first()
        data["id_reserva"] = row[0]
        data["id_habitaciones"] = row[1]
        data["id_personas"] = row[2]
        data["fecha_inicio"] = row[3]
        data["fecha_salida"] = row[4]
        data["total_a_pagar"] = row[5]
        return jsonify(data), 200

    return jsonify({"message": f"La reserva con id {id} no existe"}), 404


# DELETE clientes por id
@app.route("/clientes/<id>", methods=["DELETE"])
def delete_clientes(id):
    conn = engine.connect()
    QUERY = f"SELECT * FROM personas WHERE id_persona = {id}"

    # Validamos que exista el cliente antes de borrarlo
    try:
        validation_result = conn.execute(text(QUERY))
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en delete_clientes: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    # Si no existe el cliente devolvemos un mensaje con codigo 404
    if validation_result.rowcount == 0:
        conn.close()
        return jsonify({"message": f"El usuario con id {id} no existe"}), 404

    try:
        QUERY = f"DELETE FROM personas WHERE id_persona = {id};"
        conn.execute(text(QUERY))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un DELETE en cargar_reserva: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    return (
        jsonify({"message": f"Se ha eliminado correctamente al cliente con id {id}"}),
        202,
    )


# DELETE habitaciones por id_habitacion
@app.route("/habitaciones/<id>", methods=["DELETE"])
def delete_habitaciones(id):
    conn = engine.connect()
    QUERY = f"SELECT * FROM habitaciones WHERE id_habitacion = {id}"

    # Validamos que exista la habitacion antes de borrarla
    try:
        validation_result = conn.execute(text(QUERY))
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en delete_habitaciones: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    # Si no existe la habitacion devolvemos un mensaje con codigo 404
    if validation_result.rowcount == 0:
        conn.close()
        return jsonify({"message": f"La habitacion con id {id} no existe"}), 404

    try:
        QUERY = f"DELETE FROM habitaciones WHERE id_habitacion = {id};"
        conn.execute(text(QUERY))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un DELETE en delete_habitaciones: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    return (
        jsonify(
            {"message": f"Se ha eliminado correctamente a la habitacion con id {id}"}
        ),
        202,
    )


# DELETE reservas por id_reserva
@app.route("/reservas/<id>", methods=["DELETE"])
def delete_reserva(id):
    conn = engine.connect()
    QUERY = f"SELECT * FROM reservas WHERE id_reserva = {id}"

    # Validamos que exista la reserva antes de borrarla
    try:
        validation_result = conn.execute(text(QUERY))
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en delete_reserva: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    # Si no existe la reserva devolvemos un mensaje con codigo 404
    if validation_result.rowcount == 0:
        conn.close()
        return jsonify({"message": f"La reserva con id {id} no existe"}), 404

    try:
        QUERY = f"DELETE FROM reservas WHERE id_reserva = {id};"
        conn.execute(text(QUERY))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un DELETE en delete_reserva: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    return (
        jsonify({"message": f"Se ha eliminado correctamente a la reserva con id {id}"}),
        202,
    )


# PATCH editar_habitacion por id_habitacion
@app.route("/editar_habitacion/<id>", methods=["PATCH"])
def editar_habitacion(id):
    conn = engine.connect()
    datos_habitacion = request.get_json()
    QUERY = f"SELECT * FROM habitaciones WHERE id_habitacion = {id};"

    # Validamos que exista la habitacion antes de modificarla
    try:
        validation_result = conn.execute(text(QUERY))
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un SELECT en editar_habitacion: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    # Si no existe la habitacion devolvemos un mensaje con codigo 404
    if validation_result.rowcount == 0:
        conn.close()
        return jsonify({"message": f"La habitación con id {id} no existe"}), 404

    try:
        QUERY = f"""UPDATE habitaciones SET {', '.join([f"{key} = '{value}'" for key, value in datos_habitacion.items()])} WHERE id_habitacion = {id};"""
        conn.execute(text(QUERY))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        message = f"Error con la base de datos, al hacer un UPDATE en editar_habitacion: {str(err.__cause__)}"
        return (
            jsonify({"message": message}),
            500,
        )

    return (
        jsonify(
            {"message": f"Se ha modificado correctamente a la habitacion con id {id}"}
        ),
        200,
    )


if __name__ == "__main__":
    app.run("127.0.0.1", port=BACKEND_PORT, debug=True)
