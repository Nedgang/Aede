##########
# IMPORT #
##########
from nicegui import ui

from src.frontend.parameters.details_parameters import (
    complementary_freq_details,
    variant_details_label_column,
    variant_frequencies_label_column,
    variant_gnomad_label_column,
)
from src.frontend.table.details_freq_table import details_freq_table


###################
# VARIANT DETAILS #
###################
class Variant_details(ui.card):
    def __init__(self, variant_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("w-23/100 h-105")
        if variant_type == "SNV-Indel":
            # Find back to parameters which info goes to which tab
            self.details_label_column = variant_details_label_column(variant_type)
            self.frequencies_label_column = variant_frequencies_label_column(
                variant_type
            )
            self.gnomAD_label_column = variant_gnomad_label_column(variant_type)
            self.selected_variant_details = {
                col: ""
                for col in list(self.details_label_column.values())
                + list(self.frequencies_label_column.values())
                + list(self.gnomAD_label_column.values())
            }
            # Card header
            with self:
                with ui.row().classes("w-full"):
                    ui.label(f"Details on {variant_type}").classes("text-h5")
                # Create tabs and then populate them
                with ui.tabs().classes("w-full") as tabs:
                    ui.tab("info")
                    ui.tab("freq")
                    ui.tab("gnomad")
                with ui.tab_panels(tabs, value="info").classes("w-full"):
                    with ui.tab_panel("info"), ui.grid(columns=2):
                        for detail in self.details_label_column:
                            ui.label(detail)
                            ui.label().bind_text_from(
                                self.selected_variant_details,
                                self.details_label_column[detail],
                            )
                    with ui.tab_panel("freq"):
                        self.selected_variant_freq_table = details_freq_table(
                            variant_type
                        ).classes("w-full")
                        with ui.grid(columns=2):
                            for freq in complementary_freq_details(variant_type):
                                ui.label(freq)
                                ui.label().bind_text_from(
                                    self.selected_variant_details,
                                    freq,
                                )
                    with ui.tab_panel("gnomad"), ui.grid(columns=2):
                        for detail in self.gnomAD_label_column:
                            ui.label(detail)
                            ui.label().bind_text_from(
                                self.selected_variant_details,
                                self.gnomAD_label_column[detail],
                                backward=lambda b: str(b),
                            )

        else:
            raise TypeError(
                f"{variant_type} not yet supported for variant details card"
            )

    def set_variant_details(self, selected_variant: dict) -> None:
        """
        Allow to update the card with the selected variant informations from the variant
        selector.
        """
        self.selected_variant_details.update(selected_variant)
        self.selected_variant_freq_table.update_rows(
            [
                {
                    key: row[key]
                    if key == "pop"
                    else selected_variant[key]
                    if row["pop"] == "All"
                    else selected_variant[f"{key}_{row['pop']}"]
                    for key in row
                }
                for row in self.selected_variant_freq_table.rows
            ]
        )

    def clear(self) -> None:
        """
        Clear everything.
        """
        self.selected_variant_details.update(
            {
                col: ""
                for col in list(self.details_label_column.values())
                + list(self.frequencies_label_column.values())
                + list(self.gnomAD_label_column.values())
            }
        )
        self.selected_variant_freq_table.update_rows(
            [
                {key: row[key] if key == "pop" else "" for key in row}
                for row in self.selected_variant_freq_table.rows
            ]
        )
