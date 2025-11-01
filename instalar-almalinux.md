# 🐧 INSTALAÇÃO NO CWP/ALMALINUX

## 📋 PRÉ-REQUISITOS

Você vai precisar de:
- Acesso SSH ao servidor
- Usuário root ou sudo
- Python 3.8 ou superior
- FFmpeg (para converter áudios do WhatsApp)

---

## 🔧 PASSO 1: INSTALAR DEPENDÊNCIAS DO SISTEMA

Conecte via SSH e execute:

```bash
# Atualizar sistema
sudo dnf update -y

# Instalar Python 3 e pip
sudo dnf install python3 python3-pip python3-devel -y

# Instalar FFmpeg (ESSENCIAL para áudios do WhatsApp)
sudo dnf install epel-release -y
sudo dnf install ffmpeg -y

# Instalar dependências de áudio
sudo dnf install portaudio portaudio-devel -y

# Verificar instalações
python3 --version
pip3 --version
ffmpeg -version
```

---

## 📂 PASSO 2: CONFIGURAR A APLICAÇÃO

```bash
# Criar diretório para a aplicação
sudo mkdir -p /var/www/api_transcrever
cd /var/www/api_transcrever

# Fazer upload dos arquivos:
# - app.py
# - requirements.txt
# - passenger_wsgi.py (se usar Passenger)

# Ou clonar do repositório (se tiver)
# git clone seu_repositorio.git .

# Dar permissões corretas
sudo chown -R nobody:nobody /var/www/api_transcrever
sudo chmod -R 755 /var/www/api_transcrever
```

---

## 🐍 PASSO 3: CRIAR AMBIENTE VIRTUAL

```bash
cd /var/www/api_transcrever

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Testar se instalou tudo
python -c "import flask; import speech_recognition; import pydub; print('Tudo OK\!')"
```

---

## ⚙️ PASSO 4: CONFIGURAR SYSTEMD SERVICE

Crie um arquivo de serviço para rodar a aplicação automaticamente:

```bash
sudo nano /etc/systemd/system/api-transcrever.service
```

Cole este conteúdo:

```ini
[Unit]
Description=API Transcrever Audios WhatsApp
After=network.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/home/app/api_transcrever
Environment="PATH=/home/app/api_transcrever/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="FFMPEG_BINARY=/usr/local/bin/ffmpeg"
Environment="FFPROBE_BINARY=/usr/local/bin/ffprobe"
ExecStart=/home/app/api_transcrever/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=append:/home/app/api_transcrever/logs/app.log
StandardError=append:/home/app/api_transcrever/logs/error.log

[Install]
WantedBy=multi-user.target
```

**Ou copie do repositório:**

```bash
cd /home/app/api_transcrever
sudo cp api-transcrever.service /etc/systemd/system/api-transcrever.service
```

Ativar e iniciar o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable api-transcrever
sudo systemctl start api-transcrever
sudo systemctl status api-transcrever
```

---

## 🌐 PASSO 5: CONFIGURAR PROXY REVERSO NO APACHE

O CWP usa Apache, então vamos criar um proxy reverso:

```bash
sudo nano /usr/local/apache/conf.d/api_transcrever.conf
```

Cole:

```apache
<VirtualHost *:80>
    ServerName api.seudominio.com
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    ErrorLog /var/log/httpd/api_transcrever_error.log
    CustomLog /var/log/httpd/api_transcrever_access.log combined
</VirtualHost>
```

Reiniciar Apache:

```bash
sudo systemctl restart httpd
```

---

## 🔒 PASSO 6: CONFIGURAR FIREWALL

```bash
# Permitir porta 5000 (se quiser acesso direto)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# Ou apenas HTTP/HTTPS (recomendado)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## ✅ PASSO 7: TESTAR

```bash
# Teste local
curl http://localhost:5000/health

# Teste externo
curl http://api.seudominio.com/health
```

Deve retornar:
```json
{
  "status": "ok",
  "message": "API de transcrição funcionando"
}
```

---

## 🐛 TROUBLESHOOTING

### Ver logs da aplicação:
```bash
sudo journalctl -u api-transcrever -f
```

### Verificar se a porta está em uso:
```bash
sudo netstat -tulpn | grep 5000
```

### Testar manualmente:
```bash
cd /var/www/api_transcrever
source venv/bin/activate
python app.py
```

### Permissões de diretório temporário:
```bash
sudo chmod 1777 /tmp
```

---

## 🔄 ATUALIZAR A APLICAÇÃO

```bash
cd /var/www/api_transcrever
source venv/bin/activate
git pull  # se usar git
pip install -r requirements.txt --upgrade
sudo systemctl restart api-transcrever
```

---

## 🌐 USAR COM DOMÍNIO (HTTPS)

No **CWP Panel**:

1. Vá em **WebServer Settings** → **WebServers Main Conf**
2. Ou use o **Apache Vhost Manager**
3. Configure o domínio apontando para o proxy reverso
4. Instale SSL com **AutoSSL** ou **Let's Encrypt**

---

## 📊 MONITORAMENTO

```bash
# Status do serviço
sudo systemctl status api-transcrever

# Uso de recursos
htop

# Logs em tempo real
tail -f /var/log/httpd/api_transcrever_error.log
```

---

## ✨ PRONTO!

Sua API está rodando em:
- Local: `http://localhost:5000`
- Externa: `http://api.seudominio.com`

### Testar transcrição:
```bash
curl -X POST -F "audio=@seu_audio.ogg" http://api.seudominio.com/transcrever
```