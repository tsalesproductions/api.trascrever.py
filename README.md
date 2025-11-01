# API de Transcrição de Áudios do WhatsApp

API REST em Python/Flask para transcrever áudios do WhatsApp para texto em português (pt-BR).

## 📋 Requisitos

- Python 3.8 ou superior
- FFmpeg (necessário para conversão de áudios)

### Instalar FFmpeg

**Windows:**
1. Baixe do site oficial: https://ffmpeg.org/download.html
2. Extraia e adicione ao PATH do sistema
3. Ou use: `choco install ffmpeg` (se tiver Chocolatey)

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**MacOS:**
```bash
brew install ffmpeg
```

## 🚀 Instalação

1. Clone ou navegue até o diretório do projeto:
```bash
cd d:\Repositorios\python\api_transcrever
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## ▶️ Como Usar

### 1. Iniciar a API

```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`

### 2. Endpoints Disponíveis

#### Health Check
```
GET /health
```

Resposta:
```json
{
  "status": "ok",
  "message": "API de transcrição funcionando"
}
```

#### Transcrever Áudio
```
POST /transcrever
```

**Parâmetros:**
- `audio` (file): Arquivo de áudio (formatos: ogg, oga, mp3, wav, opus, m4a)

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:5000/transcrever \
  -F "audio=@caminho/do/audio.ogg"
```

**Exemplo com Python (requests):**
```python
import requests

url = "http://localhost:5000/transcrever"
files = {'audio': open('audio.ogg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Exemplo com JavaScript (fetch):**
```javascript
const formData = new FormData();
formData.append('audio', audioFile); // audioFile é um File object

fetch('http://localhost:5000/transcrever', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Resposta de Sucesso:**
```json
{
  "success": true,
  "texto": "olá este é o texto transcrito do áudio",
  "message": "Áudio transcrito com sucesso"
}
```

**Resposta de Erro:**
```json
{
  "success": false,
  "error": "Descrição do erro"
}
```

## 🎯 Integração com WhatsApp

### Exemplo de integração típica:

1. **Recebe áudio do WhatsApp** (através do webhook da sua plataforma)
2. **Baixa o arquivo de áudio** (usando a API do WhatsApp Business)
3. **Envia para esta API**:

```javascript
// Exemplo Node.js
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function transcreverAudioWhatsApp(caminhoAudio) {
  const formData = new FormData();
  formData.append('audio', fs.createReadStream(caminhoAudio));
  
  try {
    const response = await axios.post('http://localhost:5000/transcrever', formData, {
      headers: formData.getHeaders()
    });
    
    if (response.data.success) {
      console.log('Transcrição:', response.data.texto);
      return response.data.texto;
    } else {
      console.error('Erro:', response.data.error);
      return null;
    }
  } catch (error) {
    console.error('Erro na requisição:', error);
    return null;
  }
}
```

## ⚙️ Configurações

Você pode modificar as seguintes configurações no arquivo `app.py`:

- `MAX_CONTENT_LENGTH`: Tamanho máximo do arquivo (padrão: 16MB)
- `ALLOWED_EXTENSIONS`: Formatos de áudio permitidos
- `port`: Porta da API (padrão: 5000)
- `host`: Host da API (padrão: 0.0.0.0)

## 🐛 Problemas Comuns

### "Erro ao converter áudio"
- Verifique se o FFmpeg está instalado corretamente
- Execute: `ffmpeg -version` no terminal para confirmar

### "Não foi possível entender o áudio"
- Verifique a qualidade do áudio
- Certifique-se de que há fala no áudio
- O áudio precisa estar em português

### "Erro no serviço de reconhecimento"
- Verifique sua conexão com a internet
- A API do Google Speech Recognition tem limites de uso

## 📝 Notas

- A API usa o Google Speech Recognition (gratuito com limitações)
- Áudios muito longos podem demorar para processar
- A transcrição é feita em português do Brasil (pt-BR)
- Arquivos temporários são automaticamente removidos após o processamento

## 🔒 Produção

Para uso em produção, considere:

1. **Usar um servidor WSGI** (gunicorn, uWSGI):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Adicionar autenticação** (API key, JWT, etc.)
3. **Usar HTTPS**
4. **Adicionar rate limiting**
5. **Monitoramento e logs**
6. **Configurar CORS** se necessário:
```python
from flask_cors import CORS
CORS(app)
```

## 📄 Licença

Este projeto é open source e está disponível para uso livre.
