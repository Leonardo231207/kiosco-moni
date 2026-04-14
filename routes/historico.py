from flask import Blueprint, render_template, request
from models import db, MovimientoStock, Producto
from datetime import datetime, timedelta

historico_bp = Blueprint('historico', __name__, url_prefix='/historico')


@historico_bp.route('/')
def index():
    producto_id = request.args.get('producto_id', '')
    fechaDesde = request.args.get('fecha_desde', '')
    fechaHasta = request.args.get('fecha_hasta', '')
    
    query = MovimientoStock.query
    
    if producto_id:
        query = query.filter_by(producto_id=int(producto_id))
    
    if fechaDesde:
        desde = datetime.fromisoformat(fechaDesde)
        query = query.filter(MovimientoStock.timestamp >= desde.isoformat())
    
    if fechaHasta:
        hasta = datetime.fromisoformat(fechaHasta)
        hasta = hasta + timedelta(days=1)
        query = query.filter(MovimientoStock.timestamp < hasta.isoformat())
    
    movimientos = query.order_by(MovimientoStock.timestamp.desc()).all()
    
    productos = Producto.query.filter_by(activo=1).all()
    
    datos_diarios = {}
    for m in movimientos:
        if m.tipo == 'venta':
            fecha = m.timestamp[:10]
            if fecha not in datos_diarios:
                datos_diarios[fecha] = {'ventas': 0, 'ingreso': 0}
            datos_diarios[fecha]['ventas'] += 1
            producto = Producto.query.get(m.producto_id)
            if producto:
                datos_diarios[fecha]['ingreso'] += producto.precio_venta
    
    dias_ordenados = sorted(datos_diarios.items(), key=lambda x: x[0], reverse=True)
    
    return render_template('historico/index.html',
                           movimientos=movimientos,
                           productos=productos,
                           producto_id=producto_id,
                           fecha_desde=fechaDesde,
                           fecha_hasta=fechaHasta,
                           datos_diarios=dias_ordenados)


@historico_bp.route('/resumen')
def resumen():
    movimientos = MovimientoStock.query.filter_by(tipo='venta').all()
    
    total_ventas = len(movimientos)
    total_ingreso = 0
    
    for m in movimientos:
        producto = Producto.query.get(m.producto_id)
        if producto:
            total_ingreso += producto.precio_venta
    
    return render_template('historico/resumen.html',
                           total_ventas=total_ventas,
                           total_ingreso=total_ingreso)