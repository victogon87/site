from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from src.models.database import db
from src.models.usuario import Usuario
from src.models.recursos import ContaPaga, MaterialEscritorio, RecursoEstrategico

recursos_bp = Blueprint('recursos', __name__)

# === CONTAS PAGAS ===
@recursos_bp.route('/contas', methods=['GET'])
@jwt_required()
def list_contas():
    """Listar contas pagas com filtros opcionais"""
    try:
        # Parâmetros de filtro
        tipo_conta = request.args.get('tipo_conta')
        mes_referencia = request.args.get('mes_referencia')
        ano = request.args.get('ano')
        
        query = ContaPaga.query
        
        if tipo_conta:
            query = query.filter_by(tipo_conta=tipo_conta)
        
        if mes_referencia:
            query = query.filter_by(mes_referencia=mes_referencia)
        
        if ano:
            query = query.filter(ContaPaga.mes_referencia.like(f'{ano}-%'))
        
        contas = query.order_by(ContaPaga.mes_referencia.desc()).all()
        
        return jsonify({
            'contas': [conta.to_dict() for conta in contas]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recursos_bp.route('/contas', methods=['POST'])
@jwt_required()
def create_conta():
    """Criar registro de conta paga"""
    try:
        # Verificar permissões
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso == 'visualizador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['tipo_conta', 'mes_referencia', 'valor', 'data_pagamento']):
            return jsonify({'error': 'Dados obrigatórios: tipo_conta, mes_referencia, valor, data_pagamento'}), 400
        
        nova_conta = ContaPaga(
            tipo_conta=data['tipo_conta'],
            mes_referencia=data['mes_referencia'],
            valor=float(data['valor']),
            data_pagamento=datetime.strptime(data['data_pagamento'], '%Y-%m-%d').date(),
            arquivo_comprovante=data.get('arquivo_comprovante'),
            observacoes=data.get('observacoes')
        )
        
        db.session.add(nova_conta)
        db.session.commit()
        
        return jsonify({
            'message': 'Conta registrada com sucesso',
            'conta': nova_conta.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# === MATERIAIS DE ESCRITÓRIO ===
@recursos_bp.route('/materiais', methods=['GET'])
@jwt_required()
def list_materiais():
    """Listar materiais de escritório"""
    try:
        materiais = MaterialEscritorio.query.order_by(MaterialEscritorio.data_entrada.desc()).all()
        
        return jsonify({
            'materiais': [material.to_dict() for material in materiais]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recursos_bp.route('/materiais', methods=['POST'])
@jwt_required()
def create_material():
    """Criar registro de material de escritório"""
    try:
        # Verificar permissões
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso == 'visualizador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['nome', 'quantidade', 'data_entrada']):
            return jsonify({'error': 'Dados obrigatórios: nome, quantidade, data_entrada'}), 400
        
        novo_material = MaterialEscritorio(
            nome=data['nome'],
            descricao=data.get('descricao'),
            quantidade=int(data['quantidade']),
            unidade=data.get('unidade'),
            fornecedor=data.get('fornecedor'),
            data_entrada=datetime.strptime(data['data_entrada'], '%Y-%m-%d').date(),
            valor_unitario=float(data['valor_unitario']) if data.get('valor_unitario') else None
        )
        
        db.session.add(novo_material)
        db.session.commit()
        
        return jsonify({
            'message': 'Material registrado com sucesso',
            'material': novo_material.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# === RECURSOS ESTRATÉGICOS ===
@recursos_bp.route('/estrategicos', methods=['GET'])
@jwt_required()
def list_recursos_estrategicos():
    """Listar recursos estratégicos"""
    try:
        recursos = RecursoEstrategico.query.order_by(RecursoEstrategico.data_chegada.desc()).all()
        
        return jsonify({
            'recursos': [recurso.to_dict() for recurso in recursos]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recursos_bp.route('/estrategicos', methods=['POST'])
@jwt_required()
def create_recurso_estrategico():
    """Criar registro de recurso estratégico"""
    try:
        # Verificar permissões
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso == 'visualizador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['nome', 'descricao', 'quantidade', 'data_chegada']):
            return jsonify({'error': 'Dados obrigatórios: nome, descricao, quantidade, data_chegada'}), 400
        
        novo_recurso = RecursoEstrategico(
            nome=data['nome'],
            descricao=data['descricao'],
            quantidade=int(data['quantidade']),
            data_chegada=datetime.strptime(data['data_chegada'], '%Y-%m-%d').date(),
            destino_uso=data.get('destino_uso'),
            fornecedor=data.get('fornecedor'),
            valor=float(data['valor']) if data.get('valor') else None,
            status=data.get('status', 'recebido')
        )
        
        db.session.add(novo_recurso)
        db.session.commit()
        
        return jsonify({
            'message': 'Recurso estratégico registrado com sucesso',
            'recurso': novo_recurso.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# === DASHBOARD DE RECURSOS ===
@recursos_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard_recursos():
    """Dados para o dashboard de recursos"""
    try:
        from sqlalchemy import func, extract
        
        # Gastos por tipo de conta no ano atual
        ano_atual = date.today().year
        gastos_por_tipo = db.session.query(
            ContaPaga.tipo_conta,
            func.sum(ContaPaga.valor).label('total')
        ).filter(
            ContaPaga.mes_referencia.like(f'{ano_atual}-%')
        ).group_by(ContaPaga.tipo_conta).all()
        
        # Total de gastos no mês atual
        mes_atual = date.today().strftime('%Y-%m')
        gastos_mes_atual = db.session.query(
            func.sum(ContaPaga.valor)
        ).filter_by(mes_referencia=mes_atual).scalar() or 0
        
        # Materiais recebidos nos últimos 30 dias
        from datetime import timedelta
        data_limite = date.today() - timedelta(days=30)
        materiais_recentes = MaterialEscritorio.query.filter(
            MaterialEscritorio.data_entrada >= data_limite
        ).count()
        
        # Recursos estratégicos por status
        recursos_por_status = db.session.query(
            RecursoEstrategico.status,
            func.count(RecursoEstrategico.id).label('total')
        ).group_by(RecursoEstrategico.status).all()
        
        return jsonify({
            'gastos_por_tipo': [
                {'tipo': tipo, 'total': float(total)} 
                for tipo, total in gastos_por_tipo
            ],
            'gastos_mes_atual': float(gastos_mes_atual),
            'materiais_recentes': materiais_recentes,
            'recursos_por_status': [
                {'status': status, 'total': total} 
                for status, total in recursos_por_status
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === ENDPOINTS DE ATUALIZAÇÃO E EXCLUSÃO ===
@recursos_bp.route('/contas/<int:conta_id>', methods=['PUT'])
@jwt_required()
def update_conta(conta_id):
    """Atualizar conta paga"""
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if not current_user or current_user.nivel_acesso == 'visualizador':
            return jsonify({'error': 'Acesso negado'}), 403
        
        conta = ContaPaga.query.get_or_404(conta_id)
        data = request.get_json()
        
        if 'tipo_conta' in data:
            conta.tipo_conta = data['tipo_conta']
        if 'mes_referencia' in data:
            conta.mes_referencia = data['mes_referencia']
        if 'valor' in data:
            conta.valor = float(data['valor'])
        if 'data_pagamento' in data:
            conta.data_pagamento = datetime.strptime(data['data_pagamento'], '%Y-%m-%d').date()
        if 'arquivo_comprovante' in data:
            conta.arquivo_comprovante = data['arquivo_comprovante']
        if 'observacoes' in data:
            conta.observacoes = data['observacoes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Conta atualizada com sucesso',
            'conta': conta.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

