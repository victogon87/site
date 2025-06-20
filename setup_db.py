#!/usr/bin/env python3
"""
Script simples para criar e popular o banco de dados
"""
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Criar aplicação Flask simples
app = Flask(__name__)

# Configurar banco de dados
database_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Definir modelos diretamente aqui para simplificar
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nivel_acesso = db.Column(db.String(20), nullable=False, default='colaborador')
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Secretaria(db.Model):
    __tablename__ = 'secretarias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    responsavel = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(100))
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Projeto(db.Model):
    __tablename__ = 'projetos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='planejamento')
    data_inicio = db.Column(db.Date)
    data_previsao_termino = db.Column(db.Date)
    data_termino_real = db.Column(db.Date)
    progresso = db.Column(db.Integer, default=0)
    recursos_aplicados = db.Column(db.Numeric(12, 2), default=0)
    recursos_pendentes = db.Column(db.Numeric(12, 2), default=0)
    observacoes = db.Column(db.Text)
    secretaria_id = db.Column(db.Integer, db.ForeignKey('secretarias.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

def criar_dados_iniciais():
    """Criar dados iniciais para o sistema"""
    
    with app.app_context():
        print("🗄️  Criando banco de dados...")
        
        # Criar todas as tabelas
        db.create_all()
        
        print("👥 Criando usuários iniciais...")
        
        # Criar usuário administrador
        admin = Usuario(
            nome="Administrador",
            email="admin@secretaria.gov.br",
            senha_hash=generate_password_hash("admin123"),
            nivel_acesso="administrador"
        )
        db.session.add(admin)
        
        # Criar usuário colaborador
        colaborador = Usuario(
            nome="João Silva",
            email="joao@secretaria.gov.br",
            senha_hash=generate_password_hash("colaborador123"),
            nivel_acesso="colaborador"
        )
        db.session.add(colaborador)
        
        # Criar usuário visualizador
        visualizador = Usuario(
            nome="Maria Santos",
            email="maria@secretaria.gov.br",
            senha_hash=generate_password_hash("visualizador123"),
            nivel_acesso="visualizador"
        )
        db.session.add(visualizador)
        
        db.session.commit()
        
        print("🏢 Criando secretarias...")
        
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
        
        print("✅ Dados iniciais criados com sucesso!")
        print("\n📋 Resumo:")
        print(f"   • {Usuario.query.count()} usuários")
        print(f"   • {Secretaria.query.count()} secretarias")
        print(f"   • {Projeto.query.count()} projetos")
        
        print("\n🔑 Credenciais de acesso:")
        print("   Administrador: admin@secretaria.gov.br / admin123")
        print("   Colaborador: joao@secretaria.gov.br / colaborador123")
        print("   Visualizador: maria@secretaria.gov.br / visualizador123")
        
        print(f"\n📁 Banco de dados criado em: {database_path}")

if __name__ == "__main__":
    criar_dados_iniciais()

