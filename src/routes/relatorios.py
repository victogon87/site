from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from src.models.database import db
from src.models.usuario import Usuario
from src.models.secretaria import Secretaria
from src.models.projeto import Projeto
from src.models.recursos import ContaPaga, MaterialEscritorio, RecursoEstrategico

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/secretarias', methods=['GET'])
@jwt_required()
def relatorio_secretarias():
    """Relatório geral de secretarias"""
    try:
        # Parâmetros de filtro
        periodo_inicio = request.args.get('periodo_inicio')
        periodo_fim = request.args.get('periodo_fim')
        secretaria_id = request.args.get('secretaria_id', type=int)
        
        # Query base
        query = Secretaria.query.filter_by(ativa=True)
        
        if secretaria_id:
            query = query.filter_by(id=secretaria_id)
        
        secretarias = query.all()
        
        relatorio = []
        
        for secretaria in secretarias:
            # Filtrar projetos por período se especificado
            projetos_query = Projeto.query.filter_by(secretaria_id=secretaria.id)
            
            if periodo_inicio:
                data_inicio = datetime.strptime(periodo_inicio, '%Y-%m-%d').date()
                projetos_query = projetos_query.filter(Projeto.data_inicio >= data_inicio)
            
            if periodo_fim:
                data_fim = datetime.strptime(periodo_fim, '%Y-%m-%d').date()
                projetos_query = projetos_query.filter(Projeto.data_inicio <= data_fim)
            
            projetos = projetos_query.all()
            
            # Estatísticas da secretaria
            total_projetos = len(projetos)
            projetos_concluidos = len([p for p in projetos if p.status == 'concluido'])
            projetos_em_execucao = len([p for p in projetos if p.status == 'execucao'])
            projetos_atrasados = len([p for p in projetos if p.status == 'atrasado'])
            
            recursos_aplicados = sum([float(p.recursos_aplicados or 0) for p in projetos])
            recursos_pendentes = sum([float(p.recursos_pendentes or 0) for p in projetos])
            
            progresso_medio = sum([p.progresso for p in projetos]) / total_projetos if total_projetos > 0 else 0
            
            relatorio.append({
                'secretaria': secretaria.to_dict(),
                'estatisticas': {
                    'total_projetos': total_projetos,
                    'projetos_concluidos': projetos_concluidos,
                    'projetos_em_execucao': projetos_em_execucao,
                    'projetos_atrasados': projetos_atrasados,
                    'recursos_aplicados': recursos_aplicados,
                    'recursos_pendentes': recursos_pendentes,
                    'progresso_medio': round(progresso_medio, 2)
                },
                'projetos': [projeto.to_dict() for projeto in projetos]
            })
        
        return jsonify({
            'relatorio': relatorio,
            'periodo': {
                'inicio': periodo_inicio,
                'fim': periodo_fim
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorios_bp.route('/governo', methods=['GET'])
@jwt_required()
def relatorio_governo():
    """Relatório geral da Secretaria de Governo"""
    try:
        # Parâmetros de filtro
        periodo_inicio = request.args.get('periodo_inicio')
        periodo_fim = request.args.get('periodo_fim')
        
        # Converter datas se fornecidas
        data_inicio = None
        data_fim = None
        
        if periodo_inicio:
            data_inicio = datetime.strptime(periodo_inicio, '%Y-%m-%d').date()
        
        if periodo_fim:
            data_fim = datetime.strptime(periodo_fim, '%Y-%m-%d').date()
        
        # === GASTOS (CONTAS PAGAS) ===
        contas_query = ContaPaga.query
        
        if data_inicio and data_fim:
            # Filtrar por período de pagamento
            contas_query = contas_query.filter(
                ContaPaga.data_pagamento >= data_inicio,
                ContaPaga.data_pagamento <= data_fim
            )
        
        contas = contas_query.all()
        
        # Agrupar gastos por tipo
        gastos_por_tipo = {}
        total_gastos = 0
        
        for conta in contas:
            tipo = conta.tipo_conta
            valor = float(conta.valor)
            
            if tipo not in gastos_por_tipo:
                gastos_por_tipo[tipo] = 0
            
            gastos_por_tipo[tipo] += valor
            total_gastos += valor
        
        # === MATERIAIS DE ESCRITÓRIO ===
        materiais_query = MaterialEscritorio.query
        
        if data_inicio and data_fim:
            materiais_query = materiais_query.filter(
                MaterialEscritorio.data_entrada >= data_inicio,
                MaterialEscritorio.data_entrada <= data_fim
            )
        
        materiais = materiais_query.all()
        total_materiais = len(materiais)
        valor_total_materiais = sum([float(m.valor_unitario or 0) * m.quantidade for m in materiais])
        
        # === RECURSOS ESTRATÉGICOS ===
        recursos_query = RecursoEstrategico.query
        
        if data_inicio and data_fim:
            recursos_query = recursos_query.filter(
                RecursoEstrategico.data_chegada >= data_inicio,
                RecursoEstrategico.data_chegada <= data_fim
            )
        
        recursos = recursos_query.all()
        total_recursos = len(recursos)
        valor_total_recursos = sum([float(r.valor or 0) for r in recursos])
        
        # === RESUMO GERAL ===
        resumo = {
            'gastos': {
                'total': total_gastos,
                'por_tipo': gastos_por_tipo,
                'detalhes': [conta.to_dict() for conta in contas]
            },
            'materiais': {
                'total_itens': total_materiais,
                'valor_total': valor_total_materiais,
                'detalhes': [material.to_dict() for material in materiais]
            },
            'recursos_estrategicos': {
                'total_itens': total_recursos,
                'valor_total': valor_total_recursos,
                'detalhes': [recurso.to_dict() for recurso in recursos]
            },
            'periodo': {
                'inicio': periodo_inicio,
                'fim': periodo_fim
            }
        }
        
        return jsonify({'relatorio': resumo}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorios_bp.route('/dashboard-geral', methods=['GET'])
@jwt_required()
def dashboard_geral():
    """Dashboard geral com todas as informações principais"""
    try:
        from sqlalchemy import func
        
        # === ESTATÍSTICAS GERAIS ===
        total_secretarias = Secretaria.query.filter_by(ativa=True).count()
        total_projetos = Projeto.query.count()
        projetos_concluidos = Projeto.query.filter_by(status='concluido').count()
        projetos_atrasados = Projeto.query.filter_by(status='atrasado').count()
        
        # === PROJETOS POR STATUS ===
        projetos_por_status = db.session.query(
            Projeto.status,
            func.count(Projeto.id).label('total')
        ).group_by(Projeto.status).all()
        
        # === PROJETOS POR SECRETARIA ===
        projetos_por_secretaria = db.session.query(
            Secretaria.nome,
            func.count(Projeto.id).label('total')
        ).join(Projeto).group_by(Secretaria.id, Secretaria.nome).all()
        
        # === ALERTAS ===
        alertas = []
        
        # Projetos próximos do vencimento (próximos 7 dias)
        from datetime import timedelta
        data_limite = date.today() + timedelta(days=7)
        projetos_vencendo = Projeto.query.filter(
            Projeto.data_previsao_termino <= data_limite,
            Projeto.status.in_(['planejamento', 'execucao'])
        ).all()
        
        for projeto in projetos_vencendo:
            alertas.append({
                'tipo': 'projeto_vencendo',
                'mensagem': f'Projeto "{projeto.titulo}" vence em breve',
                'data': projeto.data_previsao_termino.isoformat() if projeto.data_previsao_termino else None,
                'projeto_id': projeto.id
            })
        
        # Projetos com recursos pendentes
        projetos_recursos_pendentes = Projeto.query.filter(
            Projeto.recursos_pendentes > 0
        ).all()
        
        for projeto in projetos_recursos_pendentes:
            alertas.append({
                'tipo': 'recursos_pendentes',
                'mensagem': f'Projeto "{projeto.titulo}" tem recursos pendentes: R$ {projeto.recursos_pendentes}',
                'valor': float(projeto.recursos_pendentes),
                'projeto_id': projeto.id
            })
        
        # === GASTOS RECENTES ===
        # Gastos do mês atual
        mes_atual = date.today().strftime('%Y-%m')
        gastos_mes_atual = db.session.query(
            func.sum(ContaPaga.valor)
        ).filter_by(mes_referencia=mes_atual).scalar() or 0
        
        # === MATERIAIS RECENTES ===
        data_limite_materiais = date.today() - timedelta(days=30)
        materiais_recentes = MaterialEscritorio.query.filter(
            MaterialEscritorio.data_entrada >= data_limite_materiais
        ).count()
        
        dashboard = {
            'estatisticas_gerais': {
                'total_secretarias': total_secretarias,
                'total_projetos': total_projetos,
                'projetos_concluidos': projetos_concluidos,
                'projetos_atrasados': projetos_atrasados,
                'taxa_conclusao': round((projetos_concluidos / total_projetos * 100) if total_projetos > 0 else 0, 2)
            },
            'projetos_por_status': [
                {'status': status, 'total': total} 
                for status, total in projetos_por_status
            ],
            'projetos_por_secretaria': [
                {'secretaria': nome, 'total': total} 
                for nome, total in projetos_por_secretaria
            ],
            'alertas': alertas,
            'resumo_financeiro': {
                'gastos_mes_atual': float(gastos_mes_atual),
                'materiais_recentes': materiais_recentes
            }
        }
        
        return jsonify({'dashboard': dashboard}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

