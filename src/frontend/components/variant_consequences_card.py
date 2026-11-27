##########
# IMPORT #
##########
from nicegui import ui

from src.frontend.aggrid.variant_consequences import variant_consequences


########################
# VARIANT CONSEQUENCES #
########################
class Variant_consequences(ui.card):
    def __init__(self, variant_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if variant_type == "SNV-Indel":
            self.classes("w-75/100 h-105")
            # Card header
            with self:
                with ui.row().classes("items-center"):
                    ui.label(f"Transcript details on {variant_type}").classes("text-h5")
                    col_csq = ui.button(icon="menu")
                    self.consequences_number = ui.label("")
                    self.selector_switch = ui.switch("Variant selection", value=True)
                self.variant_consequences = variant_consequences(variant_type)
                # Keep track of selected columns
                self.consequences_columns = {
                    column["field"]: True
                    for column in self.variant_consequences.options["columnDefs"]
                }
                # Allowing columns selection
                with col_csq, ui.menu(), ui.column().classes("'gap-0 p-2'"):
                    for column in self.variant_consequences.options["columnDefs"]:
                        ui.switch(
                            column["headerName"],
                            value=True,
                            on_change=lambda switch, column=column: (
                                self.variant_consequences.run_grid_method(
                                    "setColumnsVisible",
                                    [column["field"]],
                                    switch.value,
                                ),
                                self.variant_consequences.run_grid_method(
                                    "sizeColumnsToFit"
                                ),
                            ),
                        ).bind_value(self.consequences_columns, column["field"])
        else:
            raise TypeError(
                f"{variant_type} not yet supported for variant consequences card"
            )

    def set_consequences(self, consequences: list(dict)) -> None:
        """
        Allow to update consequences with data requested from the database with the
        variant selected in the variants selector.
        """
        self.variant_consequences.options["rowData"].clear()
        self.variant_consequences.options["rowData"].extend(consequences)
        for key in self.consequences_columns:
            self.variant_consequences.run_grid_method(
                "setColumnsVisible", [key], self.consequences_columns[key]
            )
        self.consequences_number.set_text(
            f"""{len(self.variant_consequences.options["rowData"])} consequences found on
            this variant"""
        )
        self.variant_consequences.run_grid_method("sizeColumnsToFit")

    def clear(self) -> None:
        """
        Clear everything.
        """
        self.variant_consequences.options["rowData"].clear()
        self.consequences_number.set_text("")
