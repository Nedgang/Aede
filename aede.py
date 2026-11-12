##########
# IMPORT #
##########
import os

import polars as pl
import requests
from nicegui import ui

from src.frontend.components.footer import Footer
from src.frontend.components.header import Header
from src.frontend.components.search_form import Search_form
from src.frontend.components.variant_results import Variant_results


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
    """
    Main research page.
    """
    # Dict to follow and tranfer information from one component to another
    variant_type_visibility = {
        variant_type: variant_type in REQUEST["variant_type"]
        for variant_type in all_variants_type
    }
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
    # Link value from widgets to the REQUEST formulary
    # Link variant type selection to general state value for results visibility
    search_form.variant_type.bind_value(REQUEST, "variant_type").on_value_change(
        lambda: variant_type_visibility.update(
            {var: var in search_form.variant_type.value for var in all_variants_type}
        ),
    )
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

    variant_type_results = {
        variant_type: Variant_results(variant_type).bind_visibility(
            variant_type_visibility, variant_type
        )
        for variant_type in all_variants_type
    }

    # Link search form toggle to the button in the header
    header.search_form_button.on_click(
        lambda: (
            search_form.toggle(),
            variant_type_results["SNV-Indel"].refresh_selector(),
        )
    )
    Footer(elevated=True, fixed=False)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
