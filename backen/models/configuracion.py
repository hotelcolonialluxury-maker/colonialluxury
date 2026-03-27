from models import db

class Configuracion(db.Model):
    __tablename__ = "configuracion"

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(255), nullable=False)

    @staticmethod
    def get(clave):
        c = Configuracion.query.filter_by(clave=clave).first()
        return c.valor if c else None

    @staticmethod
    def set(clave, valor):
        c = Configuracion.query.filter_by(clave=clave).first()
        if c:
            c.valor = valor
        else:
            c = Configuracion(clave=clave, valor=valor)
            db.session.add(c)
        db.session.commit()