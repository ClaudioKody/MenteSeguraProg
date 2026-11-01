class NotaRepository:
    """Patrón Repository: encapsula las consultas SQL de notas privadas."""
    def __init__(self, db):
        self.db = db


    def listar_por_usuario(self, usuario_id):
        return self.db.execute("SELECT * FROM notas WHERE id_usuario=? ORDER BY fecha_hora DESC", (usuario_id,)).fetchall()


    def crear(self, usuario_id, fecha_hora, titulo, texto, estado_animo):
        cursor = self.db.execute("INSERT INTO notas(id_usuario,fecha_hora,titulo,texto,estado_animo) VALUES(?,?,?,?,?)", (usuario_id, fecha_hora, titulo, texto, estado_animo))
        return cursor.lastrowid


    def actualizar(self, nota_id, usuario_id, titulo, texto, estado_animo):
        self.db.execute("UPDATE notas SET titulo=?, texto=?, estado_animo=? WHERE id_nota=? AND id_usuario=?", (titulo, texto, estado_animo, nota_id, usuario_id))


    def eliminar(self, nota_id, usuario_id):
        self.db.execute("DELETE FROM notas WHERE id_nota=? AND id_usuario=?", (nota_id, usuario_id))
