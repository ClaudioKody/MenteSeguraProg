import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from app import analyze_risk, conversation_replies, mood_from_text

def test_detecta_riesgo_critico():
    nivel, _, _ = analyze_risk("Me quiero hacer daño")
    assert nivel == "critico"

def test_responde_a_tristeza_y_registra_mood():
    respuestas = conversation_replies("Me siento triste", "bajo")
    assert respuestas
    assert mood_from_text("Hoy fui al gimnasio y me sentí súper bien") == "motivado/a"
