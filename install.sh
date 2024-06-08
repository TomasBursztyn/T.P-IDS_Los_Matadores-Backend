# instrucciones para correr el front (un boceto inicial)

FRONT_FOLDER=./Front

# instala pipenv por si acaso
pip install pipenv --user

# se mueve a la carpeta front
cd FRONT_FOLDER

# instalo las dependencias del proyecto administrado por pipenv
pipenv install

# entro a la shell del proyecto
pipenv shell

# corro el front con el --debug activado para actualizar los cambios
# ojo esto solo para desarrollo (no meter en produccion con --debug activado)
pipenv run flask run --debug

# TODO: Habria que añadir las instrucciones para que cualquier persona que abra
# el backend, corra el script y se le instale todo lo necesario sin saber
# como funciona. Y en el Pipfile tambien
# Que se le instale el pip (si no lo tiene), todas las dependencias,
# (hace falta agregar flask) 
pip install flask_sqlalchemy
pip install mysql-connector-python