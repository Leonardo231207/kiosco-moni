from flask import Blueprint, render_template, send_file
from models import Producto
import os
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from config import Config

codigos_bp = Blueprint('codigos', __name__, url_prefix='/codigos')


@codigos_bp.route('/')
def index():
    productos = Producto.query.filter_by(activo=1, codigo_tipo='interno').all()
    
    for p in productos:
        generar_codigo_barras(p.codigo_barras)
    
    return render_template('codigos/index.html', productos=productos)


@codigos_bp.route('/generar/<codigo>')
def generar(codigo):
    img = generar_codigo_barras(codigo)
    return send_file(img, mimetype='image/png')


@codigos_bp.route('/planilla')
def generar_planilla():
    productos = Producto.query.filter_by(activo=1, codigo_tipo='interno').all()
    
    for p in productos:
        generar_codigo_barras(p.codigo_barras)
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    cols = 3
    rows = 5
    cell_width = width / cols
    cell_height = height / rows
    
    for i, producto in enumerate(productos):
        row = i // cols
        col = i % cols
        
        if row >= rows:
            c.showPage()
            row = 0
            col = 0
        
        x = col * cell_width
        y = height - (row + 1) * cell_height
        
        img_path = os.path.join(Config.BARCODE_PATH, f'{producto.codigo_barras}.png')
        if os.path.exists(img_path):
            c.drawImage(img_path, x + 10, y + 10, width=cell_width - 20, height=cell_height - 40)
        
        c.drawString(x + 10, y + 5, producto.nombre[:20])
    
    c.save()
    buffer.seek(0)
    
    return send_file(buffer, mimetype='application/pdf', download_name='codigos_barras.pdf')


def generar_codigo_barras(codigo):
    os.makedirs(Config.BARCODE_PATH, exist_ok=True)
    img_path = os.path.join(Config.BARCODE_PATH, f'{codigo}.png')
    
    if not os.path.exists(img_path):
        try:
            ean = barcode.get_barcode_class('ean13')
            ean(codigo).write(writer=ImageWriter(), output=img_path.replace('.png', ''))
        except Exception:
            pass
    
    return img_path


@codigos_bp.route('/api/validar/<codigo>')
def validar_codigo(codigo):
    from models import Producto
    existente = Producto.query.filter_by(codigo_barras=codigo).first()
    return {'existe': existente is not None, 'codigo': codigo}
