from nicegui import ui


class Header(ui.header):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("items-center justify-between")
        with self:
            with ui.row():
                ui.image("logo/logo_temporaire.png").classes("w-130")
                self.formulary_button = ui.button(
                    icon="wysiwyg",
                    # on_click=lambda: left_drawer.toggle(),
                ).tooltip("Request formulary")
            ui.switch("Dark mode").bind_value(ui.dark_mode()).props("color=white")
