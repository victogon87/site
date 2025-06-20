from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from src.models.database import db
from src.models.usuario import Usuario
from src.models.projeto import Projeto
from src.models.secretaria import Secretaria

projetos_bp = Blueprint('projetos', __name__)

@projetos_bp.route('/', methods=['GET'])
@jwt_required()
def list_projetos():
    """Listar todos os projetos com filtros opcionais"""
    try:
        # Parâmetros de filtro
        secretaria_id = request.args.get('secretaria_id', type=int)
        status = request.args.get('status')
        
        query = Projeto.query
        
        if secretaria_id:
            query = query.filter_by(secretaria_id=secretaria_id)
        
        if status:
            query = query.filter_by(status=status)
        
        projetos = query.all()
        
        return jsonify({
            'projetos': [projeto.to_dict() for projeto in projetos]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projetos_bp.route('/', methods=['POST'])
@jwt_required()
def create_projeto():
    """Criar novo projeto"""
    try:
        # Verificar permissões
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso == 'visualizador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['titulo', 'secretaria_id']):
            return jsonify({'error': 'Título e secretaria são obrigatórios'}), 400
        
        # Verificar se a secretaria existe
        secretaria = Secretaria.query.get(data['secretaria_id'])
        if not secretaria:
            return jsonify({'error': 'Secretaria não encontrada'}), 404
        
        novo_projeto = Projeto(
            titulo=data['titulo'],
            descricao=data.get('descricao'),
            status=data.get('status', 'planejamento'),
            secretaria_id=data['secretaria_id']
        )
        
        # Converter datas se fornecidas
        if data.get('data_inicio'):
            novo_projeto.data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
        
        if data.get('data_previsao_termino'):
            novo_projeto.data_previsao_termino = datetime.strptime(data['data_previsao_termino'], '%Y-%m-%d').date()
        
        if data.get('progresso'):
            novo_projeto.progresso = max(0, min(100, int(data['progresso'])))
        
        if data.get('recursos_aplicados'):
            novo_projeto.recursos_aplicados = float(data['recursos_aplicados'])
        
        if data.get('recursos_pendentes'):
            novo_projeto.recursos_pendentes = float(data['recursos_pendentes'])
        
        if data.get('observacoes'):
            novo_projeto.observacoes = data['observacoes']
        
        db.session.add(novo_projeto)
        db.session.commit()
        
        return jsonify({
            'message': 'Projeto criado com sucesso',
            'projeto': novo_projeto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projetos_bp.route('/<int:projeto_id>', methods=['GET'])
@jwt_required()
def get_projeto(projeto_id):
    """Obter detalhes de um projeto específico"""
    try:
        projeto = Projeto.query.get_or_404(projeto_id)
        return jsonify({'projeto': projeto.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projetos_bp.route('/<int:projeto_id>', methods=['PUT'])
@jwt_required()
def update_projeto(projeto_id):
    """Atualizar dados de um projeto"""
    try:
        # Verificar permissões
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso == 'visualizador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        projeto = Projeto.query.get_or_404(projeto_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Atualizar campos
        if 'titulo' in data:
            projeto.titulo = data['titulo']
        if 'descricao' in data:
            projeto.descricao = data['descricao']
        if 'status' in data:
            projeto.status = data['status']
        if 'data_inicio' in data and data['data_inicio']:
            projeto.data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
        if 'data_previsao_termino' in data and data['data_previsao_termino']:
            projeto.data_previsao_termino = datetime.strptime(data['data_previsao_termino'], '%Y-%m-%d').date()
        if 'data_termino_real' in data and data['data_termino_real']:
            projeto.data_termino_real = datetime.strptime(data['data_termino_real'], '%Y-%m-%d').date()
        if 'progresso' in data:
            projeto.progresso = max(0, min(100, int(data['progresso'])))
        if 'recursos_aplicados' in data:
            projeto.recursos_aplicados = float(data['recursos_aplicados'])
        if 'recursos_pendentes' in data:
            projeto.recursos_pendentes = float(data['recursos_pendentes'])
        if 'observacoes' in data:
            projeto.observacoes = data['observacoes']
        
        # Atualizar status automaticamente baseado no progresso
        if projeto.progresso == 100 and projeto.status != 'concluido':
            projeto.status = 'concluido'
            if not projeto.data_termino_real:
                projeto.data_termino_real = date.today()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Projeto atualizado com sucesso',
            'projeto': projeto.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projetos_bp.route('/<int:projeto_id>', methods=['DELETE'])
@jwt_required()
def delete_projeto(projeto_id):
    """Excluir um projeto"""
    try:
        # Verificar permissões (apenas administradores)
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso != 'administrador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        projeto = Projeto.query.get_or_404(projeto_id)
        
        db.session.delete(projeto)
        db.session.commit()
        
        return jsonify({'message': 'Projeto excluído com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projetos_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard_projetos():
    """Dados para o dashboard de projetos"""
    try:
        # Estatísticas gerais
        total_projetos = Projeto.query.count()
        projetos_concluidos = Projeto.query.filter_by(status='concluido').count()
        projetos_em_execucao = Projeto.query.filter_by(status='execucao').count()
        projetos_atrasados = Projeto.query.filter_by(status='atrasado').count()
        
        # Projetos por secretaria
        from sqlalchemy import func
        projetos_por_secretaria = db.session.query(
            Secretaria.nome,
            func.count(Projeto.id).label('total')
        ).join(Projeto).group_by(Secretaria.id, Secretaria.nome).all()
        
        # Projetos próximos do vencimento (próximos 7 dias)
        from datetime import timedelta
        data_limite = date.today() + timedelta(days=7)
        projetos_vencendo = Projeto.query.filter(
            Projeto.data_previsao_termino <= data_limite,
            Projeto.status.in_(['planejamento', 'execucao'])
        ).all()
        
        return jsonify({
            'estatisticas': {
                'total_projetos': total_projetos,
                'projetos_concluidos': projetos_concluidos,
                'projetos_em_execucao': projetos_em_execucao,
                'projetos_atrasados': projetos_atrasados
            },
            'projetos_por_secretaria': [
                {'secretaria': nome, 'total': total} 
                for nome, total in projetos_por_secretaria
            ],
            'projetos_vencendo': [projeto.to_dict() for projeto in projetos_vencendo]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

