##########
# IMPORT #
##########
import polars as pl
from nicegui import ui


##########
# HEADER #
##########
class Search_form(ui.left_drawer):
    def __init__(
        self,
        variants_type: list,
        chromosomes_list: list,
        impact_list: list,
        consequence_list: list,
        lf_id_chrom: pl.LazyFrame,
        lf_feature_chrom_symbol: pl.LazyFrame,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.chromosomes_list = chromosomes_list
        self.lf_id_chrom = lf_id_chrom
        self.lf_feature_chrom_symbol = lf_feature_chrom_symbol

        # Widgets creation
        with self, ui.column().classes("w-full"):
            ui.label("Request").classes("text-h5")
            # Variant type selection
            self.variant_type = ui.select(
                options=variants_type,
                label="Variant type",
                multiple=True,
                validation=lambda value: (
                    "Must select at least one variant type" if value == [] else None
                ),
            ).classes("w-full")
            # Gene search
            self.gene = (
                ui.select(
                    label="Gene symbol",
                    options=self.lf_feature_chrom_symbol.select("csq_SYMBOL")
                    .unique()
                    .sort("csq_SYMBOL")
                    .collect()
                    .to_series()
                    .to_list(),
                    with_input=True,
                    clearable=True,
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
                ui.input(
                    label="Variant ID",
                    validation={
                        "Not in DB": lambda v: (
                            not self.lf_id_chrom.filter(
                                pl.col("chrom").is_in(self.chrom.options)
                            )
                            .filter(pl.col("id") == v)
                            .collect()
                            .is_empty()
                            or v == ""
                        )
                    },
                )
                .tooltip("""It will be automaticly checked if it is present in the
                         database at the available chromosome, and limit chrom choice if
                         it's the case. Ex: it won't validate a variant on chr21 if other
                         parameters (gene, feature, etc...) limit choice to chr18.""")
                .classes("w-full")
            ).props("debounce=500")
            self.variant_id.on(
                "blur",
                lambda: (
                    (
                        self.harmonize_chrom_options(),
                        self.harmonize_gene_options(),
                        self.harmonize_features_options(),
                    )
                    if not self.variant_id.error
                    else (
                        ui.notify(
                            f"""{self.variant_id.value} not in POPGEN database for the request
                        available chromosomes.""",
                            type="warning",
                            position="center",
                        ),
                        self.variant_id.set_value(""),
                    ),
                ),
            )
            # csq_Feature
            self.features = (
                ui.select(
                    label="Trancript ID",
                    options=self.lf_feature_chrom_symbol.select("csq_Feature")
                    .unique()
                    .sort("csq_Feature")
                    .collect()
                    .to_series()
                    .to_list(),
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
                options=impact_list,
                with_input=True,
                multiple=True,
                clearable=True,
            ).classes("w-full")
            # Consequence selection
            self.consequences = ui.select(
                label="Variant consequences",
                options=consequence_list,
                with_input=True,
                multiple=True,
                clearable=True,
            ).classes("w-full")
            with ui.row():
                # Chromosome choice
                self.chrom = (
                    ui.select(label="Chromosome", options=self.chromosomes_list)
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

    def harmonize_chrom_options(self) -> None:
        """
        Check gene/id/feature widget and adjust available chromosome options in accordance
        """
        if (
            self.variant_id.value == ""
            and self.gene.value is None
            and self.features.value == []
        ):
            self.chrom.set_options(options=self.chromosomes_list)
        else:
            if self.variant_id.value is not None:
                self.chrom.set_options(
                    self.lf_id_chrom.filter(pl.col("id") == self.variant_id.value)
                    .collect()["chrom"]
                    .to_list(),
                    value=self.chrom.options[0],
                )
                self.chrom.set_value(self.chrom.options[0])
            elif self.features.value is not None:
                self.chrom.set_options(
                    self.lf_feature_chrom_symbol.filter(
                        pl.col("csq_Feature").is_in(self.features.value)
                    )
                    .collect()["chrom"]
                    .to_list(),
                    value=self.chrom.options[0],
                )
            else:
                self.chrom.set_options(
                    self.lf_feature_chrom_symbol.filter(
                        pl.col("csq_SYMBOL") == self.gene.value
                    )
                    .collect()["chrom"]
                    .to_list(),
                    value=self.chrom.options[0],
                )

    def harmonize_gene_options(self) -> None:
        """
        Adapt gene options depending on the available chromosomes
        """
        self.gene.set_options(
            self.lf_feature_chrom_symbol.filter(
                pl.col("chrom").is_in(self.chrom.options)
            )
            .select("csq_SYMBOL")
            .unique()
            .collect()["csq_SYMBOL"]
            .sort()
            .to_list()
        )

    def harmonize_features_options(self) -> None:
        """
        Adapt features options depending on the available chromosomes
        """
        self.features.set_options(
            self.lf_feature_chrom_symbol.filter(
                pl.col("chrom").is_in(self.chrom.options)
            )
            .select("csq_Feature")
            .unique()
            .collect()["csq_Feature"]
            .sort()
            .to_list()
        )
