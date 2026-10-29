import sys 
import site 
# Ruta de tu proyecto 
sys.path.insert(0, '/var/www/html/Sentinel') 
# Ruta de las librerías de tu entorno virtual (si usas uno) 
sys.path.insert(0, '/var/www/html/Sentinel/venv/lib/python3.14/site-packages') 
# Importa tu aplicación (cámbialo si tu archivo principal se llama diferente a app.py) 
from run import app as application
