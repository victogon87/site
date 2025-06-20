#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados iniciais
"""
import os
import sys
from datetime import date, timedelta

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app
from src.models.database import db
from src.models.usuario import Usuario
from src.models.secretaria import Secretaria
from src.models.projeto import Projeto
from src.models.recursos import ContaPaga, MaterialEscritorio, RecursoEstrategico

def criar_dados_iniciais():
    """Criar dados iniciais para o sistema"""
    
    with app.app_context():
        # Limpar dados existentes (cuidado em produção!)
        db.drop_all()
        db.create_all()
        
        print("🗄️  Criando usuários iniciais...")
        
        # Criar usuário administrador
        admin = Usuario(
            nome="Administrador",
            email="admin@secretaria.gov.br",
            nivel_acesso="administrador"
        )
        admin.set_senha("admin123")
        db.session.add(admin)
        
        # Criar usuário colaborador
        colaborador = Usuario(
            nome="João Silva",
            email="joao@secretaria.gov.br",
            nivel_acesso="colaborador"
        )
        colaborador.set_senha("colaborador123")
        db.session.add(colaborador)
        
        # Criar usuário visualizador
        visualizador = Usuario(
            nome="Maria Santos",
            email="maria@secretaria.gov.br",
            nivel_acesso="visualizador"
        )
        visualizador.set_senha("visualizador123")
        db.session.add(visualizador)
        
        db.session.commit()
        
        print("👥 Criando secretarias...")
        
        # Criar secretarias
        secretarias_data = [
            {
                "nome": "Secretaria de Educação",
                "responsavel": "Ana Costa",
                "contato": "ana.costa@educacao.gov.br",
                "email": "educacao@gov.br",
                "telefone": "(11) 3333-1111"
            },
            {
                "nome": "Secretaria de Saúde",
                "responsavel": "Dr. Carlos Mendes",
                "contato": "carlos.mendes@saude.gov.br",
                "email": "saude@gov.br",
                "telefone": "(11) 3333-2222"
            },
            {
                "nome": "Secretaria de Obras",
                "responsavel": "Eng. Roberto Lima",
                "contato": "roberto.lima@obras.gov.br",
                "email": "obras@gov.br",
                "telefone": "(11) 3333-3333"
            },
            {
                "nome": "Secretaria de Meio Ambiente",
                "responsavel": "Dra. Fernanda Oliveira",
                "contato": "fernanda.oliveira@meioambiente.gov.br",
                "email": "meioambiente@gov.br",
                "telefone": "(11) 3333-4444"
            }
        ]
        
        secretarias = []
        for data in secretarias_data:
            secretaria = Secretaria(**data)
            db.session.add(secretaria)
            secretarias.append(secretaria)
        
        db.session.commit()
        
        print("📋 Criando projetos...")
        
        # Criar projetos
        hoje = date.today()
        
        projetos_data = [
            {
                "titulo": "Reforma das Escolas Municipais",
                "descricao": "Reforma e modernização de 10 escolas municipais",
                "status": "execucao",
                "data_inicio": hoje - timedelta(days=30),
                "data_previsao_termino": hoje + timedelta(days=60),
                "progresso": 65,
                "recursos_aplicados": 150000.00,
                "recursos_pendentes": 40000.00,
                "observacoes": "Projeto em andamento, dentro do cronograma",
                "secretaria_id": 1  # Educação
            },
            {
                "titulo": "Construção do Novo Posto de Saúde",
                "descricao": "Construção de posto de saúde no bairro Vila Nova",
                "status": "planejamento",
                "data_inicio": hoje + timedelta(days=15),
                "data_previsao_termino": hoje + timedelta(days=180),
                "progresso": 10,
                "recursos_aplicados": 25000.00,
                "recursos_pendentes": 200000.00,
                "observacoes": "Aguardando liberação de recursos",
                "secretaria_id": 2  # Saúde
            },
            {
                "titulo": "Pavimentação da Rua Principal",
                "descricao": "Pavimentação asfáltica da rua principal do centro",
                "status": "execucao",
                "data_inicio": hoje - timedelta(days=15),
                "data_previsao_termino": hoje + timedelta(days=30),
                "progresso": 80,
                "recursos_aplicados": 120000.00,
                "recursos_pendentes": 15000.00,
                "observacoes": "Projeto quase concluído",
                "secretaria_id": 3  # Obras
            },
            {
                "titulo": "Programa de Arborização Urbana",
                "descricao": "Plantio de 500 árvores em praças e ruas da cidade",
                "status": "concluido",
                "data_inicio": hoje - timedelta(days=90),
                "data_previsao_termino": hoje - timedelta(days=10),
                "data_termino_real": hoje - timedelta(days=5),
                "progresso": 100,
                "recursos_aplicados": 35000.00,
                "recursos_pendentes": 0.00,
                "observacoes": "Projeto concluído com sucesso",
                "secretaria_id": 4  # Meio Ambiente
            },
            {
                "titulo": "Digitalização do Acervo Escolar",
                "descricao": "Digitalização de documentos e criação de biblioteca digital",
                "status": "atrasado",
                "data_inicio": hoje - timedelta(days=60),
                "data_previsao_termino": hoje - timedelta(days=5),
                "progresso": 45,
                "recursos_aplicados": 18000.00,
                "recursos_pendentes": 12000.00,
                "observacoes": "Projeto atrasado devido a problemas técnicos",
                "secretaria_id": 1  # Educação
            }
        ]
        
        for data in projetos_data:
            projeto = Projeto(**data)
            db.session.add(projeto)
        
        db.session.commit()
        
        print("💰 Criando registros de contas pagas...")
        
        # Criar contas pagas
        contas_data = [
            {
                "tipo_conta": "energia",
                "mes_referencia": "2024-12",
                "valor": 2500.00,
                "data_pagamento": hoje - timedelta(days=5),
                "observacoes": "Conta de energia elétrica do prédio principal"
            },
            {
                "tipo_conta": "agua",
                "mes_referencia": "2024-12",
                "valor": 800.00,
                "data_pagamento": hoje - timedelta(days=3),
                "observacoes": "Conta de água do prédio principal"
            },
            {
                "tipo_conta": "internet",
                "mes_referencia": "2024-12",
                "valor": 450.00,
                "data_pagamento": hoje - timedelta(days=10),
                "observacoes": "Internet fibra óptica 500MB"
            },
            {
                "tipo_conta": "telefone",
                "mes_referencia": "2024-12",
                "valor": 320.00,
                "data_pagamento": hoje - timedelta(days=8),
                "observacoes": "Telefonia fixa e móvel corporativa"
            }
        ]
        
        for data in contas_data:
            conta = ContaPaga(**data)
            db.session.add(conta)
        
        db.session.commit()
        
        print("📦 Criando registros de materiais...")
        
        # Criar materiais de escritório
        materiais_data = [
            {
                "nome": "Papel A4",
                "descricao": "Papel sulfite branco A4 75g",
                "quantidade": 50,
                "unidade": "resma",
                "fornecedor": "Papelaria Central",
                "data_entrada": hoje - timedelta(days=7),
                "valor_unitario": 25.00
            },
            {
                "nome": "Canetas Esferográficas",
                "descricao": "Canetas azuis BIC",
                "quantidade": 100,
                "unidade": "unidade",
                "fornecedor": "Material de Escritório Ltda",
                "data_entrada": hoje - timedelta(days=12),
                "valor_unitario": 2.50
            },
            {
                "nome": "Copos Descartáveis",
                "descricao": "Copos plásticos 200ml",
                "quantidade": 20,
                "unidade": "pacote",
                "fornecedor": "Distribuidora Hygiene",
                "data_entrada": hoje - timedelta(days=3),
                "valor_unitario": 8.00
            }
        ]
        
        for data in materiais_data:
            material = MaterialEscritorio(**data)
            db.session.add(material)
        
        db.session.commit()
        
        print("🎯 Criando recursos estratégicos...")
        
        # Criar recursos estratégicos
        recursos_data = [
            {
                "nome": "Computadores Desktop",
                "descricao": "Computadores Dell OptiPlex para renovação do parque tecnológico",
                "quantidade": 15,
                "data_chegada": hoje - timedelta(days=20),
                "destino_uso": "Secretarias municipais",
                "fornecedor": "TechSolutions Ltda",
                "valor": 45000.00,
                "status": "em_uso"
            },
            {
                "nome": "Veículo Utilitário",
                "descricao": "Fiat Strada para uso da Secretaria de Obras",
                "quantidade": 1,
                "data_chegada": hoje - timedelta(days=45),
                "destino_uso": "Secretaria de Obras",
                "fornecedor": "Concessionária AutoMax",
                "valor": 85000.00,
                "status": "em_uso"
            },
            {
                "nome": "Equipamentos Médicos",
                "descricao": "Kit de equipamentos básicos para posto de saúde",
                "quantidade": 1,
                "data_chegada": hoje - timedelta(days=10),
                "destino_uso": "Novo Posto de Saúde Vila Nova",
                "fornecedor": "MedEquip Hospitalar",
                "valor": 25000.00,
                "status": "recebido"
            }
        ]
        
        for data in recursos_data:
            recurso = RecursoEstrategico(**data)
            db.session.add(recurso)
        
        db.session.commit()
        
        print("✅ Dados iniciais criados com sucesso!")
        print("\n📋 Resumo:")
        print(f"   • {Usuario.query.count()} usuários")
        print(f"   • {Secretaria.query.count()} secretarias")
        print(f"   • {Projeto.query.count()} projetos")
        print(f"   • {ContaPaga.query.count()} contas pagas")
        print(f"   • {MaterialEscritorio.query.count()} materiais de escritório")
        print(f"   • {RecursoEstrategico.query.count()} recursos estratégicos")
        
        print("\n🔑 Credenciais de acesso:")
        print("   Administrador: admin@secretaria.gov.br / admin123")
        print("   Colaborador: joao@secretaria.gov.br / colaborador123")
        print("   Visualizador: maria@secretaria.gov.br / visualizador123")

if __name__ == "__main__":
    criar_dados_iniciais()

