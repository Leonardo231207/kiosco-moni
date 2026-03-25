from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Producto, Stock, MovimientoStock
import logging

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')


@stock_bp.route('/')
def index():
    productos = Producto.query.filter_by(activo=1).all()
    return render_template('stock/index.html', productos=productos)


@stock_bp.route('/cargar', methods=['POST'])
def cargar():
    try:
        producto_id = request.form['producto_id']
        cantidad = int(request.form['cantidad'])
        
        if cantidad <= 0:
            flash('La cantidad debe ser mayor a 0', 'error')
            return redirect(url_for('stock.index'))
        
        stock = Stock.query.filter_by(producto_id=producto_id).first()
        if not stock:
            stock = Stock(producto_id=producto_id, cantidad_actual=0)
            db.session.add(stock)
        
        stock.cantidad_actual += cantidad
        
        movimiento = MovimientoStock(
            producto_id=producto_id,
            tipo='carga',
            cantidad=cantidad,
            origen='carga_manual'
        )
        db.session.add(movimiento)
        db.session.commit()
        
        flash(f'Stock cargado: +{cantidad} unidades', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error al cargar stock: {e}')
        flash('No se pudo guardar. Intentalo de nuevo o avisale a Leo.', 'error')
    
    return redirect(url_for('stock.index'))
