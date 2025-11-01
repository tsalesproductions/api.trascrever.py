import sys
import os

# Adicionar o diretório da aplicação ao path
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'api_transcrever', '3.7', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Adicionar diretório do projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importar a aplicação Flask
from app import app as application
