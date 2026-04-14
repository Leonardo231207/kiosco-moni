import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    DEBUG = True
    LOG_LEVEL = 'DEBUG' if DEBUG else 'ERROR'
    SECRET_KEY = 'kiosco-moni-2026-seguro'
    
    DB_PATH = os.path.join(BASE_DIR, 'kiosco.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    PUERTO = 5000
    
    BARCODE_PATH = os.path.join(BASE_DIR, 'static', 'codigos_barras')
    IMAGENES_PATH = os.path.join(BASE_DIR, 'static', 'imagenes')
    LOG_PATH = os.path.join(BASE_DIR, 'logs', 'kiosco_errors.log')
