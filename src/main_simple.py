import os
import sys
from dotenv import load_dotenv

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = 'sua_chave_secreta_muito_segura_aqui_123456789'
app.config['JWT_SECRET_KEY'] = 'sua_chave_secreta_muito_segura_aqui_123456789'

# Inicializar extensões
CORS(app, origins=["https://sitefrontend-zeta.vercel.app"])  # Adicionei a URL do seu frontend aqui
jwt = JWTManager(app)

# Dados em memória para demonstração
usuarios = [
    {
        'id': 1,
        'nome': 'Administrador',
        'email': 'admin@secretaria.gov.br',
        'senha_hash': generate_password_hash('8738mv'),
        'nivel_acesso': 'administrador',
        'ativo': True
    },
    {
        'id': 2,
        'nome': 'João Silva',
        'email': 'joao@secretaria.gov.br',
        'senha_hash': generate_password_hash('colaborador123'),
        'nivel_acesso': 'colaborador',
        'ativo': True
    },
    {
        'id': 3,
        'nome': 'Maria Santos',
        'email': 'maria@secretaria.gov.br',
        'senha_hash': generate_password_hash('visualizador123'),
        'nivel_acesso': 'visualizador',
        'ativo': True
    }
]

# Função de login
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('senha'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário
        usuario = None
        for u in usuarios:
            if u['email'] == data['email']:
                usuario = u
                break
        
        if not usuario or not check_password_hash(usuario['senha_hash'], data['senha']):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not usuario['ativo']:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        # Criar token de acesso
        access_token = create_access_token(identity=usuario['id'])
        
        # Remover senha do retorno
        usuario_response = {k: v for k, v in usuario.items() if k != 'senha_hash'}
        
        return jsonify({
            'access_token': access_token,
            'usuario': usuario_response
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para verificar o usuário atual
@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar usuário
        usuario = None
        for u in usuarios:
            if u['id'] == current_user_id:
                usuario = u
                break
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Remover senha do retorno
        usuario_response = {k: v for k, v in usuario.items() if k != 'senha_hash'}
        
        return jsonify({'usuario': usuario_response}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota de saúde (para checar se a API está funcionando)
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'API funcionando!'})

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)
