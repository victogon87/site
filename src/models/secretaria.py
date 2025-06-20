from src.models.database import db, BaseModel

class Secretaria(BaseModel):
    __tablename__ = 'secretarias'
    
    nome = db.Column(db.String(200), nullable=False)
    responsavel = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(100))
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    ativa = db.Column(db.Boolean, default=True)
    
    # Relacionamento com projetos
    projetos = db.relationship('Projeto', backref='secretaria', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'responsavel': self.responsavel,
            'contato': self.contato,
            'email': self.email,
            'telefone': self.telefone,
            'ativa': self.ativa,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_projetos': len(self.projetos) if self.projetos else 0
        }

