from src.models.database import db, BaseModel
from datetime import date

class Projeto(BaseModel):
    __tablename__ = 'projetos'
    
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='planejamento')  # planejamento, execucao, concluido, atrasado
    data_inicio = db.Column(db.Date)
    data_previsao_termino = db.Column(db.Date)
    data_termino_real = db.Column(db.Date)
    progresso = db.Column(db.Integer, default=0)  # 0 a 100
    recursos_aplicados = db.Column(db.Numeric(12, 2), default=0)
    recursos_pendentes = db.Column(db.Numeric(12, 2), default=0)
    observacoes = db.Column(db.Text)
    
    # Chave estrangeira para secretaria
    secretaria_id = db.Column(db.Integer, db.ForeignKey('secretarias.id'), nullable=False)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'status': self.status,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_previsao_termino': self.data_previsao_termino.isoformat() if self.data_previsao_termino else None,
            'data_termino_real': self.data_termino_real.isoformat() if self.data_termino_real else None,
            'progresso': self.progresso,
            'recursos_aplicados': float(self.recursos_aplicados) if self.recursos_aplicados else 0,
            'recursos_pendentes': float(self.recursos_pendentes) if self.recursos_pendentes else 0,
            'observacoes': self.observacoes,
            'secretaria_id': self.secretaria_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def dias_restantes(self):
        """Calcula quantos dias restam para o término do projeto"""
        if self.data_previsao_termino:
            delta = self.data_previsao_termino - date.today()
            return delta.days
        return None
    
    @property
    def esta_atrasado(self):
        """Verifica se o projeto está atrasado"""
        if self.status == 'concluido':
            return False
        if self.data_previsao_termino:
            return date.today() > self.data_previsao_termino
        return False

