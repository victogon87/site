from src.models.database import db, BaseModel
from datetime import date

class ContaPaga(BaseModel):
    __tablename__ = 'contas_pagas'
    
    tipo_conta = db.Column(db.String(50), nullable=False)  # agua, luz, internet, etc
    mes_referencia = db.Column(db.String(7), nullable=False)  # formato YYYY-MM
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_pagamento = db.Column(db.Date, nullable=False)
    arquivo_comprovante = db.Column(db.String(255))  # caminho para o arquivo PDF/scan
    observacoes = db.Column(db.Text)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'tipo_conta': self.tipo_conta,
            'mes_referencia': self.mes_referencia,
            'valor': float(self.valor) if self.valor else 0,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'arquivo_comprovante': self.arquivo_comprovante,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MaterialEscritorio(BaseModel):
    __tablename__ = 'materiais_escritorio'
    
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    quantidade = db.Column(db.Integer, nullable=False)
    unidade = db.Column(db.String(20))  # unidade, caixa, pacote, etc
    fornecedor = db.Column(db.String(100))
    data_entrada = db.Column(db.Date, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2))
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'quantidade': self.quantidade,
            'unidade': self.unidade,
            'fornecedor': self.fornecedor,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'valor_unitario': float(self.valor_unitario) if self.valor_unitario else 0,
            'valor_total': float(self.valor_unitario * self.quantidade) if self.valor_unitario and self.quantidade else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RecursoEstrategico(BaseModel):
    __tablename__ = 'recursos_estrategicos'
    
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_chegada = db.Column(db.Date, nullable=False)
    destino_uso = db.Column(db.String(200))
    fornecedor = db.Column(db.String(100))
    valor = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(20), default='recebido')  # recebido, em_uso, finalizado
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'quantidade': self.quantidade,
            'data_chegada': self.data_chegada.isoformat() if self.data_chegada else None,
            'destino_uso': self.destino_uso,
            'fornecedor': self.fornecedor,
            'valor': float(self.valor) if self.valor else 0,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

