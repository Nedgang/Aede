##########
# IMPORT #
##########
from nicegui import ui

from src.frontend.aggrid.variant_consequences import variant_consequences
from src.frontend.aggrid.variant_selector import variant_selector
from src.frontend.parameters.details_parameters import (
    complementary_freq_details,
    variant_details_label_column,
    variant_frequencies_label_column,
    variant_gnomad_label_column,
)
from src.frontend.table.details_freq_table import details_freq_table


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
        # type. Will generate details for selected variant informations.
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
            # Line with the variant selector aggrid
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
                    col_selector = ui.button(icon="menu")
                # Generate aggrid for variant selection
                self.selector = variant_selector(self.variants).classes("w-full h-9/10")
                # Allowing columns selection
                with col_selector, ui.menu(), ui.column().classes("'gap-0 p-2'"):
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
            # Line with variant details card, and variant consequences card
            with (
                ui.row()
                .classes("w-full")
                .bind_visibility(element_visibility, "variant_details")
            ):
                # Variant details card
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
                                    selected_variant_details,
                                    details_label_column[detail],
                                )
                        with ui.tab_panel("freq"):
                            self.variant_freq_table = details_freq_table(
                                variant_type
                            ).classes("w-full")
                            with ui.grid(columns=2):
                                for freq in complementary_freq_details(variant_type):
                                    ui.label(freq)
                                    ui.label().bind_text_from(
                                        selected_variant_details, freq
                                    )
                        with ui.tab_panel("gnomad"), ui.grid(columns=2):
                            for detail in gnomAD_label_column:
                                ui.label(detail)
                                ui.label().bind_text_from(
                                    selected_variant_details,
                                    gnomAD_label_column[detail],
                                )
                # Variant consequences card
                with ui.card().classes("w-75/100 h-105"):
                    with ui.row():
                        ui.label(f"Transcript details on {variant_type}").classes(
                            "text-h5"
                        )
                        col_csq = ui.button(icon="menu")
                        ui.switch("Variant selection", value=True).bind_value_to(
                            element_visibility, "variant_selection"
                        )
                    self.variant_consequences = variant_consequences(variant_type)
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
                                    )
                                ),
                            )

    def refresh_selector(self):
        """"""
        # self.selector.run_grid_method("autoSizeAllColumns")
        self.selector.run_grid_method("sizeColumnsToFit")
