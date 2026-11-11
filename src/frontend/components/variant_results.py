##########
# IMPORT #
##########
from nicegui import ui

from src.frontend.aggrid.variant_selector import variant_selector


###################
# VARIANT RESULTS #
###################
class Variant_results(ui.row):
    def __init__(self, variant_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("w-full")
        self.element_visibility = {"variant_selection": True, "variant_detail": False}
        self.variants = []
        with self:
            with (
                (
                    ui.row()
                    .classes("w-full")
                    .bind_visibility(self.element_visibility, "variant_selection")
                ),
                ui.card().classes("w-99/100 h-105"),
            ):
                with ui.row():
                    ui.label(variant_type).classes("text-h5")
                self.selector = variant_selector(self.variants)
            with ui.row():
                pass

    def refresh_selector(self):
        """"""
        self.selector.update()
