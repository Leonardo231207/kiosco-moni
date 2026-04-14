from flask import Blueprint, send_file, request, jsonify, render_template
import os
import shutil
from datetime import datetime

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')


@backup_bp.route('/')
def index():
    from config import Config
    
    db_path = Config.DB_PATH
    tamano = 0
    if os.path.exists(db_path):
        tamano = os.path.getsize(db_path)
        if tamano > 1024 * 1024:
            tamano = f"{tamano / (1024*1024):.2f} MB"
        elif tamano > 1024:
            tamano = f"{tamano / 1024:.2f} KB"
        else:
            tamano = f"{tamano} bytes"
    
    return render_template('backup/index.html', db_path=db_path, tamano=tamano)


@backup_bp.route('/exportar')
def exportar():
    from config import Config
    
    db_path = Config.DB_PATH
    
    if not os.path.exists(db_path):
        return 'No hay base de datos', 404
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'kiosco_backup_{timestamp}.db'
    
    try:
        shutil.copy2(db_path, filename)
        return send_file(filename, as_attachment=True, download_name=filename)
    except Exception as e:
        return f'Error al exportar: {str(e)}', 500


@backup_bp.route('/importar', methods=['POST'])
def importar():
    from config import Config
    
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se recibió archivo'}), 400
    
    file = request.files['archivo']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    if not file.filename.endswith('.db'):
        return jsonify({'error': 'El archivo debe ser .db'}), 400
    
    try:
        db_path = Config.DB_PATH
        
        if os.path.exists(db_path):
            backup_path = db_path + '.backup'
            shutil.copy2(db_path, backup_path)
        
        file.save(db_path)
        
        return jsonify({'success': True, 'message': 'Base de datos restaurada. Reiniciá la app.'})
    except Exception as e:
        return jsonify({'error': f'Error al importar: {str(e)}'}), 500