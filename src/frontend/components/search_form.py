##########
# IMPORT #
##########
from nicegui import ui


##########
# HEADER #
##########
class Search_form(ui.left_drawer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Widgets creation
        with self, ui.column().classes("w-full"):
            ui.label("Request").classes("text-h5")
            # Variant type selection
            self.variant_type = ui.select(
                options=[],
                label="Variant type",
                multiple=True,
                validation=lambda value: (
                    "Must select at least one variant type" if value == [] else None
                ),
            ).classes("w-full")
            # Gene search
            self.gene = (
                ui.select(
                    label="Gene symbol", options=[], with_input=True, clearable=True
                )
                .tooltip(
                    """You can search variant which impact a gene symbol. Choosing one
                    lead to limitation to the chromosome choice.\n
                    Options will be limited to the possible chromosomes choice: you won't
                    be able to select a gene on chr13 if you selected another parameter
                    which set chr to only 18."""
                )
                .classes("w-full")
            )
            # ID search
            self.variant_id = (
                ui.input(label="Variant ID")
                .tooltip("""It will be automaticly checked if it is present in the
                         database at the available chromosome, and limit chrom choice if
                         it's the case. Ex: it won't validate a variant on chr21 if other
                         parameters (gene, feature, etc...) limit choice to chr18.""")
                .classes("w-full")
            ).props("debounce=500")
            # csq_Feature
            self.features = (
                ui.select(
                    label="Feature ID",
                    options=[],
                    with_input=True,
                    multiple=True,
                    clearable=True,
                )
                .tooltip("""Ensemble stable ID of Feature, which can be Transcript,
                         Regulatory_Feature, Motif_Feature. Options will be limited to the
                         possible choice of chromosome.
                         Selecting one will also affect the available choice of
                         chromosome.""")
                .classes("w-full")
            )
            # Variant impact
            self.impact = ui.select(
                label="Variant impacts",
                options=[],
                with_input=True,
                multiple=True,
                clearable=True,
            ).classes("w-full")
            # Consequence selection
            self.consequences = ui.select(
                label="Variant consequences",
                options=[],
                with_input=True,
                multiple=True,
                clearable=True,
            ).classes("w-full")
            with ui.row():
                # Chromosome choice
                self.chrom = (
                    ui.select(label="Chromosome", options=[])
                    .tooltip(
                        """Only one at a time, options affected by choice made on gene,
                        variantand feature."""
                    )
                    .classes("w-2/7")
                )
                # Selection start
                self.start = ui.number(label="Start", min=0, precision=0).classes(
                    "w-2/7"
                )
                # Selection stop
                self.stop = ui.number(label="End", min=0, precision=0).classes("w-2/7")
                # Start can't be higher than Stop
                self.start.on(
                    "change",
                    lambda: (
                        self.stop.set_value(self.start.value)
                        if self.stop.value < self.start.value
                        else None
                    ),
                ).on(
                    "blur",
                    lambda: self.start.set_value(0) if self.start is None else None,
                )
                self.stop.on(
                    "change",
                    lambda: (
                        self.start.set_value(self.stop.value)
                        if self.stop.value < self.start.value
                        else None
                    ),
                ).on(
                    "blur",
                    lambda: self.stop.set_value(0) if self.stop is None else None,
                )
            # Quality selection
            self.only_pass = ui.switch("PASS variants only", value=False)
            # gnomAD covered region
            self.gnomad_regions = ui.switch("gnomAD covered regions only", value=False)
            # in_gnomAD
            self.in_gnomad = ui.switch("Variant in gnomAD", value=False)
            # pass_gnomAD
            self.pass_gnomad = ui.switch("Variant pass in gnomAD", value=False)
            # Switches interactions
            self.gnomad_regions.on(
                "click",
                lambda: (
                    self.in_gnomad.set_value(False)
                    and self.pass_gnomad.set_value(False)
                    if not self.gnomad_regions.value
                    else None
                ),
            )
            self.in_gnomad.on(
                "click",
                lambda: (
                    self.pass_gnomad.set_value(False)
                    if not self.in_gnomad.value
                    else self.gnomad_regions.set_value(True)
                ),
            )
            self.pass_gnomad.on(
                "click",
                lambda: (
                    self.in_gnomad.set_value(True)
                    and self.gnomad_regions.set_value(True)
                    if self.pass_gnomad.value
                    else None
                ),
            )
            # Search form reset/search buttons
            ui.separator()
            with ui.row().classes("w-full"):
                self.clear = ui.button("Clear", color="red")
                ui.space()
                self.search = ui.button("Search")
