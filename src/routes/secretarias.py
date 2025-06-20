from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import db
from src.models.usuario import Usuario
from src.models.secretaria import Secretaria

secretarias_bp = Blueprint('secretarias', __name__)

@secretarias_bp.route('/', methods=['GET'])
@jwt_required()
def list_secretarias():
    """Listar todas as secretarias"""
    try:
        secretarias = Secretaria.query.filter_by(ativa=True).all()
        return jsonify({
            'secretarias': [secretaria.to_dict() for secretaria in secretarias]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@secretarias_bp.route('/', methods=['POST'])
@jwt_required()
def create_secretaria():
    """Criar nova secretaria"""
    try:
        # Verificar permissões
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso == 'visualizador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['nome', 'responsavel']):
            return jsonify({'error': 'Nome e responsável são obrigatórios'}), 400
        
        nova_secretaria = Secretaria(
            nome=data['nome'],
            responsavel=data['responsavel'],
            contato=data.get('contato'),
            email=data.get('email'),
            telefone=data.get('telefone')
        )
        
        db.session.add(nova_secretaria)
        db.session.commit()
        
        return jsonify({
            'message': 'Secretaria criada com sucesso',
            'secretaria': nova_secretaria.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@secretarias_bp.route('/<int:secretaria_id>', methods=['GET'])
@jwt_required()
def get_secretaria(secretaria_id):
    """Obter detalhes de uma secretaria específica"""
    try:
        secretaria = Secretaria.query.get_or_404(secretaria_id)
        return jsonify({'secretaria': secretaria.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@secretarias_bp.route('/<int:secretaria_id>', methods=['PUT'])
@jwt_required()
def update_secretaria(secretaria_id):
    """Atualizar dados de uma secretaria"""
    try:
        # Verificar permissões
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso == 'visualizador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        secretaria = Secretaria.query.get_or_404(secretaria_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Atualizar campos
        if 'nome' in data:
            secretaria.nome = data['nome']
        if 'responsavel' in data:
            secretaria.responsavel = data['responsavel']
        if 'contato' in data:
            secretaria.contato = data['contato']
        if 'email' in data:
            secretaria.email = data['email']
        if 'telefone' in data:
            secretaria.telefone = data['telefone']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Secretaria atualizada com sucesso',
            'secretaria': secretaria.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@secretarias_bp.route('/<int:secretaria_id>', methods=['DELETE'])
@jwt_required()
def delete_secretaria(secretaria_id):
    """Desativar uma secretaria (soft delete)"""
    try:
        # Verificar permissões (apenas administradores)
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso != 'administrador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        secretaria = Secretaria.query.get_or_404(secretaria_id)
        secretaria.ativa = False
        
        db.session.commit()
        
        return jsonify({'message': 'Secretaria desativada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

