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

secretarias = [
    {
        'id': 1,
        'nome': 'Secretaria de Educação',
        'responsavel': 'Ana Costa',
        'contato': 'ana.costa@educacao.gov.br',
        'email': 'educacao@gov.br',
        'telefone': '(11) 3333-1111',
        'ativa': True
    },
    {
        'id': 2,
        'nome': 'Secretaria de Saúde',
        'responsavel': 'Dr. Carlos Mendes',
        'contato': 'carlos.mendes@saude.gov.br',
        'email': 'saude@gov.br',
        'telefone': '(11) 3333-2222',
        'ativa': True
    },
    {
        'id': 3,
        'nome': 'Secretaria de Obras',
        'responsavel': 'Eng. Roberto Lima',
        'contato': 'roberto.lima@obras.gov.br',
        'email': 'obras@gov.br',
        'telefone': '(11) 3333-3333',
        'ativa': True
    },
    {
        'id': 4,
        'nome': 'Secretaria de Meio Ambiente',
        'responsavel': 'Dra. Fernanda Oliveira',
        'contato': 'fernanda.oliveira@meioambiente.gov.br',
        'email': 'meioambiente@gov.br',
        'telefone': '(11) 3333-4444',
        'ativa': True
    }
]

projetos = [
    {
        'id': 1,
        'titulo': 'Reforma das Escolas Municipais',
        'descricao': 'Reforma e modernização de 10 escolas municipais',
        'status': 'execucao',
        'data_inicio': '2024-11-15',
        'data_previsao_termino': '2025-02-15',
        'progresso': 65,
        'recursos_aplicados': 150000.00,
        'recursos_pendentes': 40000.00,
        'observacoes': 'Projeto em andamento, dentro do cronograma',
        'secretaria_id': 1
    },
    {
        'id': 2,
        'titulo': 'Construção do Novo Posto de Saúde',
        'descricao': 'Construção de posto de saúde no bairro Vila Nova',
        'status': 'planejamento',
        'data_inicio': '2025-01-01',
        'data_previsao_termino': '2025-06-30',
        'progresso': 10,
        'recursos_aplicados': 25000.00,
        'recursos_pendentes': 200000.00,
        'observacoes': 'Aguardando liberação de recursos',
        'secretaria_id': 2
    },
    {
        'id': 3,
        'titulo': 'Pavimentação da Rua Principal',
        'descricao': 'Pavimentação asfáltica da rua principal do centro',
        'status': 'execucao',
        'data_inicio': '2024-12-01',
        'data_previsao_termino': '2025-01-15',
        'progresso': 80,
        'recursos_aplicados': 120000.00,
        'recursos_pendentes': 15000.00,
        'observacoes': 'Projeto quase concluído',
        'secretaria_id': 3
    },
    {
        'id': 4,
        'titulo': 'Programa de Arborização Urbana',
        'descricao': 'Plantio de 500 árvores em praças e ruas da cidade',
        'status': 'concluido',
        'data_inicio': '2024-09-15',
        'data_previsao_termino': '2024-12-05',
        'data_termino_real': '2024-12-10',
        'progresso': 100,
        'recursos_aplicados': 35000.00,
        'recursos_pendentes': 0.00,
        'observacoes': 'Projeto concluído com sucesso',
        'secretaria_id': 4
    },
    {
        'id': 5,
        'titulo': 'Digitalização do Acervo Escolar',
        'descricao': 'Digitalização de documentos e criação de biblioteca digital',
        'status': 'atrasado',
        'data_inicio': '2024-10-15',
        'data_previsao_termino': '2024-12-10',
        'progresso': 45,
        'recursos_aplicados': 18000.00,
        'recursos_pendentes': 12000.00,
        'observacoes': 'Projeto atrasado devido a problemas técnicos',
        'secretaria_id': 1
    }
]

# Rotas de autenticação
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

# Rotas de secretarias
@app.route('/api/secretarias', methods=['GET'])
@jwt_required()
def list_secretarias():
    try:
        secretarias_ativas = [s for s in secretarias if s['ativa']]
        return jsonify({'secretarias': secretarias_ativas}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rotas de projetos
@app.route('/api/projetos', methods=['GET'])
@jwt_required()
def list_projetos():
    try:
        return jsonify({'projetos': projetos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard
@app.route('/api/relatorios/dashboard-geral', methods=['GET'])
@jwt_required()
def dashboard_geral():
    try:
        total_secretarias = len([s for s in secretarias if s['ativa']])
        total_projetos = len(projetos)
        projetos_concluidos = len([p for p in projetos if p['status'] == 'concluido'])
        projetos_atrasados = len([p for p in projetos if p['status'] == 'atrasado'])
        projetos_em_execucao = len([p for p in projetos if p['status'] == 'execucao'])
        
        # Projetos por status
        status_count = {}
        for projeto in projetos:
            status = projeto['status']
            status_count[status] = status_count.get(status, 0) + 1
        
        projetos_por_status = [{'status': k, 'total': v} for k, v in status_count.items()]
        
        # Projetos por secretaria
        secretaria_count = {}
        for projeto in projetos:
            sec_id = projeto['secretaria_id']
            sec_nome = next((s['nome'] for s in secretarias if s['id'] == sec_id), 'Desconhecida')
            secretaria_count[sec_nome] = secretaria_count.get(sec_nome, 0) + 1
        
        projetos_por_secretaria = [{'secretaria': k, 'total': v} for k, v in secretaria_count.items()]
        
        # Alertas simulados
        alertas = [
            {
                'tipo': 'projeto_vencendo',
                'mensagem': 'Projeto "Pavimentação da Rua Principal" vence em breve',
                'projeto_id': 3
            },
            {
                'tipo': 'recursos_pendentes',
                'mensagem': 'Projeto "Construção do Novo Posto de Saúde" tem recursos pendentes: R$ 200.000',
                'valor': 200000.00,
                'projeto_id': 2
            }
        ]
        
        dashboard = {
            'estatisticas_gerais': {
                'total_secretarias': total_secretarias,
                'total_projetos': total_projetos,
                'projetos_concluidos': projetos_concluidos,
                'projetos_atrasados': projetos_atrasados,
                'projetos_em_execucao': projetos_em_execucao,
                'taxa_conclusao': round((projetos_concluidos / total_projetos * 100) if total_projetos > 0 else 0, 2)
            },
            'projetos_por_status': projetos_por_status,
            'projetos_por_secretaria': projetos_por_secretaria,
            'alertas': alertas,
            'resumo_financeiro': {
                'gastos_mes_atual': 4070.00,
                'materiais_recentes': 3
            }
        }
        
        return jsonify({'dashboard': dashboard}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota de teste
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'API funcionando!'})

@app.route('/api/', methods=['GET'])
def index():
    return "API do Sistema de Gestão da Secretaria de Governo", 200

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("📊 Usando dados em memória para demonstração")
    app.run(host='0.0.0.0', port=5000, debug=True)
