from werkzeug.security import generate_password_hash, check_password_hash
from src.models.database import db, BaseModel

class Usuario(BaseModel):
    __tablename__ = 'usuarios'
    
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nivel_acesso = db.Column(db.String(20), nullable=False, default='colaborador')  # administrador, visualizador, colaborador
    ativo = db.Column(db.Boolean, default=True)
    
    def set_senha(self, senha):
        """Define a senha do usuário (hash)"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'nivel_acesso': self.nivel_acesso,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

