from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Producto, MateriaPrima, Receta
import logging

recetas_bp = Blueprint('recetas', __name__, url_prefix='/recetas')


def calcular_costo_receta(producto_id):
    recetas = Receta.query.filter_by(producto_id=producto_id).all()
    costo = 0
    for r in recetas:
        mp = MateriaPrima.query.get(r.materia_prima_id)
        if mp:
            costo += r.cantidad * mp.precio_por_unidad
    return costo


def actualizar_precio_costo_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if producto:
        producto.precio_costo = calcular_costo_receta(producto_id)
        db.session.commit()


@recetas_bp.route('/')
def index():
    materias_primas = MateriaPrima.query.filter_by(activo=1).all()
    
    productos = Producto.query.filter_by(activo=1).all()
    productos_con_receta = []
    productos_sin_receta = []
    
    for p in productos:
        recetas = Receta.query.filter_by(producto_id=p.id).all()
        if recetas:
            costo = calcular_costo_receta(p.id)
            ingredientes = []
            for r in recetas:
                mp = MateriaPrima.query.get(r.materia_prima_id)
                if mp:
                    ingredientes.append({
                        'nombre': mp.nombre,
                        'cantidad': r.cantidad,
                        'unidad': mp.unidad
                    })
            
            margen = ((p.precio_venta - costo) / p.precio_venta * 100) if p.precio_venta > 0 else 0
            
            productos_con_receta.append({
                'id': p.id,
                'nombre': p.nombre,
                'precio_venta': p.precio_venta,
                'costo': costo,
                'margen': margen,
                'ingredientes': ingredientes
            })
        else:
            productos_sin_receta.append(p)
    
    return render_template('recetas/index.html',
                           materias_primas=materias_primas,
                           productos_con_receta=productos_con_receta,
                           productos_sin_receta=productos_sin_receta)


@recetas_bp.route('/materia-prima', methods=['POST'])
def guardar_materia_prima():
    try:
        mp = MateriaPrima(
            nombre=request.form['nombre'],
            unidad=request.form['unidad'],
            precio_por_unidad=float(request.form['precio_por_unidad'])
        )
        db.session.add(mp)
        db.session.commit()
        flash('Materia prima guardada', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error al guardar materia prima: {e}')
        flash('No se pudo guardar. Intentalo de nuevo o avisale a Leo.', 'error')
    
    return redirect(url_for('recetas.index'))


@recetas_bp.route('/materia-prima/<int:id>', methods=['DELETE'])
def eliminar_materia_prima(id):
    try:
        mp = MateriaPrima.query.get_or_404(id)
        mp.activo = 0
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error al eliminar materia prima: {e}')
        return 'Error', 500


@recetas_bp.route('/receta', methods=['POST'])
def guardar_receta():
    try:
        producto_id = request.form['producto_id']
        materia_primas = request.form.getlist('materia_prima_id[]')
        cantidades = request.form.getlist('cantidad[]')
        
        Receta.query.filter_by(producto_id=producto_id).delete()
        
        for mp_id, cant in zip(materia_primas, cantidades):
            if mp_id and cant:
                receta = Receta(
                    producto_id=producto_id,
                    materia_prima_id=int(mp_id),
                    cantidad=float(cant)
                )
                db.session.add(receta)
        
        actualizar_precio_costo_producto(producto_id)
        
        flash('Receta guardada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Error al guardar receta: {e}')
        flash('No se pudo guardar. Intentalo de nuevo o avisale a Leo.', 'error')
    
    return redirect(url_for('recetas.index'))
