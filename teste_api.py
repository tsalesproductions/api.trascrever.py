# Exemplo de teste da API
import requests

# URL da API
url = "http://localhost:5000/transcrever"

# Caminho do arquivo de áudio
audio_file = "audio.ogg"  # Substitua pelo caminho do seu arquivo

# Fazer a requisição
with open(audio_file, 'rb') as f:
    files = {'audio': f}
    response = requests.post(url, files=files)

# Mostrar resultado
print("Status Code:", response.status_code)
print("Resposta:", response.json())

if response.json().get('success'):
    print("\n✅ Transcrição:", response.json().get('texto'))
else:
    print("\n❌ Erro:", response.json().get('error'))
