from __future__ import annotations


import io
import os
import secrets
import sqlite3
import urllib.request
from datetime import date, datetime
from pathlib import Path


from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS
from services.login_guard import clear_failures, is_blocked, register_failure


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "mentesegura.db"
PIN_DE_PRUEBA = "1234"
ADMIN_EMAIL = "admin@mentesegura.local"
ADMIN_PASSWORD = "Admin123!"
ADMIN_DOCUMENTO = "30123456"
IMAGE_DIR = BASE_DIR / "static" / "images"
IMAGE_FILES = ["hero-sunset.jpg", "wildflowers.jpg", "journal-morning.jpg"]
FALLBACK_QUOTES = [
    ("No tenés que resolver todo hoy. Dar un paso pequeño también es avanzar.", "Mente Segura"),
    ("Tu ritmo es válido. Hay belleza en seguir intentando con suavidad.", "Mente Segura"),
    ("Lo que sentís merece un espacio, una pausa y un poco de ternura.", "Mente Segura"),
    ("A veces cuidarte empieza por escucharte sin juzgarte.", "Mente Segura"),
    ("Incluso los días nublados guardan una parte de luz.", "Mente Segura"),
]


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("MENTE_SEGURA_SECRET", "mentesegura-dev-secret")
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}}, supports_credentials=True)
APP_INSTANCE_TOKEN = secrets.token_urlsafe(24)


# La interfaz Jinja2 existente se conserva. La API se registra al final del módulo,
# cuando todas las funciones de negocio ya están disponibles.




def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db




def init_db() -> None:
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL DEFAULT '',
                contacto_confianza TEXT NOT NULL DEFAULT '',
                rol TEXT NOT NULL DEFAULT 'usuario',
                documento TEXT NOT NULL DEFAULT '',
                pin TEXT NOT NULL DEFAULT '1234',
                creado_en TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notas (
                id_nota INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                fecha_hora TEXT NOT NULL,
                titulo TEXT NOT NULL DEFAULT '',
                texto TEXT NOT NULL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
            );
            CREATE TABLE IF NOT EXISTS frases_motivacionales (
                id_frase INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                texto TEXT NOT NULL,
                autor TEXT NOT NULL,
                url_frase TEXT NOT NULL,
                imagen TEXT NOT NULL DEFAULT 'hero-sunset.jpg',
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
            );
            CREATE TABLE IF NOT EXISTS biblioteca (
                id_recurso INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL DEFAULT '',
                tipo TEXT NOT NULL DEFAULT 'Libro',
                url TEXT NOT NULL,
                creado_en TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ayuda_profesional (
                id_ayuda INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                telefono TEXT NOT NULL,
                descripcion TEXT NOT NULL DEFAULT '',
                creado_en TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chat_mensajes (
                id_mensaje INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                rol TEXT NOT NULL,
                texto TEXT NOT NULL,
                creado_en TEXT NOT NULL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
            );
            CREATE TABLE IF NOT EXISTS alertas_crisis (
                id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                nivel TEXT NOT NULL,
                motivo TEXT NOT NULL,
                contacto TEXT NOT NULL DEFAULT '',
                creado_en TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'simulada',
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
            );
            CREATE TABLE IF NOT EXISTS estados_animo (
                id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                estado TEXT NOT NULL,
                origen TEXT NOT NULL DEFAULT 'diario',
                creado_en TEXT NOT NULL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
            );
        """)
        # Migrations for databases created in Sprint 1.
        user_cols = {row["name"] for row in db.execute("PRAGMA table_info(usuarios)")}
        migrations = {
            "apellido": "ALTER TABLE usuarios ADD COLUMN apellido TEXT NOT NULL DEFAULT ''",
            "email": "ALTER TABLE usuarios ADD COLUMN email TEXT NOT NULL DEFAULT ''",
            "password_hash": "ALTER TABLE usuarios ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''",
            "contacto_confianza": "ALTER TABLE usuarios ADD COLUMN contacto_confianza TEXT NOT NULL DEFAULT ''",
            "rol": "ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT 'usuario'",
            "documento": "ALTER TABLE usuarios ADD COLUMN documento TEXT NOT NULL DEFAULT ''",
        }
        for column, statement in migrations.items():
            if column not in user_cols:
                db.execute(statement)
        note_cols = {row["name"] for row in db.execute("PRAGMA table_info(notas)")}
        if "titulo" not in note_cols:
            db.execute("ALTER TABLE notas ADD COLUMN titulo TEXT NOT NULL DEFAULT ''")
        if "estado_animo" not in note_cols:
            db.execute("ALTER TABLE notas ADD COLUMN estado_animo TEXT NOT NULL DEFAULT ''")
        quote_cols = {row["name"] for row in db.execute("PRAGMA table_info(frases_motivacionales)")}
        if "imagen" not in quote_cols:
            db.execute("ALTER TABLE frases_motivacionales ADD COLUMN imagen TEXT NOT NULL DEFAULT 'hero-sunset.jpg'")


        legacy = db.execute("SELECT * FROM usuarios ORDER BY id_usuario LIMIT 1").fetchone()
        if not legacy:
            db.execute("INSERT INTO usuarios(nombre,apellido,email,password_hash,contacto_confianza,rol,documento,pin,creado_en) VALUES(?,?,?,?,?,?,?,?,?)", ("Sofi", "", "sofi@mentesegura.local", generate_password_hash("Sofi123!"), "", "usuario", "", PIN_DE_PRUEBA, datetime.now().isoformat(timespec="seconds")))
        else:
            if not legacy["email"]:
                db.execute("UPDATE usuarios SET email=? WHERE id_usuario=?", ("sofi@mentesegura.local", legacy["id_usuario"]))
            if not legacy["password_hash"]:
                db.execute("UPDATE usuarios SET password_hash=? WHERE id_usuario=?", (generate_password_hash("Sofi123!"), legacy["id_usuario"]))
        admin = db.execute("SELECT id_usuario FROM usuarios WHERE rol='admin' LIMIT 1").fetchone()
        if not admin:
            db.execute("INSERT INTO usuarios(nombre,apellido,email,password_hash,contacto_confianza,rol,documento,pin,creado_en) VALUES(?,?,?,?,?,?,?,?,?)", ("Administrador", "Mente Segura", ADMIN_EMAIL, generate_password_hash(ADMIN_PASSWORD), "", "admin", ADMIN_DOCUMENTO, "", datetime.now().isoformat(timespec="seconds")))


        if not db.execute("SELECT 1 FROM biblioteca LIMIT 1").fetchone():
            now = datetime.now().isoformat(timespec="seconds")
            db.executemany("INSERT INTO biblioteca(titulo,descripcion,tipo,url,creado_en) VALUES(?,?,?,?,?)", [
                ("Pausas conscientes", "Ideas sencillas para volver al presente.", "Guía", "https://www.who.int/es/news-room/fact-sheets/detail/mental-health-strengthening-our-response", now),
                ("Cuidar la salud mental", "Información introductoria y recursos de autocuidado.", "Lectura", "https://www.argentina.gob.ar/salud/mental-y-adicciones", now),
            ])
        if not db.execute("SELECT 1 FROM ayuda_profesional LIMIT 1").fetchone():
            now = datetime.now().isoformat(timespec="seconds")
            db.executemany("INSERT INTO ayuda_profesional(nombre,tipo,telefono,descripcion,creado_en) VALUES(?,?,?,?,?)", [
                ("Línea de asistencia", "Asistencia", "135", "Atención inmediata en CABA y Gran Buenos Aires.", now),
                ("Emergencias", "Emergencias", "911", "Si existe riesgo inmediato, contactá a emergencias.", now),
            ])




@app.before_request
def ensure_database():
    if not DATABASE.exists():
        init_db()




def current_user():
    uid = session.get("usuario_id")
    if not uid:
        return None
    with get_db() as db:
        return db.execute("SELECT * FROM usuarios WHERE id_usuario=?", (uid,)).fetchone()




def user_id() -> int:
    return int(session.get("usuario_id", 1))




def auth_required():
    if not current_user():
        return redirect(url_for("login"))
    return None




def admin_required():
    user = current_user()
    if not user or user["rol"] != "admin":
        flash("Necesitás ingresar como administrador.", "error")
        return redirect(url_for("login"))
    return None




def diary_required():
    if not current_user() or not session.get("diario_abierto") or session.get("app_instance_token") != APP_INSTANCE_TOKEN:
        return redirect(url_for("ingresar"))
    return None




CRITICAL_RISK_TERMS = ("suicid", "suicidarme", "matarme", "quiero matarme", "me quiero matar", "quitarme la vida", "hacerme daño", "hacer daño", "me quiero hacer daño", "lastimarme", "me voy a lastimar", "autoles", "no quiero vivir")
HIGH_RISK_TERMS = ("depresión profunda", "depresion profunda", "no puedo más", "no puedo mas", "me quiero desaparecer", "bullying", "acoso")
ANXIETY_TERMS = ("ataque de ansiedad", "crisis de ansiedad", "ansiedad extrema", "pánico", "panico", "no puedo respirar")




def analyze_risk(text: str) -> tuple[str, str, list[str]]:
    normalized = text.lower().strip()
    if any(term in normalized for term in CRITICAL_RISK_TERMS):
        return "critico", "Se detectaron expresiones relacionadas con autolesión o riesgo inmediato.", ["Contactá ahora a una persona de confianza", "Llamá a emergencias si existe peligro inmediato", "No te quedes a solas"]
    if any(term in normalized for term in HIGH_RISK_TERMS):
        return "alto", "Se detectaron señales que merecen acompañamiento profesional.", ["Hablá hoy con tu contacto de confianza", "Buscá apoyo profesional", "Probá una respiración guiada"]
    if any(term in normalized for term in ANXIETY_TERMS):
        return "moderado", "Parece que estás atravesando mucha activación o ansiedad.", ["Hacé una pausa de respiración", "Apoyá los pies en el piso", "Tomá agua lentamente"]
    return "bajo", "Gracias por compartir lo que estás sintiendo.", ["Escribí una cosa que necesitás hoy", "Probá una pausa consciente", "Podés registrar tu estado en Mi evolución"]




def preventive_reply(text: str, level: str) -> str:
    if level == "critico":
        return "Lamento que estés pasando por esto. No estás solo/a. Este chat es preventivo y no reemplaza a profesionales. Contactá ahora a tu persona de confianza o a emergencias de tu zona si hay peligro inmediato."
    if level == "alto":
        return "Gracias por contarlo. Lo que sentís merece apoyo real y cercano. Este espacio puede acompañarte de manera preventiva, pero no reemplaza la atención profesional."
    if level == "moderado":
        return "Te leo. Podemos bajar un poco el ritmo con una respiración guiada. Este chat ofrece orientación preventiva y no reemplaza a un profesional."
    return "Te leo con atención. Podemos ordenar lo que sentís paso a paso. Recordá que este chat brinda apoyo preventivo y no reemplaza la atención profesional."




def conversation_replies(text: str, level: str) -> list[str]:
    normalized = text.lower().strip()
    if level == "critico":
        return [
            "Lamento que estés pasando por esto. No estás solo/a. Este chat es preventivo y no reemplaza a profesionales.",
            "¿Estás en peligro inmediato ahora? Contactá a tu persona de confianza, no te quedes a solas y llamá a emergencias de tu zona si hace falta.",
        ]
    if level == "alto":
        return [
            "Gracias por contarlo. Lo que sentís merece apoyo real y cercano; no tenés que atravesarlo en soledad.",
            "¿Querés contarme qué pasó hoy? También podés hablar con tu contacto de confianza, buscar apoyo profesional o hacer una respiración guiada.",
        ]
    if level == "moderado":
        return [
            "Te leo. Parece que estás atravesando mucha activación o ansiedad; vamos de a un paso.",
            "¿Preferís respirar conmigo, contarme qué lo desencadenó o pensar una acción pequeña para este momento?",
        ]
    if any(word in normalized for word in ("gracias por preguntar", "te agradezco", "me ayudaste")):
        return [
            "Gracias a vos por confiarme lo que te pasa.",
            "Para seguir acompañándote: ¿qué fue lo más difícil de este momento y qué te ayudaría a sentirte apenas un poco mejor?",
        ]
    if any(word in normalized for word in ("muchas gracias", "muchísimas gracias", "mil gracias", "gracias")):
        return [
            "De nada. Me alegra poder acompañarte en este momento.",
            "¿Cómo estás ahora: un poco más tranquilo/a, igual que antes o todavía necesitás apoyo?",
        ]
    if any(word in normalized for word in ("estoy bien", "me siento bien", "todo bien", "estoy tranquilo", "estoy tranquila")):
        return [
            "Me alegra saberlo. También es importante reconocer cuando aparece un momento de calma.",
            "¿Qué pasó hoy que te ayudó a sentirte así? Podemos identificarlo para que tengas ese recurso presente.",
        ]
    if normalized in ("sí", "si", "dale", "ok", "okay", "bueno", "está bien", "esta bien"):
        return [
            "Bien, vamos paso a paso.",
            "Elegí por dónde seguimos: ¿querés contarme qué pasó, hacer una respiración guiada o pensar una acción pequeña para ahora?",
        ]
    if any(word in normalized for word in ("no sé", "no se", "no tengo idea", "no puedo elegir")):
        return [
            "Está bien no tener una respuesta ahora; no tenés que decidir todo de una vez.",
            "Podemos empezar por algo simple: ¿preferís que te haga una pregunta sobre cómo te sentís o querés probar una respiración corta?",
        ]
    if any(word in normalized for word in ("tristeza", "triste", "llorar", "llorando", "vacío", "vacio")):
        return [
            "La tristeza puede sentirse pesada, y no tenés que atravesarla en soledad.",
            "Podés probar algo pequeño: tomar agua, salir a caminar unos minutos, escribir lo que necesitás o hablar con alguien de confianza. ¿Cuál de estas opciones te parece posible hoy?",
        ]
    if any(word in normalized for word in ("ansiedad", "ansioso", "ansiosa", "nervios", "preocupado", "preocupada")):
        return [
            "La ansiedad puede hacer que todo parezca urgente. Vamos a bajar un cambio sin exigirte resolverlo todo.",
            "Probá inhalar lento y exhalar más lento, apoyá los pies en el piso y elegí una sola acción: respirar, tomar agua o pedir compañía.",
        ]
    if any(word in normalized for word in ("enojo", "enojado", "enojada", "bronca", "rabia", "frustrado", "frustrada")):
        return [
            "Tiene sentido que quieras encontrar una forma de descargar lo que sentís sin lastimarte ni lastimar a nadie.",
            "Podés alejarte unos minutos de la situación, respirar, escribir lo que pasó o hablar cuando te sientas un poco más tranquilo/a.",
        ]
    if any(word in normalized for word in ("cansancio", "cansado", "cansada", "agotado", "agotada", "sin energía", "sin energia")):
        return [
            "Parece que necesitás recuperar un poco de energía, y descansar también es cuidarte.",
            "Elegí algo amable y pequeño: descansar unos minutos, comer algo, tomar agua o pedir ayuda con lo que hoy te pesa.",
        ]
    if any(word in normalized for word in ("hola", "buen día", "buen dia", "buenas", "hey")):
        return ["Hola. ¿Cómo te sentís hoy?", "Podés contarme cómo fue tu día, hacer una pausa de respiración o registrar lo que estás sintiendo."]
    if any(word in normalized for word in ("me siento mal", "triste", "llorar", "vacío", "vacio")):
        return ["Gracias por decirlo. No tenés que resolver todo ahora; podemos quedarnos un momento con lo que sentís.", "¿Es más tristeza, ansiedad o cansancio? Si te sirve, podés dar una caminata breve, tomar agua o hablar con alguien cercano."]
    if any(word in normalized for word in ("me siento mejor", "estoy mejor", "feliz", "logré", "logre", "gimnasio", "gym", "orgulloso", "orgullosa", "disfruté", "disfrute", "avancé", "avance", "satisfecho", "satisfecha", "súper bien", "super bien")):
        return ["¡Qué alegría leerte así! Lo que hiciste hoy también cuenta como progreso.", "Reconocer estos momentos puede ayudarte a repetir lo que te hace bien. ¿Querés guardar este logro en tu registro?"]
    return ["Podemos seguir conversando paso a paso.", "¿Qué te ayudaría más ahora: contarme qué pasó, pensar una acción pequeña o hacer una respiración guiada?"]




def mood_from_text(text: str) -> str:
    normalized = text.lower()
    mapping = {
        "motivado/a": ("motivad", "feliz", "content", "orgull", "logré", "logre", "mejor", "gimnasio", "gym", "disfrut", "avancé", "avance", "satisfech", "súper bien", "super bien"),
        "tranquilo/a": ("tranquil", "en paz", "calma", "bien", "seren"),
        "ansioso/a": ("ansiedad", "ansioso", "nervios", "preocup"),
        "triste": ("triste", "llor", "depre", "vacío", "vacio"),
        "agotado/a": ("agot", "cansad", "sin energía", "sin energia"),
    }
    for mood, terms in mapping.items():
        if any(term in normalized for term in terms):
            return mood
    return "sin registrar"




def daily_quote() -> sqlite3.Row:
    today = date.today().isoformat()
    with get_db() as db:
        found = db.execute("SELECT * FROM frases_motivacionales WHERE id_usuario=? AND fecha=?", (user_id(), today)).fetchone()
        if found:
            return found
        text, author = FALLBACK_QUOTES[date.today().day % len(FALLBACK_QUOTES)]
        source = "https://www.positive-api.online/phrase/esp"
        try:
            import json
            with urllib.request.urlopen(source, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
                text, author = data.get("text") or text, data.get("author") or author
        except Exception:
            pass
        image = IMAGE_FILES[date.today().day % len(IMAGE_FILES)]
        db.execute("INSERT INTO frases_motivacionales(id_usuario,fecha,texto,autor,url_frase,imagen) VALUES(?,?,?,?,?,?)", (user_id(), today, text, author, source, image))
        return db.execute("SELECT * FROM frases_motivacionales WHERE id_usuario=? AND fecha=?", (user_id(), today)).fetchone()




@app.context_processor
def globals_for_templates():
    user = current_user()
    return {"usuario_nombre": user["nombre"] if user else "", "current_user": user, "diario_abierto": session.get("diario_abierto", False)}




@app.get("/")
def inicio():
    return redirect(url_for("login"))




@app.get("/hoy")
def hoy():
    if not current_user():
        return redirect(url_for("login"))
    if current_user()["rol"] == "admin":
        return redirect(url_for("admin_dashboard"))
    session.pop("diario_abierto", None)
    session.pop("app_instance_token", None)
    quote = daily_quote()
    image_url = url_for("static", filename=f"images/{quote['imagen']}", _external=True)
    with get_db() as db:
        other_quotes = db.execute("SELECT * FROM frases_motivacionales WHERE id_usuario=? ORDER BY id_frase DESC LIMIT 3", (user_id(),)).fetchall()
    return render_template("hoy.html", quote=quote, image_url=image_url, other_quotes=other_quotes)




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        is_admin = request.form.get("es_admin") == "on"
        documento = request.form.get("documento", "").strip()
        if is_blocked(email):
            flash("Demasiados intentos. Esperá unos minutos antes de volver a ingresar.", "error")
            return render_template("login.html")
        with get_db() as db:
            user = db.execute("SELECT * FROM usuarios WHERE lower(email)=?", (email,)).fetchone()
        valid = user and check_password_hash(user["password_hash"], password)
        if valid and is_admin:
            valid = user["rol"] == "admin" and user["documento"] == documento
        if valid and not is_admin and user["rol"] == "admin":
            valid = False
        if valid:
            clear_failures(email)
            session.clear()
            session["usuario_id"] = user["id_usuario"]
            if user["rol"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("hoy"))
        register_failure(email)
        flash("Los datos de acceso no son válidos.", "error")
    return render_template("login.html")




@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        contacto = request.form.get("contacto_confianza", "").strip()
        if not all([nombre, apellido, email, password, contacto]):
            flash("Completá todos los campos obligatorios.", "error")
        else:
            try:
                with get_db() as db:
                    db.execute("INSERT INTO usuarios(nombre,apellido,email,password_hash,contacto_confianza,rol,documento,pin,creado_en) VALUES(?,?,?,?,?,?,?,?,?)", (nombre, apellido, email, generate_password_hash(password), contacto, "usuario", "", PIN_DE_PRUEBA, datetime.now().isoformat(timespec="seconds")))
                flash("Registro creado. Ya podés iniciar sesión.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Ese correo ya está registrado.", "error")
    return render_template("registro.html")




@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))




@app.route("/ingresar", methods=["GET", "POST"])
def ingresar():
    if (response := auth_required()):
        return response
    if request.method == "POST":
        if request.form.get("pin", "") == PIN_DE_PRUEBA:
            session.update(diario_abierto=True, app_instance_token=APP_INSTANCE_TOKEN)
            return redirect(url_for("diario"))
        flash("PIN incorrecto", "error")
    return render_template("ingresar.html")




@app.get("/salir")
def salir():
    session.pop("diario_abierto", None)
    session.pop("app_instance_token", None)
    return redirect(url_for("hoy"))




@app.get("/diario")
def diario():
    if (response := diary_required()):
        return response
    with get_db() as db:
        notes = db.execute("SELECT * FROM notas WHERE id_usuario=? ORDER BY fecha_hora DESC", (user_id(),)).fetchall()
    return render_template("diario.html", notes=notes)




@app.route("/diario/nueva", methods=["GET", "POST"])
def nueva_nota():
    if (response := diary_required()):
        return response
    if request.method == "POST":
        text = request.form.get("texto", "").strip()
        title = request.form.get("titulo", "").strip()
        mood = request.form.get("estado_animo", "").strip() or mood_from_text(text)
        if text:
            with get_db() as db:
                cursor = db.execute("INSERT INTO notas(id_usuario,fecha_hora,titulo,texto,estado_animo) VALUES(?,?,?,?,?)", (user_id(), datetime.now().isoformat(timespec="seconds"), title, text, mood))
                db.execute("INSERT INTO estados_animo(id_usuario,estado,origen,creado_en) VALUES(?,?,?,?)", (user_id(), mood, "diario", datetime.now().isoformat(timespec="seconds")))
            return redirect(url_for("ver_nota", id_nota=cursor.lastrowid))
        flash("Escribí algo antes de guardar", "error")
    now = datetime.now()
    return render_template("nueva.html", now_date=now.strftime("%d %b. %Y").lstrip("0"), now_time=now.strftime("%H:%M"))




@app.get("/diario/nota/<int:id_nota>")
def ver_nota(id_nota: int):
    if (response := diary_required()):
        return response
    with get_db() as db:
        note = db.execute("SELECT * FROM notas WHERE id_nota=? AND id_usuario=?", (id_nota, user_id())).fetchone()
    if not note:
        return redirect(url_for("diario"))
    return render_template("nota.html", note=note, note_image=IMAGE_FILES[(id_nota - 1) % len(IMAGE_FILES)])




@app.route("/diario/nota/<int:id_nota>/editar", methods=["GET", "POST"])
def editar_nota(id_nota: int):
    if (response := diary_required()):
        return response
    with get_db() as db:
        note = db.execute("SELECT * FROM notas WHERE id_nota=? AND id_usuario=?", (id_nota, user_id())).fetchone()
        if not note:
            return redirect(url_for("diario"))
        if request.method == "POST":
            title = request.form.get("titulo", "").strip()
            text = request.form.get("texto", "").strip()
            mood = request.form.get("estado_animo", "").strip() or mood_from_text(text)
            if text:
                db.execute("UPDATE notas SET titulo=?, texto=?, estado_animo=? WHERE id_nota=? AND id_usuario=?", (title, text, mood, id_nota, user_id()))
                db.execute("INSERT INTO estados_animo(id_usuario,estado,origen,creado_en) VALUES(?,?,?,?)", (user_id(), mood, "diario", datetime.now().isoformat(timespec="seconds")))
                flash("Nota guardada", "success")
                return redirect(url_for("ver_nota", id_nota=id_nota))
    return render_template("editar.html", note=note, note_image=IMAGE_FILES[(id_nota - 1) % len(IMAGE_FILES)])




@app.post("/diario/eliminar/<int:id_nota>")
def eliminar_nota(id_nota: int):
    if (response := diary_required()):
        return response
    with get_db() as db:
        db.execute("DELETE FROM notas WHERE id_nota=? AND id_usuario=?", (id_nota, user_id()))
    return redirect(url_for("diario"))




@app.get("/diario/descargar")
def descargar_registro():
    if (response := diary_required()):
        return response
    with get_db() as db:
        notes = db.execute("SELECT * FROM notas WHERE id_usuario=? ORDER BY fecha_hora DESC", (user_id(),)).fetchall()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("MSTitle", parent=styles["Title"], fontName="Times-Italic", textColor=HexColor("#76538b"), fontSize=30, leading=34, alignment=1, spaceAfter=8)
    meta = ParagraphStyle("MSMeta", parent=styles["Normal"], fontName="Helvetica", textColor=HexColor("#9a87a2"), fontSize=10, alignment=1, letterSpacing=1.2, spaceAfter=18)
    intro = ParagraphStyle("MSIntro", parent=styles["Normal"], fontName="Helvetica-Oblique", textColor=HexColor("#6e5b76"), fontSize=11, leading=17, alignment=1, spaceAfter=22)
    date_style = ParagraphStyle("MSDate", parent=styles["Normal"], fontName="Helvetica-Bold", textColor=HexColor("#8d638e"), fontSize=10, spaceBefore=12, spaceAfter=5)
    note_heading = ParagraphStyle("MSHeading", parent=styles["Heading2"], fontName="Times-Italic", textColor=HexColor("#68487c"), fontSize=16, leading=20, spaceAfter=6)
    body = ParagraphStyle("MSBody", parent=styles["BodyText"], fontName="Helvetica", textColor=HexColor("#302936"), fontSize=11, leading=17, spaceAfter=6)
    story = [Paragraph("Mente Segura", title), Paragraph("DIARIO EMOCIONAL · REGISTRO PERSONAL", meta), Paragraph("Un espacio para escucharte con calma, reconocer lo que sentís y guardar tus pequeños avances.", intro)]
    for note in notes:
        clean = note["texto"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        note_title = note["titulo"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        heading = f"{note_title}" if note_title else "Registro personal"
        story += [Paragraph(note["fecha_hora"].replace("T", " · "), date_style), Paragraph(heading, note_heading), Paragraph(clean, body), Spacer(1, 10)]
    if not notes:
        story.append(Paragraph("Todavía no hay entradas guardadas.", body))
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name="registro-mente-segura.pdf")




@app.route("/chat", methods=["GET", "POST"])
def chat():
    if (response := auth_required()):
        return response
    if current_user()["rol"] == "admin":
        return redirect(url_for("admin_dashboard"))
    suggestions, risk_level, risk_message = [], "bajo", ""
    if request.method == "POST":
        text = request.form.get("mensaje", "").strip()
        if text:
            risk_level, risk_message, suggestions = analyze_risk(text)
            replies = conversation_replies(text, risk_level)
            detected_mood = mood_from_text(text)
            with get_db() as db:
                now = datetime.now().isoformat(timespec="seconds")
                db.execute("INSERT INTO chat_mensajes(id_usuario,rol,texto,creado_en) VALUES(?,?,?,?)", (user_id(), "usuario", text, now))
                for reply in replies:
                    db.execute("INSERT INTO chat_mensajes(id_usuario,rol,texto,creado_en) VALUES(?,?,?,?)", (user_id(), "asistente", reply, now))
                if detected_mood != "sin registrar":
                    db.execute("INSERT INTO estados_animo(id_usuario,estado,origen,creado_en) VALUES(?,?,?,?)", (user_id(), detected_mood, "chat", now))
                if risk_level == "critico":
                    db.execute("INSERT INTO alertas_crisis(id_usuario,nivel,motivo,contacto,creado_en) VALUES(?,?,?,?,?)", (user_id(), risk_level, risk_message, current_user()["contacto_confianza"], now))
            if risk_level == "critico":
                flash("Aviso preventivo registrado para tu contacto de confianza. Si hay peligro inmediato, llamá a emergencias.", "error")
    with get_db() as db:
        messages = db.execute("SELECT * FROM chat_mensajes WHERE id_usuario=? ORDER BY id_mensaje", (user_id(),)).fetchall()
        latest_alert = db.execute("SELECT * FROM alertas_crisis WHERE id_usuario=? ORDER BY id_alerta DESC LIMIT 1", (user_id(),)).fetchone()
    return render_template("chat.html", messages=messages, suggestions=suggestions, risk_level=risk_level, risk_message=risk_message, latest_alert=latest_alert)




@app.post("/chat/limpiar")
def limpiar_chat():
    if (response := auth_required()):
        return response
    with get_db() as db:
        db.execute("DELETE FROM chat_mensajes WHERE id_usuario=?", (user_id(),))
    flash("Conversación eliminada.", "success")
    return redirect(url_for("chat"))




@app.get("/respirar")
def respirar():
    if (response := auth_required()):
        return response
    return render_template("respirar.html")




@app.get("/evolucion")
def evolucion():
    if (response := auth_required()):
        return response
    if current_user()["rol"] == "admin":
        return redirect(url_for("admin_dashboard"))
    with get_db() as db:
        mood_rows = db.execute("SELECT estado, COUNT(*) AS total FROM estados_animo WHERE id_usuario=? GROUP BY estado ORDER BY total DESC", (user_id(),)).fetchall()
        recent = db.execute("SELECT estado, substr(creado_en,1,10) AS dia FROM estados_animo WHERE id_usuario=? ORDER BY creado_en DESC LIMIT 14", (user_id(),)).fetchall()
        week_notes = db.execute("SELECT COUNT(*) AS total FROM notas WHERE id_usuario=? AND fecha_hora >= datetime('now','-7 day')", (user_id(),)).fetchone()["total"]
        week_chat = db.execute("SELECT COUNT(*) AS total FROM chat_mensajes WHERE id_usuario=? AND rol='usuario' AND creado_en >= datetime('now','-7 day')", (user_id(),)).fetchone()["total"]
        positive_count = db.execute("SELECT COUNT(*) AS total FROM estados_animo WHERE id_usuario=? AND estado='motivado/a'", (user_id(),)).fetchone()["total"]
        week_positive = db.execute("SELECT COUNT(*) AS total FROM estados_animo WHERE id_usuario=? AND estado='motivado/a' AND creado_en >= datetime('now','-7 day')", (user_id(),)).fetchone()["total"]
    total_entries = sum(row["total"] for row in mood_rows)
    chart_labels = [row["dia"] for row in reversed(recent)]
    chart_values = [row["estado"] for row in reversed(recent)]
    if week_positive:
        achievement = f"¡Felicitaciones! Registraste {week_positive} {'avance' if week_positive == 1 else 'avances'} positivos esta semana. Eso también es progreso."
    elif week_notes + week_chat >= 3:
        achievement = "Tu constancia también es autocuidado. Cada vez que te escuchás, estás avanzando."
    else:
        achievement = "Cada pequeño registro cuenta. Volvé cuando lo necesites y prestá atención también a lo que te hace bien."
    return render_template("evolucion.html", mood_rows=mood_rows, total_entries=total_entries, week_notes=week_notes, week_chat=week_chat, positive_count=positive_count, week_positive=week_positive, achievement=achievement, chart_labels=chart_labels, chart_values=chart_values)




@app.get("/frase/<int:id_frase>/descargar")
def descargar_frase(id_frase: int):
    with get_db() as db:
        quote = db.execute("SELECT * FROM frases_motivacionales WHERE id_frase=?", (id_frase,)).fetchone()
    if not quote:
        return redirect(url_for("hoy"))
    source = Image.open(IMAGE_DIR / quote["imagen"]).convert("RGB")
    canvas = ImageOps.fit(source, (1080, 1350), method=Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", canvas.size, (35, 22, 45, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle((0, 760, 1080, 1350), fill=(35, 22, 45, 178))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(canvas)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    quote_font = ImageFont.truetype(font_path, 78) if Path(font_path).exists() else ImageFont.load_default()
    author_font = ImageFont.truetype(font_bold_path, 38) if Path(font_bold_path).exists() else ImageFont.load_default()
    small_font = ImageFont.truetype(font_path, 28) if Path(font_path).exists() else ImageFont.load_default()


    words = quote["texto"].split()
    lines, line = [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=quote_font)[2] > 890 and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    y = 820 - (len(lines) * 45)
    for text_line in lines:
        box = draw.textbbox((0, 0), text_line, font=quote_font)
        x = (1080 - (box[2] - box[0])) // 2
        draw.text((x, y), text_line, font=quote_font, fill=(255, 250, 252, 255))
        y += 98
    author = f"— {quote['autor']}"
    box = draw.textbbox((0, 0), author, font=author_font)
    draw.text(((1080 - (box[2] - box[0])) // 2, y + 42), author, font=author_font, fill=(255, 238, 249, 255))
    label = "MENTE SEGURA · FRASE DEL DÍA"
    box = draw.textbbox((0, 0), label, font=small_font)
    draw.text(((1080 - (box[2] - box[0])) // 2, 55), label, font=small_font, fill=(255, 255, 255, 230))
    buffer = io.BytesIO()
    canvas.convert("RGB").save(buffer, format="JPEG", quality=94)
    buffer.seek(0)
    return send_file(buffer, mimetype="image/jpeg", as_attachment=True, download_name=f"frase-{quote['fecha']}.jpg")




@app.get("/biblioteca")
def biblioteca():
    if (response := auth_required()):
        return response
    with get_db() as db:
        resources = db.execute("SELECT * FROM biblioteca ORDER BY id_recurso DESC").fetchall()
    return render_template("biblioteca.html", resources=resources)




@app.get("/ayuda")
def ayuda():
    if (response := auth_required()):
        return response
    with get_db() as db:
        contacts = db.execute("SELECT * FROM ayuda_profesional ORDER BY id_ayuda DESC").fetchall()
    return render_template("ayuda.html", contacts=contacts)




@app.get("/admin")
def admin_dashboard():
    if (response := admin_required()):
        return response
    with get_db() as db:
        total_users = db.execute("SELECT COUNT(*) AS total FROM usuarios WHERE rol='usuario'").fetchone()["total"]
        total_resources = db.execute("SELECT COUNT(*) AS total FROM biblioteca").fetchone()["total"]
        total_help = db.execute("SELECT COUNT(*) AS total FROM ayuda_profesional").fetchone()["total"]
        growth_rows = db.execute("SELECT substr(creado_en,1,10) AS dia, COUNT(*) AS total FROM usuarios WHERE rol='usuario' GROUP BY dia ORDER BY dia").fetchall()
        resources = db.execute("SELECT * FROM biblioteca ORDER BY id_recurso DESC").fetchall()
        contacts = db.execute("SELECT * FROM ayuda_profesional ORDER BY id_ayuda DESC").fetchall()
    chart_labels = [row["dia"] for row in growth_rows]
    chart_values = [row["total"] for row in growth_rows]
    return render_template("admin.html", total_users=total_users, total_resources=total_resources, total_help=total_help, resources=resources, contacts=contacts, chart_labels=chart_labels, chart_values=chart_values)




@app.post("/admin/biblioteca/guardar")
def admin_guardar_recurso():
    if (response := admin_required()):
        return response
    resource_id = request.form.get("id_recurso")
    values = (request.form.get("titulo", "").strip(), request.form.get("descripcion", "").strip(), request.form.get("tipo", "Recurso").strip(), request.form.get("url", "").strip())
    if not all(values[0::3]):
        flash("El título y la URL son obligatorios.", "error")
    else:
        with get_db() as db:
            if resource_id:
                db.execute("UPDATE biblioteca SET titulo=?, descripcion=?, tipo=?, url=? WHERE id_recurso=?", (*values, resource_id))
            else:
                db.execute("INSERT INTO biblioteca(titulo,descripcion,tipo,url,creado_en) VALUES(?,?,?,?,?)", (*values, datetime.now().isoformat(timespec="seconds")))
        flash("Recurso actualizado.", "success")
    return redirect(url_for("admin_dashboard"))




@app.post("/admin/biblioteca/eliminar/<int:resource_id>")
def admin_eliminar_recurso(resource_id):
    if (response := admin_required()):
        return response
    with get_db() as db:
        db.execute("DELETE FROM biblioteca WHERE id_recurso=?", (resource_id,))
    return redirect(url_for("admin_dashboard"))




@app.post("/admin/ayuda/guardar")
def admin_guardar_ayuda():
    if (response := admin_required()):
        return response
    help_id = request.form.get("id_ayuda")
    values = (request.form.get("nombre", "").strip(), request.form.get("tipo", "Asistencia").strip(), request.form.get("telefono", "").strip(), request.form.get("descripcion", "").strip())
    if not values[0] or not values[2]:
        flash("El nombre y el teléfono son obligatorios.", "error")
    else:
        with get_db() as db:
            if help_id:
                db.execute("UPDATE ayuda_profesional SET nombre=?, tipo=?, telefono=?, descripcion=? WHERE id_ayuda=?", (*values, help_id))
            else:
                db.execute("INSERT INTO ayuda_profesional(nombre,tipo,telefono,descripcion,creado_en) VALUES(?,?,?,?,?)", (*values, datetime.now().isoformat(timespec="seconds")))
        flash("Contacto actualizado.", "success")
    return redirect(url_for("admin_dashboard"))




@app.post("/admin/ayuda/eliminar/<int:help_id>")
def admin_eliminar_ayuda(help_id):
    if (response := admin_required()):
        return response
    with get_db() as db:
        db.execute("DELETE FROM ayuda_profesional WHERE id_ayuda=?", (help_id,))
    return redirect(url_for("admin_dashboard"))




from api.routes import register_api
from api.openapi import register_docs
register_api(app)
register_docs(app)




if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
