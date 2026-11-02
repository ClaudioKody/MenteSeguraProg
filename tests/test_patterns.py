import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from services.app_factory import create_app
from repositories.nota_repository import NotaRepository
from strategies.chat_strategy import seleccionar_estrategia

def test_factory_crea_app_configurable():
    app = create_app({"TESTING": True})
    assert app.config["TESTING"] is True

def test_repository_y_strategy():
    class Cursor:
        lastrowid = 7
    class DB:
        def execute(self, *_):
            return Cursor()
    assert NotaRepository(DB()).crear(1, "ahora", "t", "c", "bien") == 7
    assert "avance" in seleccionar_estrategia("bajo", "motivado/a").responder("fui al gimnasio")
    assert "peligro" in seleccionar_estrategia("critico", "triste").responder("riesgo")
