##########
# IMPORT #
##########
import polars as pl
import requests
from nicegui import ui

from src.frontend.cards.variant_consequences_card import Variant_consequences
from src.frontend.cards.variant_details_card import Variant_details
from src.frontend.cards.variant_selector_card import Variant_selector
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
        self.variant_type = variant_type
        # By default, there is no results yet, so it's an empty DataFrame
        self.request_results = pl.DataFrame()
        # Separate visibility status for variant selection and selected variant display
        self.element_visibility = {"variant_selection": True, "variant_details": False}
        with self:
            # Line with the variant selector aggrid
            with (
                ui.row()
                .classes("w-full")
                .bind_visibility(self.element_visibility, "variant_selection"),
            ):
                self.selector_card = Variant_selector(variant_type)
                self.selector_card.selector.on(
                    "rowSelected", lambda: self.display_selected_row()
                )

            # Line with variant details card, and variant consequences card
            with (
                ui.row()
                .classes("w-full")
                .bind_visibility(self.element_visibility, "variant_details")
            ):
                # Variant details card
                self.variant_detail_card = Variant_details(variant_type)
                # Variant consequences card
                self.variant_consequences_card = Variant_consequences(variant_type)
                self.variant_consequences_card.selector_switch.bind_value_to(
                    self.element_visibility, "variant_selection"
                )
        # To have cleaner initial aggrid
        self.size_aggrid_columns()

    def set_request_results(self, search_results: list(dict)) -> None:
        """
        Take results from API call and set it in DataFrame format in self.request_results
        before setting them to the variant selector card.
        """
        if search_results != []:
            self.request_results = pl.from_dicts(
                search_results, infer_schema_length=None
            )
            self.selector_card.update_selector(
                self.request_results.select(
                    pl.col(
                        ["variant_key"]
                        + [
                            col
                            for col in list(
                                variant_details_label_column(self.variant_type).values()
                            )
                            + list(
                                variant_frequencies_label_column(
                                    self.variant_type
                                ).values()
                            )
                            + list(
                                variant_gnomad_label_column(self.variant_type).values()
                            )
                        ]
                    )
                )
                .unique()
                .sort("pos")
                .to_dicts()
            )
        else:
            self.request_results = pl.DataFrame()
            self.selector_card.selector.options["rowData"].clear()

    async def display_selected_row(self) -> None:
        """
        Used to get information on selector aggrid and display details information in the
        variant details card and consequence aggrid.
        """
        selected_row = await self.selector_card.selector.get_selected_row()
        if selected_row:
            self.element_visibility["variant_details"] = True
            self.variant_detail_card.set_variant_details(selected_row)
            self.variant_consequences_card.set_consequences(
                self.get_consequences(selected_row["variant_key"])
            )
        else:
            self.element_visibility["variant_details"] = False

    def get_consequences(self, variant_key: str) -> list(dict):
        """
        Send a get request to the API to obtain list of consequences for a variant_key.
        """
        answer = requests.get(
            "http://localhost:8000/query/v1/consequences/",
            params={
                "variant_type": self.variant_type,
                "variant_key": variant_key,
            },
        )
        if answer.ok:
            answer = answer.json()
            if answer["warning"]:
                ui.notify(
                    answer["message"],
                    type="warning",
                    position="center",
                )
            return answer["results"]
        else:
            ui.notify(answer["detail"], type="negative", position="center")

    def size_aggrid_columns(self) -> None:
        """
        Size aggrid columns to fit the available space.
        """
        self.selector_card.selector.run_grid_method("sizeColumnsToFit")
        self.variant_consequences_card.variant_consequences.run_grid_method(
            "sizeColumnsToFit"
        )

    def clear_display(self) -> None:
        """
        Reinitialize variant_results.
        """
        self.set_request_results([])
        self.element_visibility["variant_details"] = False
        self.selector_card.clear()
        self.variant_detail_card.clear()
        self.variant_consequences_card.clear()
