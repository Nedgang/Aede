##########
# IMPORT #
##########
import os

import polars as pl
import requests
from nicegui import ui

from src.frontend.components.header import Header
from src.frontend.components.search_form import Search_form


#############
# FUNCTIONS #
#############
def run_variant_search() -> None:
    """
    Send the get request to the API, handle the answer and return a dict with results
    from database search.
    """
    answer = requests.get("http://localhost:8000/query/v1/variants/", params=REQUEST)
    if answer.ok:
        ui.notify("Results received!")
        for variant_type in answer.json():
            if answer.json()[variant_type]["results"] != []:
                GENERAL_STATE[f"result_request_{variant_type}"] = pl.from_dicts(
                    answer.json()[variant_type]["results"], infer_schema_length=None
                )
                GENERAL_STATE[f"result_table_{variant_type}"].options["rowData"].clear()
                GENERAL_STATE[f"result_table_{variant_type}"].options["rowData"].extend(
                    GENERAL_STATE[f"result_request_{variant_type}"]
                    .select(
                        pl.col(
                            ["variant_key"]
                            + list(
                                GENERAL_STATE[f"details_variant_{variant_type}"].keys()
                            )
                        )
                    )
                    .unique()
                    .sort("pos")
                    .to_dicts()
                )
            else:
                GENERAL_STATE[f"result_request_{variant_type}"] = pl.DataFrame()
                ui.notify(
                    "No variants found using those parameters",
                    type="warning",
                    position="center",
                )
            if answer.json()[variant_type]["warning"]:
                ui.notify(
                    answer.json()[variant_type]["message"],
                    type="warning",
                    position="center",
                )
    else:
        ui.notify(answer.json()["detail"], type="negative", position="center")


def reset_request() -> dict:
    """
    Return basic dict for default request.
    """
    return {
        "variant_type": [all_variants_type[0]],
        "id": "",
        "csq": [],
        "impact": [],
        "feature": [],
        "gene": None,
        "chr": chromosomes[0],
        "start": 0,
        "stop": 0,
        "only_pass": False,
        "gnomad_regions": False,
        "in_gnomad": False,
        "pass_gnomad": False,
    }


async def output_selected_row(variant_type) -> None:
    """
    Update details in display depending on the selected variant in result table.
    """
    selected_row = await GENERAL_STATE[
        f"result_table_{variant_type}"
    ].get_selected_row()
    if selected_row:
        GENERAL_STATE[f"selected_{variant_type}_variant"] = True
        GENERAL_STATE[f"details_variant_{variant_type}"] = selected_row
        GENERAL_STATE[f"details_table_{variant_type}"].update_rows(
            [
                {
                    key: row[key]
                    if key == "pop"
                    else selected_row[key]
                    if row["pop"] == "All"
                    else selected_row[f"{key}_{row['pop']}"]
                    for key in row
                }
                for row in GENERAL_STATE[f"details_table_{variant_type}"].rows
            ]
        )
        GENERAL_STATE[f"csq_table_{variant_type}"].options["rowData"].clear()
        GENERAL_STATE[f"csq_table_{variant_type}"].options["rowData"].extend(
            GENERAL_STATE[f"result_request_{variant_type}"]
            .filter(pl.col("variant_key") == selected_row["variant_key"])
            .to_dicts()
        )
        GENERAL_STATE[f"display_{variant_type}_csq"] = True
    else:
        GENERAL_STATE[f"selected_{variant_type}_variant"] = False
        GENERAL_STATE[f"details_variant_{variant_type}"] = {
            col: ""
            for col in list(details_label_column.values())
            + list(frequencies_label_column.values())
            + list(gnomAD_label_column.values())
        }
        GENERAL_STATE[f"details_table_{variant_type}"].update_rows(
            [
                {key: row[key] if key == "pop" else "" for key in row}
                for row in GENERAL_STATE[f"details_table_{variant_type}"].rows
            ]
        )
        GENERAL_STATE[f"csq_table_{variant_type}"].options["rowData"].clear()
        GENERAL_STATE[f"display_{variant_type}_csq"] = False


def harmonize_chrom_options(
    select_chr,
    request: dict,
    base_chr: list,
    link_feature_chrom: pl.LazyFrame,
    link_id_chrom: pl.LazyFrame,
) -> None:
    if request["id"] == "" and request["feature"] == [] and request["gene"] is None:
        select_chr.set_options(base_chr, value=base_chr[0])
    else:
        if request["id"] != "":
            select_chr.set_options(
                link_id_chrom.filter(pl.col("id") == request["id"])
                .collect()["chrom"]
                .to_list(),
                value=select_chr.options[0],
            )
        elif request["feature"] != []:
            select_chr.set_options(
                link_feature_chrom.filter(
                    pl.col("csq_Feature").is_in(request["feature"])
                )
                .collect()["chrom"]
                .to_list(),
                value=select_chr.options[0],
            )
        else:
            select_chr.set_options(
                link_feature_chrom.filter(pl.col("csq_SYMBOL") == request["gene"])
                .collect()["chrom"]
                .to_list(),
                value=select_chr.options[0],
            )


def clear_results(variants: list(str)):
    for variant_type in variants:
        GENERAL_STATE["result_table_" + variant_type].options["rowData"].clear()
        GENERAL_STATE[f"selected_{variant_type}_variant"] = False
        GENERAL_STATE[f"details_variant_{variant_type}"] = {
            col: ""
            for col in list(details_label_column.values())
            + list(frequencies_label_column.values())
            + list(gnomAD_label_column.values())
        }
        GENERAL_STATE[f"details_table_{variant_type}"].update_rows(
            [
                {key: row[key] if key == "pop" else "" for key in row}
                for row in GENERAL_STATE[f"details_table_{variant_type}"].rows
            ]
        )
        GENERAL_STATE[f"csq_table_{variant_type}"].options["rowData"].clear()
        GENERAL_STATE[f"display_{variant_type}_csq"] = False


####################
# GLOBAL VARIABLES #
####################
# Finding options from data structure, which lead to automatic update of the front with
# data upload
all_variants_type = sorted(
    [
        dir.name
        for dir in os.scandir("../Mneme/")
        if dir.is_dir() and "_index.parquet" not in dir.name
    ]
)
with open("../Mneme/chromosomes.txt") as file:
    chromosomes = [chr.strip() for chr in file]
    file.close()
link_feature_chrom = pl.scan_parquet("../Mneme/feature_index.parquet")
link_id_chrom = pl.scan_parquet("../Mneme/id_index.parquet")

REQUEST = reset_request()

details_label_column = {
    "Chromosome": "chrom",
    "Position": "pos",
    "ID": "id",
    "Reference": "ref",
    "Alternative": "alt",
    "Filter": "filter",
    "DP": "DP",
    "Variant type": "variant_type",
}

frequencies_label_column = {
    "AC": "AC",
    "AN": "AN",
    "AF": "AF",
    "AC_Hom": "AC_Hom",
    "AC_XX": "AC_XX",
    "AN_XX": "AN_XX",
    "AF_XX": "AF_XX",
    "AC_XY": "AC_XY",
    "AN_XY": "AN_XY",
    "AF_XY": "AF_XY",
    "grpmax": "grpmax",
    "AC_grpmax": "AC_grpmax",
    "AN_grpmax": "AN_grpmax",
    "AF_grpmax": "AF_grpmax",
}

gnomAD_label_column = {
    "Present in gnomAD": "inGnomad",
    "Pass gnomAD QC": "passGnomad",
    "Not covered by gnomAD": "notCoveredByGnomad",
}

GENERAL_STATE = {
    variant_type: variant_type in REQUEST["variant_type"]
    for variant_type in all_variants_type
}
for variant_type in all_variants_type:
    GENERAL_STATE.setdefault("result_table_" + variant_type, None)
    GENERAL_STATE.setdefault("result_request_" + variant_type, None)
    GENERAL_STATE.setdefault("csq_table_" + variant_type, None)
    GENERAL_STATE.setdefault(
        "details_variant_" + variant_type,
        {
            col: ""
            for col in list(details_label_column.values())
            + list(frequencies_label_column.values())
            + list(gnomAD_label_column.values())
        },
    )
    GENERAL_STATE.setdefault(f"display_{variant_type}_variants", True)
    GENERAL_STATE.setdefault(f"display_{variant_type}_csq", False)
    GENERAL_STATE.setdefault(f"selected_{variant_type}_variant", False)


########
# MAIN #
########
@ui.page("/")
def search_page():
    with open("../Mneme/Impact.txt", "r") as file:
        impact_list = [impact.strip() for impact in file]
    with open("../Mneme/consequences.txt", "r") as file:
        csq_list = [csq.strip() for csq in file]
    # Initialize header and search form
    header = Header(elevated=True)
    search_form = Search_form(
        variants_type=all_variants_type,
        chromosomes_list=chromosomes,
        impact_list=impact_list,
        consequence_list=csq_list,
        lf_feature_chrom_symbol=link_feature_chrom,
        lf_id_chrom=link_id_chrom,
        bordered=True,
        elevated=True,
    )
    # Link search form toggle to the button in the header
    header.search_form_button.on_click(lambda: search_form.toggle())

    # Link value from widgets to the REQUEST formulary
    search_form.variant_type.bind_value(REQUEST, "variant_type")
    search_form.gene.bind_value(REQUEST, "gene")
    search_form.variant_id.bind_value(REQUEST, "id")
    search_form.features.bind_value(REQUEST, "feature")
    search_form.impact.bind_value(REQUEST, "impact")
    search_form.consequences.bind_value(REQUEST, "csq")
    search_form.chrom.bind_value(REQUEST, "chr")
    search_form.start.bind_value(REQUEST, "start")
    search_form.stop.bind_value(REQUEST, "stop")
    search_form.only_pass.bind_value(REQUEST, "only_pass")
    search_form.gnomad_regions.bind_value(REQUEST, "gnomad_regions")
    search_form.in_gnomad.bind_value(REQUEST, "in_gnomad")
    search_form.pass_gnomad.bind_value(REQUEST, "pass_gnomad")

    # Link an effect to search form buttons
    search_form.clear.on_click(
        lambda: (REQUEST.update(reset_request()), clear_results(all_variants_type))
    )
    search_form.search.on_click(
        lambda: (
            ui.notify("Request sent to the API"),
            clear_results(all_variants_type),
            run_variant_search(),
        )
    )

    # Check if variant id exist in those chr options, and alter chromosome choice if ok
    search_form.variant_id.validation = {
        "Not in DB": lambda v: (
            not link_id_chrom.filter(pl.col("chrom").is_in(search_form.chrom.options))
            .filter(pl.col("id") == v)
            .collect()
            .is_empty()
            or v == ""
        )
    }
    (
        search_form.variant_id.on(
            "blur",
            lambda variant_id=search_form.variant_id, chromosomes=chromosomes: (
                (
                    search_form.chrom.set_options(
                        [
                            link_id_chrom.filter(
                                pl.col("id") == variant_id.value
                            ).collect()["chrom"][0]
                        ]
                    ).set_value(search_form.chrom.options[0])
                    if variant_id.value != ""
                    else harmonize_chrom_options(
                        search_form.chrom,
                        REQUEST,
                        chromosomes,
                        link_feature_chrom,
                        link_id_chrom,
                    ),
                    search_form.features.set_options(
                        link_feature_chrom.filter(
                            pl.col("chrom").is_in(search_form.chrom.options)
                        )
                        .collect()["csq_Feature"]
                        .unique()
                        .sort()
                        .to_list()
                    ),
                    search_form.gene.set_options(
                        link_feature_chrom.filter(
                            pl.col("chrom").is_in(search_form.chrom.options)
                        )
                        .collect()["csq_SYMBOL"]
                        .unique()
                        .sort()
                        .to_list()
                    ),
                )
                if not variant_id.error
                else (
                    ui.notify(
                        f"""{variant_id.value} not in POPGEN database for the request
                        available chromosomes.""",
                        type="warning",
                        position="center",
                    ),
                    variant_id.set_value(""),
                ),
            ),
        ),
    )

    # Checking link between id/gene/feature on chromosome options, and other widgets
    # options

    # with left_drawer, ui.column().classes("w-full"):
    #     with ui.row():
    # # WIDGETS INTERACTIONS
    # Check if variant id exist in those chr options, and alter chromosome choice if winning
    # # Impact of selecting gene on chromosomes choice, and features options
    # select_gene.on_value_change(
    #     lambda g, base_chr=chromosomes: (
    #         (
    #             (
    #                 select_chr.set_options(
    #                     sorted(
    #                         link_feature_chrom.filter(pl.col("csq_SYMBOL") == g.value)
    #                         .collect()["chrom"]
    #                         .unique()
    #                         .to_list(),
    #                         key=lambda c: int(c.split("chr")[-1]),
    #                     ),
    #                 ),
    #                 select_chr.set_value(select_chr.options[0]),
    #                 ui.notify(
    #                     "Multiple chr possible for this selected gene, please select one",
    #                     type="warning",
    #                     position="center",
    #                 )
    #                 if len(select_chr.options) > 1
    #                 else None,
    #             )
    #             if g.value is not None
    #             and REQUEST["id"] == ""
    #             and REQUEST["feature"] == []
    #             else harmonize_chrom_options(
    #                 select_chr, REQUEST, base_chr, link_feature_chrom, link_id_chrom
    #             )
    #         ),
    #         select_features.set_options(
    #             link_feature_chrom.filter(pl.col("chrom").is_in(select_chr.options))
    #             .collect()["csq_Feature"]
    #             .unique()
    #             .sort()
    #             .to_list()
    #         ),
    #         select_gene.set_options(
    #             link_feature_chrom.filter(pl.col("chrom").is_in(select_chr.options))
    #             .collect()["csq_SYMBOL"]
    #             .unique()
    #             .sort()
    #             .to_list()
    #         ),
    #     )
    # )
    # # Impact of selecting gene on chromosomes choice, and genes options
    # select_features.on_value_change(
    #     lambda f, base_chr=chromosomes, request=REQUEST: (
    #         (
    #             (
    #                 select_chr.set_options(
    #                     sorted(
    #                         link_feature_chrom.filter(
    #                             pl.col("csq_Feature").is_in(f.value)
    #                         )
    #                         .collect()["chrom"]
    #                         .unique()
    #                         .to_list(),
    #                         key=lambda c: int(c.split("chr")[-1]),
    #                     ),
    #                 ),
    #                 select_chr.set_value(select_chr.options[0]),
    #             )
    #             if f.value != []
    #             else harmonize_chrom_options(
    #                 select_chr, request, base_chr, link_feature_chrom, link_id_chrom
    #             )
    #         ),
    #         select_features.set_options(
    #             link_feature_chrom.filter(pl.col("chrom").is_in(select_chr.options))
    #             .collect()["csq_Feature"]
    #             .unique()
    #             .sort()
    #             .to_list()
    #         ),
    #         select_gene.set_options(
    #             link_feature_chrom.filter(pl.col("chrom").is_in(select_chr.options))
    #             .collect()["csq_SYMBOL"]
    #             .unique()
    #             .sort()
    #             .to_list()
    #         ),
    #     )
    # )

    for variant_type in all_variants_type:
        # Variants result row
        with ui.row().classes("w-full").bind_visibility(GENERAL_STATE, variant_type):
            with (
                (
                    ui.row()
                    .classes("w-full")
                    .bind_visibility(GENERAL_STATE, f"display_{variant_type}_variants")
                ),
                ui.card().classes("w-99/100 h-105"),
            ):
                with ui.row():
                    ui.label(variant_type).classes("text-h5")
                    col_select = ui.button(icon="menu")
                GENERAL_STATE[f"result_table_{variant_type}"] = (
                    ui.aggrid(
                        {
                            "columnDefs": [
                                {"headerName": "CHROM", "field": "chrom"},
                                {
                                    "headerName": "POS",
                                    "field": "pos",
                                    "filter": "agNumberColumnFilter",
                                },
                                {
                                    "headerName": "ID",
                                    "field": "id",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "REF",
                                    "field": "ref",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "ALT",
                                    "field": "alt",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "FILTER",
                                    "field": "filter",
                                    "filter": "agTextColumnFilter",
                                },
                                {"field": "AC", "filter": "agNumberColumnFilter"},
                                {"field": "AN", "filter": "agNumberColumnFilter"},
                                {"field": "AF", "filter": "agNumberColumnFilter"},
                                {
                                    "field": "AC_Hom",
                                    "filter": "agNumberColumnFilter",
                                },
                                {"field": "inGnomad"},
                                {"field": "passGnomad"},
                                {
                                    "field": "variant_type",
                                    "filter": "agTextColumnFilter",
                                },
                            ],
                            "rowData": [],
                            "rowSelection": {"mode": "singleRow"},
                        },
                        theme="balham",
                        auto_size_columns=True,
                    )
                    .on(
                        "rowSelected",
                        lambda _, variant_type=variant_type: output_selected_row(
                            variant_type
                        ),
                    )
                    .classes("w-full h-9/10")
                )
                # Allowing columns selection
                with col_select, ui.menu(), ui.column().classes("'gap-0 p-2'"):
                    for column in [
                        i
                        for i in GENERAL_STATE[f"result_table_{variant_type}"].options[
                            "columnDefs"
                        ]
                    ]:
                        colname = (
                            column["field"]
                            if "headerName" not in column
                            else column["headerName"]
                        )
                        ui.switch(
                            colname,
                            value=True,
                            on_change=lambda e, variant_type=variant_type, column=column: (
                                GENERAL_STATE[
                                    f"result_table_{variant_type}"
                                ].run_grid_method(
                                    "setColumnsVisible",
                                    [column["field"]],
                                    e.value,
                                )
                            ),
                        )
            # CSQ result row
            with (
                ui.row()
                .classes("w-full")
                .bind_visibility_from(GENERAL_STATE, f"display_{variant_type}_csq"),
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
                                    GENERAL_STATE,
                                    f"details_variant_{variant_type}",
                                    backward=lambda a, detail=detail: (
                                        f"{a[details_label_column[detail]]}"
                                    ),
                                )
                        with ui.tab_panel("freq"):
                            GENERAL_STATE[f"details_table_{variant_type}"] = ui.table(
                                columns=[
                                    {
                                        "field": "pop",
                                        "align": "center",
                                    },
                                    {
                                        "label": "AC",
                                        "field": "AC",
                                        "align": "center",
                                        "sortable": True,
                                    },
                                    {
                                        "label": "AN",
                                        "field": "AN",
                                        "align": "center",
                                        "sortable": True,
                                    },
                                    {
                                        "label": "AF",
                                        "field": "AF",
                                        "align": "center",
                                        "sortable": True,
                                    },
                                ],
                                rows=[
                                    {"pop": "All", "AC": "", "AN": "", "AF": ""},
                                    {"pop": "XY", "AC": "", "AN": "", "AF": ""},
                                    {"pop": "XX", "AC": "", "AN": "", "AF": ""},
                                    {"pop": "grpmax", "AC": "", "AN": "", "AF": ""},
                                ],
                            ).classes("w-full")
                            with ui.grid(columns=2):
                                for freq in ["AC_Hom", "grpmax"]:
                                    ui.label(freq)
                                    ui.label().bind_text_from(
                                        GENERAL_STATE,
                                        f"details_variant_{variant_type}",
                                        backward=lambda a, freq=freq: (
                                            f"{a[frequencies_label_column[freq]]}"
                                        ),
                                    )
                        with ui.tab_panel("gnomad"), ui.grid(columns=2):
                            for detail in gnomAD_label_column:
                                ui.label(detail)
                                ui.label().bind_text_from(
                                    GENERAL_STATE,
                                    f"details_variant_{variant_type}",
                                    backward=lambda a, detail=detail: (
                                        f"{a[gnomAD_label_column[detail]]}"
                                    ),
                                )
                with ui.card().classes("w-75/100 h-105"):
                    with ui.row():
                        ui.label(f"Transcript details on {variant_type}").classes(
                            "text-h5"
                        )
                        col_select = ui.button(icon="menu")
                        ui.switch("Variant selection", value=True).bind_value_to(
                            GENERAL_STATE, f"display_{variant_type}_variants"
                        )
                    GENERAL_STATE[f"csq_table_{variant_type}"] = ui.aggrid(
                        {
                            "columnDefs": [
                                {
                                    "headerName": "Consequence",
                                    "field": "csq_Consequence",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Impact",
                                    "field": "csq_IMPACT",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Symbol",
                                    "field": "csq_SYMBOL",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Gene",
                                    "field": "csq_Gene",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Feature_type",
                                    "field": "csq_Feature_type",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Feature",
                                    "field": "csq_Feature",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Biotype",
                                    "field": "csq_BIOTYPE",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Exon",
                                    "field": "csq_EXON",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Intron",
                                    "field": "csq_INTRON",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "CDS position",
                                    "field": "csq_CDS_position",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Amino acids",
                                    "field": "csq_Amino_acids",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "headerName": "Codons",
                                    "field": "csq_Codons",
                                    "filter": "agTextColumnFilter",
                                },
                            ],
                            "rowData": [],
                            "rowSelection": {"mode": "None"},
                        },
                        theme="balham",
                        auto_size_columns=True,
                    ).classes("w-full h-9/10")
                    # Allowing columns selection
                    with col_select, ui.menu(), ui.column().classes("'gap-0 p-2'"):
                        for column in [
                            i
                            for i in GENERAL_STATE[f"csq_table_{variant_type}"].options[
                                "columnDefs"
                            ]
                        ]:
                            colname = (
                                column["field"]
                                if "headerName" not in column
                                else column["headerName"]
                            )
                            ui.switch(
                                colname,
                                value=True,
                                on_change=lambda e, variant_type=variant_type, column=column: (
                                    GENERAL_STATE[
                                        f"csq_table_{variant_type}"
                                    ].run_grid_method(
                                        "setColumnsVisible",
                                        [column["field"]],
                                        e.value,
                                    )
                                ),
                            )

    with ui.footer(elevated=True, fixed=False):
        ui.label("Ceci est le bas de la page pour rajouter pleeeeeeins de trucs!")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
