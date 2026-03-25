from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    codigo_barras = db.Column(db.Text, unique=True, nullable=False)
    codigo_tipo = db.Column(db.Text, nullable=False)
    foto_path = db.Column(db.Text, nullable=True)
    precio_venta = db.Column(db.Float, nullable=False)
    precio_costo = db.Column(db.Float, nullable=True)
    activo = db.Column(db.Integer, default=1)
    creado_en = db.Column(db.Text, default=lambda: datetime.now().isoformat())
    actualizado_en = db.Column(db.Text, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    
    stock = db.relationship('Stock', backref='producto', uselist=False)
    recetas = db.relationship('Receta', backref='producto')


class Stock(db.Model):
    __tablename__ = 'stock'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, unique=True)
    cantidad_actual = db.Column(db.Integer, default=0)
    actualizado_en = db.Column(db.Text, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())


class MovimientoStock(db.Model):
    __tablename__ = 'movimientos_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    origen = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Text, default=lambda: datetime.now().isoformat())
    notas = db.Column(db.Text, nullable=True)
    
    producto = db.relationship('Producto')


class MateriaPrima(db.Model):
    __tablename__ = 'materia_prima'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text, unique=True, nullable=False)
    unidad = db.Column(db.Text, nullable=False)
    precio_por_unidad = db.Column(db.Float, nullable=False)
    activo = db.Column(db.Integer, default=1)
    actualizado_en = db.Column(db.Text, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    
    recetas = db.relationship('Receta', backref='materia_prima')


class Receta(db.Model):
    __tablename__ = 'recetas'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materia_prima.id'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    notas = db.Column(db.Text, nullable=True)


def init_db(app):
    with app.app_context():
        db.create_all()
