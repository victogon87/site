from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.database import db
from src.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login do usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('senha'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        usuario = Usuario.query.filter_by(email=data['email']).first()
        
        if not usuario or not usuario.check_senha(data['senha']):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not usuario.ativo:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        # Criar token de acesso
        access_token = create_access_token(identity=usuario.id)
        
        return jsonify({
            'access_token': access_token,
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """Endpoint para cadastro de novo usuário (apenas administradores)"""
    try:
        # Verificar se o usuário atual é administrador
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso != 'administrador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['nome', 'email', 'senha', 'nivel_acesso']):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Verificar se o email já existe
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Criar novo usuário
        novo_usuario = Usuario(
            nome=data['nome'],
            email=data['email'],
            nivel_acesso=data['nivel_acesso']
        )
        novo_usuario.set_senha(data['senha'])
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário cadastrado com sucesso',
            'usuario': novo_usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Endpoint para obter dados do usuário atual"""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'usuario': usuario.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/usuarios', methods=['GET'])
@jwt_required()
def list_users():
    """Endpoint para listar usuários (apenas administradores)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso != 'administrador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        usuarios = Usuario.query.all()
        return jsonify({
            'usuarios': [usuario.to_dict() for usuario in usuarios]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

