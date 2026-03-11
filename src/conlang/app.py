import os, sys
from flask import Flask, session

base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

import conlang.paths as paths


def create_app():
    app = Flask(__name__)
    app.secret_key = "conlanger_secret_key"

    # 確保專案根目錄存在
    os.makedirs(paths.PROJECTS_ROOT, exist_ok=True)

    # 註冊藍圖
    from routes.api import api_bp
    from routes.views import views_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'Parabola',
            'current_project': session.get('current_project', 'None')
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)