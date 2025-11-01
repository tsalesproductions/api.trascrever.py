# GUIA COMPLETO: Deploy da API no cPanel com Passenger

## 📋 Pré-requisitos no cPanel

1. **Acesso SSH** (necessário para instalar FFmpeg)
2. **Python App** habilitado no cPanel
3. **Passenger** instalado (já aparece na sua imagem)

---

## 🚀 PASSO A PASSO COMPLETO

### 1️⃣ **Configurar a Aplicação Python no cPanel**

Acesse: **cPanel → Setup Python App** e preencha:

| Campo | Valor |
|-------|-------|
| **Python version** | `2.7.18` (ou a mais recente disponível, idealmente 3.8+) |
| **Application root** | `/home/tutor121/api_transcrever` (ou onde você subir os arquivos) |
| **Application URL** | `pip-audio-transcrever` (como na sua imagem) |
| **Application startup file** | `passenger_wsgi.py` |
| **Application Entry point** | `application` |
| **Passenger log file** | `/home/tutor121/logs/pip-audio-transcrever.log` |

> ⚠️ **IMPORTANTE**: O cPanel vai criar automaticamente um **ambiente virtual** para você!

Clique em **CREATE** e aguarde a criação.

---

### 2️⃣ **Upload dos Arquivos**

Via **File Manager** ou **FTP**, envie estes arquivos para `/home/tutor121/api_transcrever/`:

```
api_transcrever/
├── passenger_wsgi.py  ← CRÍTICO! Arquivo criado
├── app.py
├── requirements.txt
└── .htaccess (opcional)
```

---

### 3️⃣ **Instalar Dependências Python**

Volte na tela **Setup Python App** e clique no ícone de **EDITAR** da sua aplicação.

Role até **Configuration files** e você verá o comando do pip. Execute:

**Clique no botão "RUN PIP INSTALL"** ou copie o comando e execute via SSH:

```bash
source /home/tutor121/virtualenv/api_transcrever/3.7/bin/activate && cd /home/tutor121/api_transcrever
pip install -r requirements.txt
```

---

### 4️⃣ **Instalar FFmpeg via SSH** ⚠️ ESSENCIAL

**FFmpeg é obrigatório** para converter áudios do WhatsApp (.ogg, .opus).

#### Opção A: Via Comandos (se tiver acesso root)
```bash
# Conectar via SSH
ssh tutor121@salescode.dev

# Instalar FFmpeg
# No CentOS/CloudLinux
sudo yum install ffmpeg

# No Ubuntu/Debian
sudo apt-get install ffmpeg
```

#### Opção B: Pedir ao Suporte da Hospedagem
Se não tiver acesso root, **abra um ticket** pedindo:
> "Por favor, instalar FFmpeg no servidor para conversão de áudio"

#### Opção C: FFmpeg Local (não recomendado)
Você pode compilar localmente, mas é complexo. Melhor pedir ao suporte.

---

### 5️⃣ **Criar/Editar .htaccess** (Opcional, mas útil)

Crie um arquivo `.htaccess` na pasta `api_transcrever`:

```apache
PassengerEnabled On
PassengerAppRoot /home/tutor121/api_transcrever

# Aumentar timeout para áudios grandes
PassengerStartTimeout 600
PassengerAppStartRetries 5

# Permitir CORS (se precisar)
<IfModule mod_headers.c>
    Header set Access-Control-Allow-Origin "*"
    Header set Access-Control-Allow-Methods "POST, GET, OPTIONS"
    Header set Access-Control-Allow-Headers "Content-Type"
</IfModule>
```

---

### 6️⃣ **Ajustar Permissões**

Via File Manager ou SSH:

```bash
chmod 644 passenger_wsgi.py
chmod 644 app.py
chmod 755 /home/tutor121/api_transcrever
```

---

### 7️⃣ **Reiniciar a Aplicação**

Volte em **Setup Python App**, clique em **RESTART** (ícone de reload).

---

## 🧪 **TESTAR A API**

### Via Browser:
```
https://salescode.dev/pip-audio-transcrever/health
```

Deve retornar:
```json
{
  "status": "ok",
  "message": "API de transcrição funcionando"
}
```

### Via cURL (testar transcrição):
```bash
curl -X POST https://salescode.dev/pip-audio-transcrever/transcrever \
  -F "audio=@audio.ogg"
```

### Via seu serviço Node.js/PHP:
```javascript
const formData = new FormData();
formData.append('audio', audioBuffer);

const response = await axios.post(
  'https://salescode.dev/pip-audio-transcrever/transcrever',
  formData
);
```

---

## 🐛 **SOLUÇÃO DE PROBLEMAS**

### ❌ Erro 500 / Application Error

**1. Verificar logs:**
```
/home/tutor121/logs/pip-audio-transcrever.log
```

No cPanel: **Metrics → Errors** ou via SSH:
```bash
tail -f /home/tutor121/logs/pip-audio-transcrever.log
```

**2. Problemas comuns:**

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError: Flask` | Executar `pip install -r requirements.txt` novamente |
| `FFmpeg not found` | Instalar FFmpeg (passo 4) |
| `Permission denied` | Ajustar permissões (passo 6) |
| `Application failed to start` | Verificar `passenger_wsgi.py` está correto |

---

### ❌ Timeout ao transcrever

Aumentar timeout no `.htaccess`:
```apache
PassengerMaxRequestQueueSize 1000
PassengerPoolIdleTime 0
```

---

### ❌ "Não foi possível entender o áudio"

- Verificar se FFmpeg está instalado: `ffmpeg -version`
- Testar áudio localmente primeiro
- Verificar qualidade do áudio do WhatsApp

---

## 📝 **ARQUITETURA FINAL**

```
https://salescode.dev/pip-audio-transcrever/
                 ↓
            Passenger WSGI
                 ↓
         passenger_wsgi.py  ← Inicia aplicação
                 ↓
              app.py  ← Flask API
                 ↓
         [Recebe áudio] → FFmpeg converte → Google Speech API
                 ↓
         [Retorna texto JSON]
```

---

## 🔒 **SEGURANÇA (RECOMENDADO)**

### Adicionar autenticação simples

Edite `app.py` e adicione antes dos endpoints:

```python
from functools import wraps
from flask import request

API_KEY = "SUA_CHAVE_SECRETA_AQUI"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') != API_KEY:
            return jsonify({'success': False, 'error': 'API key inválida'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/transcrever', methods=['POST'])
@require_api_key  # ← Adicionar esta linha
def transcrever():
    # ... resto do código
```

Então ao chamar a API:
```javascript
axios.post('https://salescode.dev/pip-audio-transcrever/transcrever', formData, {
  headers: { 'X-API-Key': 'SUA_CHAVE_SECRETA_AQUI' }
});
```

---

## 📊 **MONITORAMENTO**

Criar script para verificar se está rodando:

```bash
# Via SSH
curl https://salescode.dev/pip-audio-transcrever/health

# Se retornar erro, reiniciar:
cd /home/tutor121/api_transcrever
touch tmp/restart.txt
```

---

## ✅ **CHECKLIST FINAL**

- [ ] Aplicação criada no cPanel
- [ ] Arquivos enviados (passenger_wsgi.py, app.py, requirements.txt)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] FFmpeg instalado no servidor
- [ ] Permissões ajustadas
- [ ] Aplicação reiniciada
- [ ] `/health` testado e funcionando
- [ ] `/transcrever` testado com áudio real

---

## 🆘 **PRECISA DE AJUDA?**

Se algo não funcionar:

1. **Copie o erro do log** (`/home/tutor121/logs/pip-audio-transcrever.log`)
2. **Teste localmente** primeiro (`python app.py`)
3. **Verifique FFmpeg**: `ffmpeg -version`
4. **Contate o suporte** da hospedagem se precisar de FFmpeg

---

**URL Final da sua API:**
```
https://salescode.dev/pip-audio-transcrever/transcrever
```

Boa sorte! 🚀
