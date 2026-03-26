import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
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
        codigo = request.form.get('codigo_barras') or request.form.get('codigo_barras_interno')
        
        if not codigo:
            flash('Completá el campo Código de Barras para continuar.', 'error')
            return redirect(url_for('productos.nuevo'))
        
        existente = Producto.query.filter_by(codigo_barras=codigo).first()
        if existente:
            flash(f"Este código ya está registrado para el producto '{existente.nombre}'", 'error')
            return redirect(url_for('productos.nuevo'))
        
        producto = Producto(
            nombre=request.form['nombre'],
            codigo_barras=codigo,
            codigo_tipo=request.form['codigo_tipo'],
            precio_venta=float(request.form['precio_venta']),
            foto_path=''
        )
        db.session.add(producto)
        db.session.flush()
        
        foto_path = guardar_foto(producto.id)
        if foto_path:
            producto.foto_path = foto_path
        
        stock = Stock(producto_id=producto.id, cantidad_actual=0)
        db.session.add(stock)
        db.session.commit()
        
        flash('Producto creado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error al crear producto: {e}')
        flash('No se pudo guardar. Intentalo de nuevo o avisale a Leo.', 'error')
    
    return redirect(url_for('productos.index'))


def guardar_foto(producto_id):
    from config import Config
    
    if 'foto_file' not in request.files:
        return ''
    
    file = request.files['foto_file']
    if file.filename == '':
        return ''
    
    try:
        os.makedirs(Config.IMAGENES_PATH, exist_ok=True)
        
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = '.jpg'
        
        filename = f'producto_{producto_id}{ext}'
        filepath = os.path.join(Config.IMAGENES_PATH, filename)
        
        file.save(filepath)
        
        return f'imagenes/{filename}'
    except Exception as e:
        logging.error(f'Error al guardar foto: {e}')
        return ''


@productos_bp.route('/subir-foto/<int:producto_id>', methods=['POST'])
def subir_foto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    
    if 'foto_file' not in request.files:
        return jsonify({'error': 'No se recibió archivo'}), 400
    
    file = request.files['foto_file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    try:
        from config import Config
        import os as os_module
        
        os_module.makedirs(Config.IMAGENES_PATH, exist_ok=True)
        
        if producto.foto_path:
            old_path = os.path.join(os.path.dirname(Config.IMAGENES_PATH), producto.foto_path)
            if os_module.path.exists(old_path):
                try:
                    os_module.remove(old_path)
                except:
                    pass
        
        ext = os.path.splitext(file.filename)[1] or '.jpg'
        filename = f'producto_{producto_id}{ext}'
        filepath = os.path.join(Config.IMAGENES_PATH, filename)
        
        file.save(filepath)
        
        producto.foto_path = f'imagenes/{filename}'
        db.session.commit()
        
        return jsonify({'success': True, 'foto_path': producto.foto_path})
    except Exception as e:
        logging.error(f'Error al subir foto: {e}')
        return jsonify({'error': 'Error al guardar'}), 500


@productos_bp.route('/generar-codigo-interno')
def generar_codigo_interno():
    from utils import generar_codigo_interno
    try:
        codigo = generar_codigo_interno()
        return jsonify({'codigo': codigo})
    except Exception as e:
        logging.error(f'Error al generar código interno: {e}')
        return jsonify({'error': str(e)}), 500


@productos_bp.route('/validar-codigo/<codigo>')
def validar_codigo(codigo):
    from utils import validar_ean13
    existe = Producto.query.filter_by(codigo_barras=codigo).first() is not None
    valido = validar_ean13(codigo) if codigo.isdigit() and len(codigo) == 13 else True
    return jsonify({
        'existe': existe,
        'valido': valido,
        'codigo': codigo
    })


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
