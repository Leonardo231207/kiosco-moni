from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Producto, Stock
import logging

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')


def calcular_precio_costo(producto_id):
    from models import Receta, MateriaPrima
    recetas = Receta.query.filter_by(producto_id=producto_id).all()
    costo = 0
    for r in recetas:
        mp = MateriaPrima.query.get(r.materia_prima_id)
        if mp:
            costo += r.cantidad * mp.precio_por_unidad
    return costo


@productos_bp.route('/')
def index():
    productos = Producto.query.filter_by(activo=1).all()
    for p in productos:
        if not p.stock:
            s = Stock(producto_id=p.id, cantidad_actual=0)
            db.session.add(s)
            db.session.commit()
    return render_template('productos/index.html', productos=productos)


@productos_bp.route('/nuevo')
def nuevo():
    return render_template('productos/nuevo.html')


@productos_bp.route('/crear', methods=['POST'])
def crear():
    try:
        existente = Producto.query.filter_by(codigo_barras=request.form['codigo_barras']).first()
        if existente:
            flash(f"Este código ya está registrado para el producto '{existente.nombre}'", 'error')
            return redirect(url_for('productos.nuevo'))
        
        producto = Producto(
            nombre=request.form['nombre'],
            codigo_barras=request.form['codigo_barras'],
            codigo_tipo=request.form['codigo_tipo'],
            precio_venta=float(request.form['precio_venta']),
            foto_path=request.form.get('foto_path', '')
        )
        db.session.add(producto)
        db.session.flush()
        
        stock = Stock(producto_id=producto.id, cantidad_actual=0)
        db.session.add(stock)
        db.session.commit()
        
        flash('Producto creado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error al crear producto: {e}')
        flash('No se pudo guardar. Intentalo de nuevo o avisale a Leo.', 'error')
    
    return redirect(url_for('productos.index'))


@productos_bp.route('/editar/<int:id>')
def editar(id):
    producto = Producto.query.get_or_404(id)
    return render_template('productos/editar.html', producto=producto)


@productos_bp.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    producto = Producto.query.get_or_404(id)
    try:
        producto.nombre = request.form['nombre']
        producto.precio_venta = float(request.form['precio_venta'])
        producto.foto_path = request.form.get('foto_path', '')
        db.session.commit()
        flash('Producto actualizado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error al actualizar producto: {e}')
        flash('No se pudo guardar. Intentalo de nuevo o avisale a Leo.', 'error')
    
    return redirect(url_for('productos.index'))


@productos_bp.route('/eliminar/<int:id>')
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    try:
        producto.activo = 0
        db.session.commit()
        flash('Producto dado de baja', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error al eliminar producto: {e}')
        flash('No se pudo guardar. Intentalo de nuevo o avisale a Leo.', 'error')
    
    return redirect(url_for('productos.index'))
