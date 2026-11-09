##########
# IMPORT #
##########
from nicegui import ui


##########
# HEADER #
##########
class Header(ui.header):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("items-center justify-between")
        with self:
            with ui.row():
                ui.image("logo/logo_temporaire.png").classes("w-130")
                self.search_form_button = ui.button(
                    icon="wysiwyg",
                ).tooltip("Request formulary")
            ui.switch("Dark mode").bind_value(ui.dark_mode()).props("color=white")
