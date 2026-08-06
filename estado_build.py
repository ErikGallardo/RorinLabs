class EstadoBuild:

    def __init__(self):
        self.nombre_agente = "Ninguno"
        self.nombre_wengine = "Ninguno"
        self.refinamiento = 1
        self.stacks = 0
        self.set_stacks = 0
        self.mindscape = 0
        self.mindscape_stacks = 0
        self.mindscape_cond = ""
        self.core_activo = False
        self.core_stacks = 0
        self.set_condicion = False
        self.nombre_habilidad = None

        self.sets = {
            'set1': "Ninguno",
            'set2': "Ninguno",
            'set3': "Ninguno"
        }
        self.discos = {
            4: "Ninguno",
            5: "Ninguno",
            6: "Ninguno"
        }

        self.discos_detalles = {
            i: {
                "set": "Ninguno", 
                "main": "Vida Plana" if i == 1 else "Ataque Plano" if i == 2 else "Defensa Plana" if i == 3 else "Ninguno",
                "subs": {
                    1: {"stat": "Ninguno", "rolls": 0},
                    2: {"stat": "Ninguno", "rolls": 0},
                    3: {"stat": "Ninguno", "rolls": 0},
                    4: {"stat": "Ninguno", "rolls": 0}
                }
            } for i in range(1, 7)
        }

        self.substats_counts = {}
        self.base_stats = {}
        self.bonos_manuales_planos = {}

    def reiniciar(self):
        """
        Restaura el estado a sus valores por defecto, como si se reiniciara la app.
        """
        self.nombre_agente = "Ninguno"
        self.nombre_wengine = "Ninguno"
        self.refinamiento = 1
        self.stacks = 0
        self.set_stacks = 0
        self.mindscape = 0
        self.mindscape_stacks = 0
        self.mindscape_cond = ""
        self.core_activo = False
        self.core_stacks = 0
        self.set_condicion = False
        self.nombre_habilidad = None
        self.sets = {'set1': "Ninguno", 'set2': "Ninguno", 'set3': "Ninguno"}
        self.discos = {4: "Ninguno", 5: "Ninguno", 6: "Ninguno"}
        
        for i in range(1, 7):
            self.discos_detalles[i]["set"] = "Ninguno"
            self.discos_detalles[i]["main"] = "Vida Plana" if i == 1 else "Ataque Plano" if i == 2 else "Defensa Plana" if i == 3 else "Ninguno"
            for j in range(1, 5):
                self.discos_detalles[i]["subs"][j]["stat"] = "Ninguno"
                self.discos_detalles[i]["subs"][j]["rolls"] = 0

        self.substats_counts.clear()
        self.bonos_manuales_planos.clear()
        self.base_stats = {}

    def __str__(self):
        """Representación en texto para depuración."""
        return (
            f"Agente: {self.nombre_agente}, W-Engine: {self.nombre_wengine}\n"
            f"Sets: {self.sets}\n"
            f"Discos: {self.discos}\n"
            f"Bonos Manuales: {self.bonos_manuales_planos}"
        )