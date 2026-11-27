##########
# IMPORT #
##########
from nicegui import ui

from src.frontend.aggrid.variant_selector import variant_selector


####################
# VARIANT SELECTOR #
####################
class Variant_selector(ui.card):
    def __init__(self, variant_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if variant_type == "SNV-Indel":
            self.classes("w-99/100 h-105")
            with self:
                with ui.row().classes("items-center"):
                    ui.label(variant_type).classes("text-h5")
                    col_selector = ui.button(icon="menu")
                    self.variants_number = ui.label("No variants searched yet")
                # Generate aggrid for variant selection
                self.selector = variant_selector(variant_type).classes("w-full h-9/10")
                # Keep track of selected columns
                self.selector_columns = {
                    column["field"]: True
                    for column in self.selector.options["columnDefs"]
                }
                # Allowing columns selection
                with col_selector, ui.menu(), ui.column().classes("'gap-0 p-2'"):
                    for column in self.selector.options["columnDefs"]:
                        ui.switch(
                            column["headerName"],
                            on_change=lambda switch, column=column: (
                                self.selector.run_grid_method(
                                    "setColumnsVisible", [column["field"]], switch.value
                                ),
                                self.selector.run_grid_method("sizeColumnsToFit"),
                            ),
                        ).bind_value(self.selector_columns, column["field"])
        else:
            raise TypeError(
                f"{variant_type} not yet supported for variant selector card"
            )

    def update_selector(self, rows: list(dict)) -> None:
        """
        Update selector aggrid with variants request results.
        """
        self.clear()
        if len(rows) > 0:
            self.selector.options["rowData"].extend(rows)
            for key in self.selector_columns:
                self.selector.run_grid_method(
                    "setColumnsVisible", [key], self.selector_columns[key]
                )
            self.variants_number.set_text(f"{len(rows)} variants found")
        self.selector.run_grid_method("sizeColumnsToFit")

    def clear(self) -> None:
        """
        Clean the card.
        """
        self.selector.options["rowData"].clear()
        self.variants_number.set_text("No variants searched yet")
