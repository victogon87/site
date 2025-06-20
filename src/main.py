import os
import sys
from dotenv import load_dotenv

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sua_chave_secreta_muito_segura_aqui_123456789')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'sua_chave_secreta_muito_segura_aqui_123456789')
database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'app.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f"sqlite:///{database_path}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
CORS(app, origins="*")  # Permitir CORS para todas as origens
jwt = JWTManager(app)

# Importar e inicializar banco após configuração
from src.models.database import db
db.init_app(app)

# Importar todos os modelos
from src.models.usuario import Usuario
from src.models.secretaria import Secretaria
from src.models.projeto import Projeto
from src.models.recursos import ContaPaga, MaterialEscritorio, RecursoEstrategico

# Importar e registrar blueprints
from src.routes.auth import auth_bp
from src.routes.secretarias import secretarias_bp
from src.routes.projetos import projetos_bp
from src.routes.recursos import recursos_bp
from src.routes.relatorios import relatorios_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(secretarias_bp, url_prefix='/api/secretarias')
app.register_blueprint(projetos_bp, url_prefix='/api/projetos')
app.register_blueprint(recursos_bp, url_prefix='/api/recursos')
app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')

# Rota de teste
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'API funcionando!'})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "API do Sistema de Gestão da Secretaria de Governo", 200


if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print(f"📁 Banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.run(host='0.0.0.0', port=5000, debug=True)

