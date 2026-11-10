##########
# IMPORT #
##########
from nicegui import ui


##########
# HEADER #
##########
class Footer(ui.footer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with self:
            ui.label("Ceci est le bas de la page pour rajouter pleeeeeeins de trucs!")
