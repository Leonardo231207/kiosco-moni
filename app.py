import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

from config import Config
from models import db, init_db


def setup_logging(app):
    os.makedirs(os.path.dirname(Config.LOG_PATH), exist_ok=True)
    
    handler = RotatingFileHandler(
        Config.LOG_PATH,
        maxBytes=1_000_000,
        backupCount=3
    )
    handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    return app.logger


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    logger = setup_logging(app)
    logger.info('Iniciando aplicacion Kiosco')
    
    db.init_app(app)
    init_db(app)
    
    from routes.productos import productos_bp
    from routes.stock import stock_bp
    from routes.modo_recreo import modo_recreo_bp
    from routes.codigos import codigos_bp
    from routes.recetas import recetas_bp
    
    app.register_blueprint(productos_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(modo_recreo_bp)
    app.register_blueprint(codigos_bp)
    app.register_blueprint(recetas_bp)
    
    @app.route('/')
    def index():
        from flask import redirect
        return redirect('/productos')
    
    logger.info('Aplicacion iniciada correctamente')
    return app, logger


if __name__ == '__main__':
    app, logger = create_app()
    
    logger.info(f'Iniciando servidor en http://localhost:{Config.PUERTO}')
    app.run(host='0.0.0.0', port=Config.PUERTO, debug=Config.DEBUG)
