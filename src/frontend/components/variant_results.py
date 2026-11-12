##########
# IMPORT #
##########
from nicegui import ui

from src.frontend.aggrid.variant_selector import variant_selector
from src.frontend.parameters.details_parameters import (
    variant_details_label_column,
    variant_frequencies_label_column,
    variant_gnomad_label_column,
)


###################
# VARIANT RESULTS #
###################
class Variant_results(ui.row):
    def __init__(self, variant_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("w-full")
        self.variants = []
        element_visibility = {"variant_selection": True, "variant_details": True}
        # Get details information (label + column) from parameters depending on variant
        # type.
        details_label_column = variant_details_label_column(variant_type)
        frequencies_label_column = variant_frequencies_label_column(variant_type)
        gnomAD_label_column = variant_gnomad_label_column(variant_type)
        selected_variant_details = {
            col: ""
            for col in list(details_label_column.values())
            + list(frequencies_label_column.values())
            + list(gnomAD_label_column.values())
        }
        with self:
            with (
                (
                    ui.row()
                    .classes("w-full")
                    .bind_visibility(element_visibility, "variant_selection")
                ),
                ui.card().classes("w-99/100 h-105"),
            ):
                with ui.row():
                    ui.label(variant_type).classes("text-h5")
                    col_selection = ui.button(icon="menu")
                self.selector = variant_selector(self.variants)
                # Allowing columns selection
                with col_selection, ui.menu(), ui.column().classes("'gap-0 p-2'"):
                    for column in self.selector.options["columnDefs"]:
                        ui.switch(
                            column["headerName"],
                            value=True,
                            on_change=lambda switch, column=column: (
                                self.selector.run_grid_method(
                                    "setColumnsVisible", [column["field"]], switch.value
                                )
                            ),
                        )
            with (
                ui.row()
                .classes("w-full")
                .bind_visibility(element_visibility, "variant_details")
            ):
                with ui.card().classes("w-23/100 h-105"):
                    with ui.row().classes("w-full"):
                        ui.label(f"Details on {variant_type}").classes("text-h5")
                    with ui.tabs().classes("w-full") as tabs:
                        ui.tab("info")
                        ui.tab("freq")
                        ui.tab("gnomad")
                    with ui.tab_panels(tabs, value="info").classes("w-full"):
                        with ui.tab_panel("info"), ui.grid(columns=2):
                            for detail in details_label_column:
                                ui.label(detail)
                                ui.label().bind_text_from(
                                    selected_variant_details, detail
                                )

                with ui.card().classes("w-75/100 h-105"):
                    with ui.row():
                        ui.label(f"Transcript details on {variant_type}").classes(
                            "text-h5"
                        )
                        col_select = ui.button(icon="menu")
                        ui.switch("Variant selection", value=True).bind_value_to(
                            element_visibility, "variant_selection"
                        )
                    ui.label("aggrid here")

    def refresh_selector(self):
        """"""
        # self.selector.run_grid_method("autoSizeAllColumns")
        self.selector.run_grid_method("sizeColumnsToFit")
