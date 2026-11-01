class ChatStrategy:
    def responder(self, texto):
        raise NotImplementedError




class RiesgoCriticoStrategy(ChatStrategy):
    def responder(self, texto):
        return "Si existe peligro inmediato, contactá ahora a una persona de confianza y a emergencias. No estás solo/a."




class BienestarStrategy(ChatStrategy):
    def responder(self, texto):
        return "Qué bueno registrar este avance. Podés reconocer qué hiciste hoy que te ayudó y repetirlo cuando lo necesites."




class ExploracionStrategy(ChatStrategy):
    def responder(self, texto):
        return "Podemos ir paso a paso. ¿Qué fue lo más difícil de este momento y qué te ayudaría un poco ahora?"




def seleccionar_estrategia(nivel, estado):
    if nivel == "critico":
        return RiesgoCriticoStrategy()
    if estado in {"motivado/a", "feliz", "tranquilo/a"}:
        return BienestarStrategy()
    return ExploracionStrategy()
