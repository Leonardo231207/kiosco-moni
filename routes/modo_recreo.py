from flask import Blueprint, render_template, request, jsonify
from models import db, Producto, Stock, MovimientoStock
import logging

modo_recreo_bp = Blueprint('modo_recreo', __name__, url_prefix='/modo-recreo')


@modo_recreo_bp.route('/')
def index():
    return render_template('modo_recreo/index.html')


@modo_recreo_bp.route('/procesar', methods=['POST'])
def procesar():
    data = request.get_json()
    codigo = data.get('codigo', '').strip()
    
    try:
        producto = Producto.query.filter_by(codigo_barras=codigo, activo=1).first()
        
        if not producto:
            return jsonify({
                'success': False,
                'error': 'no_encontrado',
                'message': 'Código no reconocido. Verificar que el producto esté cargado.'
            })
        
        stock = Stock.query.filter_by(producto_id=producto.id).first()
        
        if not stock or stock.cantidad_actual <= 0:
            return jsonify({
                'success': False,
                'error': 'sin_stock',
                'message': f'ATENCIÓN: {producto.nombre} no tiene stock disponible.',
                'nombre': producto.nombre,
                'precio_venta': producto.precio_venta,
                'foto_path': producto.foto_path
            })
        
        stock.cantidad_actual -= 1
        
        movimiento = MovimientoStock(
            producto_id=producto.id,
            tipo='venta',
            cantidad=-1,
            origen='modo_recreo'
        )
        db.session.add(movimiento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'nombre': producto.nombre,
            'precio_venta': producto.precio_venta,
            'foto_path': producto.foto_path
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error en modo recreo: {e}')
        return jsonify({
            'success': False,
            'error': 'error',
            'message': 'Error interno. Intentalo de nuevo.'
        })
