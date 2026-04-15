from flask import Blueprint, render_template, send_file
from models import Producto
import os
from glob import glob as glob_glob
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import barcode
from barcode.writer import ImageWriter
from config import Config
from PIL import Image
import logging

codigos_bp = Blueprint('codigos', __name__, url_prefix='/codigos')


def generar_codigo_png(codigo):
    os.makedirs(Config.BARCODE_PATH, exist_ok=True)
    
    codigo_limpio = codigo.strip()
    base_path = os.path.join(Config.BARCODE_PATH, codigo_limpio)
    
    existing = glob_glob(base_path + '.*')
    if existing:
        existing_png = base_path + '.png'
        if not os.path.exists(existing_png) and existing[0].endswith(('.gif', '.tif', '.tiff', '.jpg', '.jpeg')):
            try:
                img = Image.open(existing[0])
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(existing_png, 'PNG')
                return existing_png
            except:
                pass
        return existing[0]
    
    try:
        logging.info(f'Generando código: {codigo_limpio}')
        
        if len(codigo_limpio) == 13 and codigo_limpio.isdigit():
            bc = barcode.get('ean13', codigo_limpio, writer=ImageWriter())
        else:
            bc = barcode.get('code128', codigo_limpio, writer=ImageWriter())
        
        filename = bc.save(base_path)
        logging.info(f'Guardado como: {filename}')
        
        if os.path.exists(filename):
            return filename
        
    except Exception as e:
        logging.error(f'Error generando código {codigo}: {e}')
        import traceback
        logging.error(traceback.format_exc())
    
    return None


@codigos_bp.route('/')
def index():
    productos = Producto.query.filter_by(activo=1, codigo_tipo='interno').all()
    
    resultados = []
    for p in productos:
        img_path = generar_codigo_png(p.codigo_barras)
        basename = os.path.basename(img_path) if img_path else None
        resultados.append({
            'producto': p,
            'img_path': basename
        })
    
    return render_template('codigos/index.html', resultados=resultados)


@codigos_bp.route('/generar/<codigo>')
def generar(codigo):
    img_path = generar_codigo_png(codigo)
    if img_path and os.path.exists(img_path):
        return send_file(img_path, mimetype='image/png')
    return 'Código no generado', 404


@codigos_bp.route('/planilla')
def generar_planilla():
    productos = Producto.query.filter_by(activo=1, codigo_tipo='interno').all()
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    cols = 3
    rows_per_page = int((height - 30) / 90)
    margin = 15
    cell_w = (width - 2 * margin) / cols
    cell_h = 90
    
    for i, producto in enumerate(productos):
        if i > 0 and i % (cols * rows_per_page) == 0:
            c.showPage()
        
        pos = i % (cols * rows_per_page)
        row = pos // cols
        col = pos % cols
        
        x = margin + col * cell_w
        y = height - margin - (row + 1) * cell_h
        
        c.setLineWidth(0.5)
        c.rect(x, y, cell_w, cell_h)
        
        img_path = generar_codigo_png(producto.codigo_barras)
        
        if img_path and os.path.exists(img_path):
            try:
                from reportlab.lib.utils import ImageReader
                ir = ImageReader(img_path)
                c.drawImage(ir, x + 5, y + 18, width=cell_w - 10, height=70)
            except Exception as e:
                logging.warning(f'Error: {e}')
        
        c.setFont("Helvetica-Bold", 10)
        nombre = producto.nombre[:25]
        text_w = c.stringWidth(nombre, "Helvetica-Bold", 10)
        c.drawString(x + (cell_w - text_w) / 2, y + 5, nombre)
    
    c.save()
    logging.info('PDF generado')
    buffer.seek(0)
    
    return send_file(buffer, mimetype='application/pdf', download_name='codigos_barras.pdf')


@codigos_bp.route('/api/validar/<codigo>')
def validar_codigo(codigo):
    existente = Producto.query.filter_by(codigo_barras=codigo).first()
    return {'existe': existente is not None, 'codigo': codigo}