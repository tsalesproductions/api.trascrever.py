import os
import tempfile
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import speech_recognition as sr
from pydub import AudioSegment
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB
ALLOWED_EXTENSIONS = {'ogg', 'oga', 'mp3', 'wav', 'opus', 'm4a'}

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def converter_para_wav(input_path):
    """Converte o áudio para formato WAV que o speech_recognition entende"""
    try:
        logger.info(f"Convertendo áudio: {input_path}")
        # Carregar o áudio (pydub detecta o formato automaticamente)
        audio = AudioSegment.from_file(input_path)
        
        # Converter para mono e taxa de amostragem adequada
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        # Salvar como WAV temporário
        output_path = input_path.rsplit('.', 1)[0] + '_converted.wav'
        audio.export(output_path, format='wav')
        
        logger.info(f"Áudio convertido com sucesso: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Erro ao converter áudio: {str(e)}")
        raise

def transcrever_audio(audio_path):
    """Transcreve o áudio usando Google Speech Recognition"""
    r = sr.Recognizer()
    
    # Otimizações para melhor reconhecimento
    r.energy_threshold = 300
    r.dynamic_energy_threshold = False
    
    try:
        with sr.AudioFile(audio_path) as source:
            logger.info("Processando áudio para transcrição...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.record(source)
        
        logger.info("Enviando para Google Speech Recognition...")
        texto = r.recognize_google(audio, language="pt-BR")
        logger.info(f"Transcrição concluída: {texto[:50]}...")
        return texto
        
    except sr.UnknownValueError:
        logger.warning("Não foi possível entender o áudio")
        return None
    except sr.RequestError as e:
        logger.error(f"Erro na API do Google: {str(e)}")
        raise Exception(f"Erro no serviço de reconhecimento: {str(e)}")
    except Exception as e:
        logger.error(f"Erro ao transcrever: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'API de transcrição funcionando'
    }), 200

@app.route('/transcrever', methods=['POST'])
def transcrever():
    """
    Endpoint principal para transcrever áudios
    
    Aceita:
    - Arquivo enviado via multipart/form-data com a chave 'audio'
    
    Retorna:
    - JSON com o texto transcrito ou mensagem de erro
    """
    try:
        # Verificar se o arquivo foi enviado
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo de áudio enviado. Use a chave "audio" no form-data.'
            }), 400
        
        file = request.files['audio']
        
        # Verificar se o arquivo tem nome
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Arquivo sem nome'
            }), 400
        
        # Verificar extensão do arquivo
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Formato não suportado. Use: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        logger.info(f"Recebido arquivo: {filename}")
        file.save(temp_path)
        
        try:
            # Converter para WAV se necessário
            if not filename.lower().endswith('.wav'):
                wav_path = converter_para_wav(temp_path)
            else:
                wav_path = temp_path
            
            # Transcrever o áudio
            texto = transcrever_audio(wav_path)
            
            # Limpar arquivos temporários
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if wav_path != temp_path and os.path.exists(wav_path):
                os.remove(wav_path)
            
            if texto:
                return jsonify({
                    'success': True,
                    'texto': texto,
                    'message': 'Áudio transcrito com sucesso'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'texto': '',
                    'message': 'Não foi possível entender o áudio. Verifique a qualidade do arquivo.'
                }), 200
                
        except Exception as e:
            # Limpar arquivos em caso de erro
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
            
    except Exception as e:
        logger.error(f"Erro no endpoint /transcrever: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Tratamento para arquivos muito grandes"""
    return jsonify({
        'success': False,
        'error': 'Arquivo muito grande. Tamanho máximo: 16MB'
    }), 413

if __name__ == '__main__':
    logger.info("🚀 Iniciando API de Transcrição de Áudios")
    logger.info("📡 Endpoint: POST /transcrever")
    logger.info("💚 Health check: GET /health")
    app.run(host='0.0.0.0', port=5000, debug=True)
