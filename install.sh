# instrucciones para correr el backend
# se espera que esto sea abierto en una terminal en la misma carpeta que install.sh

FOLDER=./API/BackEnd
BACKEND_PORT=4000

# o algo por el estilo si el usuario no tiene pip instalado
sudo apt install python3-pip

# instala pipenv por si acaso
pip install pipenv --user

# se mueve a la carpeta front
cd $FOLDER

# instalo las dependencias del proyecto administrado por pipenv
pipenv install

# entro a la shell del proyecto
pipenv shell

# esto hay que pegarlo manualmente porque "pipenv shell" crea una sub shell
# con el --debug activado para actualizar los cambios
# con el -p ponemos el port manualmente
# esto es para correr el backend en desarrollo
pipenv run flask run --debug -p $BACKEND_PORT