from __future__ import annotations 
from datetime import datetime 
from flask import Blueprint, jsonify, request, session 
from werkzeug.security import check_password_hash, generate_password_hash 
 
 
 
def register_api(app): 
    api = Blueprint("api", __name__)
    from app import analyze_risk, conversation_replies, daily_quote, get_db, mood_from_text, PIN_DE_PRUEBA 
    from repositories.nota_repository import NotaRepository 
    from strategies.chat_strategy import seleccionar_estrategia 
 
    def user(): 
        from app import current_user 
        return current_user() 
 
    def auth(): 
        current = user() 
        return (current, None) if current else (None, (jsonify(error="autenticacion_requerida"), 401)) 
 
    def admin(): 
        current, error = auth() 
        if error: 
            return None, error 
        return (current, None) if current["rol"] == "admin" else (None, (jsonify(error="permiso_denegado"), 403)) 
 
    @api.get("/health") 
    def health(): 
        return jsonify(status="ok", service="mentesegura-api") 
 
    @api.post("/auth/registro") 
    def registro_api(): 
        data = request.get_json(silent=True) or {} 
        values = [str(data.get(k, "")).strip() for k in ("nombre", "apellido", "email", "contacto_confianza")] 
        password = str(data.get("password", "")) 
        if not all(values) or len(password) < 6: 
            return jsonify(error="datos_invalidos"), 400 
        try: 
            with get_db() as db: 
                cursor = db.execute("INSERT INTO usuarios(nombre,apellido,email,password_hash,contacto_confianza,rol,documento,pin,creado_en) VALUES(?,?,?,?,?,?,?,?,?)", (*values[:3], generate_password_hash(password), values[3], "usuario", "", PIN_DE_PRUEBA, datetime.now().isoformat(timespec="seconds"))) 
            return jsonify(id=cursor.lastrowid, message="registro_creado"), 201 
        except Exception: 
            return jsonify(error="correo_ya_registrado"), 409 
 
    @api.post("/auth/login") 
    def login_api(): 
        data = request.get_json(silent=True) or {} 
        email = str(data.get("email", "")).strip().lower() 
        password = str(data.get("password", "")) 
        documento = str(data.get("documento", "")).strip() 
        with get_db() as db: 
            record = db.execute("SELECT * FROM usuarios WHERE lower(email)=?", (email,)).fetchone() 
        valid = record and check_password_hash(record["password_hash"], password) 
        if valid and record["rol"] == "admin" and documento != record["documento"]: 
            valid = False 
        if not valid: 
            return jsonify(error="credenciales_invalidas"), 401 
        session.clear(); session["usuario_id"] = record["id_usuario"] 
        return jsonify(user={"id": record["id_usuario"], "nombre": record["nombre"], "rol": record["rol"]}) 
 
    @api.post("/auth/logout") 
    def logout_api(): 
        session.clear(); return jsonify(status="ok") 
 
    @api.get("/me") 
    def me(): 
        current, error = auth() 
        if error: return error 
        return jsonify(id=current["id_usuario"], nombre=current["nombre"], apellido=current["apellido"], rol=current["rol"], contacto_confianza=current["contacto_confianza"]) 
 
    @api.post("/diario/pin") 
    def open_diary(): 
        current, error = auth() 
        if error: return error 
        data = request.get_json(silent=True) or {} 
        if str(data.get("pin", "")) != str(current["pin"] or PIN_DE_PRUEBA): 
            return jsonify(error="pin_incorrecto"), 401 
        session["diario_abierto"] = True 
        return jsonify(status="ok") 
 
    @api.get("/frases") 
    def quotes(): 
        current, error = auth() 
        if error: return error 
        quote = daily_quote() 
        return jsonify(id=quote["id_frase"], texto=quote["texto"], autor=quote["autor"], imagen=f"/static/images/{quote['imagen']}", url=quote["url_frase"], descarga=f"/frase/{quote['id_frase']}/descargar") 
 
    @api.get("/notas") 
    def notes(): 
        current, error = auth() 
        if error: return error 
        with get_db() as db: rows = NotaRepository(db).listar_por_usuario(current["id_usuario"]) 
        return jsonify(items=[dict(r) for r in rows]) 
 
    @api.post("/notas") 
    def create_note(): 
        current, error = auth() 
        if error: return error 
        data = request.get_json(silent=True) or {}; text = str(data.get("texto", "")).strip() 
        if not text: return jsonify(error="texto_requerido"), 400 
        mood = str(data.get("estado_animo", "")).strip() or mood_from_text(text); now = datetime.now().isoformat(timespec="seconds") 
        with get_db() as db: 
            cursor_id = NotaRepository(db).crear(current["id_usuario"], now, str(data.get("titulo", "")).strip(), text, mood) 
            db.execute("INSERT INTO estados_animo(id_usuario,estado,origen,creado_en) VALUES(?,?,?,?)", (current["id_usuario"], mood, "diario", now)) 
        return jsonify(id=cursor_id, estado_animo=mood), 201 
 
    @api.put("/notas/") 
    def update_note(note_id): 
        current, error = auth() 
        if error: return error 
        data = request.get_json(silent=True) or {}; text = str(data.get("texto", "")).strip() 
        if not text: return jsonify(error="texto_requerido"), 400 
        with get_db() as db: NotaRepository(db).actualizar(note_id, current["id_usuario"], str(data.get("titulo", "")).strip(), text, str(data.get("estado_animo", "")).strip() or mood_from_text(text)) 
        return jsonify(status="updated") 
 
    @api.delete("/notas/") 
    def delete_note(note_id): 
        current, error = auth() 
        if error: return error 
        with get_db() as db: NotaRepository(db).eliminar(note_id, current["id_usuario"]) 
        return jsonify(status="deleted") 
 
    @api.get("/chat") 
    def chat_history(): 
        current, error = auth() 
        if error: return error 
        with get_db() as db: rows = db.execute("SELECT rol,texto,creado_en FROM chat_mensajes WHERE id_usuario=? ORDER BY id_mensaje", (current["id_usuario"],)).fetchall() 
        return jsonify(items=[dict(r) for r in rows]) 
 
    @api.post("/chat") 
    def chat_message(): 
        current, error = auth() 
        if error: return error 
        data = request.get_json(silent=True) or {}; text = str(data.get("mensaje", "")).strip() 
        if not text: return jsonify(error="mensaje_requerido"), 400 
        level, risk_message, suggestions = analyze_risk(text); mood = mood_from_text(text); replies = conversation_replies(text, level) 
        strategy_reply = seleccionar_estrategia(level, mood).responder(text) 
        if strategy_reply not in replies: replies.append(strategy_reply) 
        now = datetime.now().isoformat(timespec="seconds") 
        with get_db() as db: 
            db.execute("INSERT INTO chat_mensajes(id_usuario,rol,texto,creado_en) VALUES(?,?,?,?)", (current["id_usuario"], "usuario", text, now)) 
            for reply in replies: db.execute("INSERT INTO chat_mensajes(id_usuario,rol,texto,creado_en) VALUES(?,?,?,?)", (current["id_usuario"], "asistente", reply, now)) 
            if mood != "sin registrar": db.execute("INSERT INTO estados_animo(id_usuario,estado,origen,creado_en) VALUES(?,?,?,?)", (current["id_usuario"], mood, "chat", now)) 
            if level == "critico": db.execute("INSERT INTO alertas_crisis(id_usuario,nivel,motivo,contacto,creado_en) VALUES(?,?,?,?,?)", (current["id_usuario"], level, risk_message, current["contacto_confianza"], now)) 
        return jsonify(nivel=level, mensaje=risk_message, sugerencias=suggestions, respuestas=replies) 
 
    @api.delete("/chat") 
    def clear_chat(): 
        current, error = auth() 
        if error: return error 
        with get_db() as db: db.execute("DELETE FROM chat_mensajes WHERE id_usuario=?", (current["id_usuario"],)) 
        return jsonify(status="cleared") 
 
    @api.get("/evolucion") 
    def evolution(): 
        current, error = auth() 
        if error: return error 
        with get_db() as db: 
            moods = db.execute("SELECT estado,COUNT(*) AS total FROM estados_animo WHERE id_usuario=? GROUP BY estado ORDER BY total DESC", (current["id_usuario"],)).fetchall() 
            notes = db.execute("SELECT COUNT(*) AS total FROM notas WHERE id_usuario=? AND fecha_hora >= datetime('now','-7 day')", (current["id_usuario"],)).fetchone()["total"] 
        return jsonify(estados=[dict(r) for r in moods], notas_semana=notes) 
 
    @api.get("/biblioteca") 
    def library(): 
        current, error = auth() 
        if error: return error 
        with get_db() as db: rows = db.execute("SELECT id_recurso,titulo,descripcion,tipo,url FROM biblioteca ORDER BY id_recurso DESC").fetchall() 
        return jsonify(items=[dict(r) for r in rows]) 
 
    @api.get("/ayuda") 
    def help_list(): 
        current, error = auth() 
        if error: return error 
        with get_db() as db: rows = db.execute("SELECT id_ayuda,nombre,tipo,telefono,descripcion FROM ayuda_profesional ORDER BY id_ayuda DESC").fetchall() 
        return jsonify(items=[dict(r) for r in rows]) 
 
    @api.get("/admin") 
    def admin_data(): 
        current, error = admin() 
        if error: return error 
        with get_db() as db: 
            resources = db.execute("SELECT * FROM biblioteca ORDER BY id_recurso DESC").fetchall(); contacts = db.execute("SELECT * FROM ayuda_profesional ORDER BY id_ayuda DESC").fetchall() 
        return jsonify(resources=[dict(r) for r in resources], contacts=[dict(r) for r in contacts]) 
 
    @api.put("/admin/biblioteca/") 
    def admin_resource(item_id): 
        current, error = admin() 
        if error: return error 
        data = request.get_json(silent=True) or {} 
        with get_db() as db: db.execute("UPDATE biblioteca SET titulo=?,descripcion=?,tipo=?,url=? WHERE id_recurso=?", (str(data.get("titulo", "")).strip(), str(data.get("descripcion", "")).strip(), str(data.get("tipo", "Recurso")).strip(), str(data.get("url", "")).strip(), item_id)) 
        return jsonify(status="updated") 
 
    @api.put("/admin/ayuda/") 
    def admin_help(item_id): 
        current, error = admin() 
        if error: return error 
        data = request.get_json(silent=True) or {} 
        with get_db() as db: db.execute("UPDATE ayuda_profesional SET nombre=?,tipo=?,telefono=?,descripcion=? WHERE id_ayuda=?", (str(data.get("nombre", "")).strip(), str(data.get("tipo", "Asistencia")).strip(), str(data.get("telefono", "")).strip(), str(data.get("descripcion", "")).strip(), item_id)) 
        return jsonify(status="updated") 
 
    @api.post("/admin/biblioteca") 
    def admin_resource_create(): 
        current, error = admin() 
        if error: return error 
        data = request.get_json(silent=True) or {}; now = datetime.now().isoformat(timespec="seconds") 
        with get_db() as db: cursor = db.execute("INSERT INTO biblioteca(titulo,descripcion,tipo,url,creado_en) VALUES(?,?,?,?,?)", (str(data.get("titulo", "Nuevo recurso")), str(data.get("descripcion", "")), str(data.get("tipo", "Recurso")), str(data.get("url", "https://")), now)) 
        return jsonify(id=cursor.lastrowid), 201 
 
    @api.delete("/admin/biblioteca/") 
    def admin_resource_delete(item_id): 
        current, error = admin() 
        if error: return error 
        with get_db() as db: db.execute("DELETE FROM biblioteca WHERE id_recurso=?", (item_id,)) 
        return jsonify(status="deleted") 
 
    @api.post("/admin/ayuda") 
    def admin_help_create(): 
        current, error = admin() 
        if error: return error 
        data = request.get_json(silent=True) or {}; now = datetime.now().isoformat(timespec="seconds") 
        with get_db() as db: cursor = db.execute("INSERT INTO ayuda_profesional(nombre,tipo,telefono,descripcion,creado_en) VALUES(?,?,?,?,?)", (str(data.get("nombre", "Nuevo contacto")), str(data.get("tipo", "Asistencia")), str(data.get("telefono", "")), str(data.get("descripcion", "")), now)) 
        return jsonify(id=cursor.lastrowid), 201 
 
    @api.delete("/admin/ayuda/") 
    def admin_help_delete(item_id): 
        current, error = admin() 
        if error: return error 
        with get_db() as db: db.execute("DELETE FROM ayuda_profesional WHERE id_ayuda=?", (item_id,)) 
        return jsonify(status="deleted") 
 
    app.register_blueprint(api) 
    return app