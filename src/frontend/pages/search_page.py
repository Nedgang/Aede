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
def reset_request(all_variants_type: list(str), chromosomes: list(str)) -> dict:
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


def launch_variants_search(
    request: dict, variant_type_results: dict(Variant_results)
) -> None:
    """
    TODO
    """
    answer = requests.get("http://localhost:8000/query/v1/variants/", params=request)
    if answer.ok:
        answer = answer.json()
        for variant_type in answer:
            variant_type_results[variant_type].set_request_results(
                answer[variant_type]["results"]
            )
            variant_type_results[variant_type].update_selector()
        if answer[variant_type]["warning"]:
            ui.notify(
                answer.json()[variant_type]["message"],
                type="warning",
                position="center",
            )
        ui.notify("Results received!")
    else:
        ui.notify(answer.json()["detail"], type="negative", position="center")


###############
# SEARCH PAGE #
###############
@ui.page("/search")
def search_page():
    """
    Main research page.
    """
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
    # Base request
    request = reset_request(all_variants_type, chromosomes)
    # Link between feature, id and gene on chromosomes
    link_feature_chrom = pl.scan_parquet("../Mneme/feature_index.parquet")
    link_id_chrom = pl.scan_parquet("../Mneme/id_index.parquet")
    # Dict to follow and tranfer information from one component to another
    variant_type_visibility = {
        variant_type: variant_type in request["variant_type"]
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
    # Link value from widgets to the request formulary
    # Link variant type selection to general state value for results visibility
    search_form.variant_type.bind_value(request, "variant_type").on_value_change(
        lambda: variant_type_visibility.update(
            {var: var in search_form.variant_type.value for var in all_variants_type}
        ),
    )
    search_form.gene.bind_value(request, "gene")
    search_form.variant_id.bind_value(request, "id")
    search_form.features.bind_value(request, "feature")
    search_form.impact.bind_value(request, "impact")
    search_form.consequences.bind_value(request, "csq")
    search_form.chrom.bind_value(request, "chr")
    search_form.start.bind_value(request, "start")
    search_form.stop.bind_value(request, "stop")
    search_form.only_pass.bind_value(request, "only_pass")
    search_form.gnomad_regions.bind_value(request, "gnomad_regions")
    search_form.in_gnomad.bind_value(request, "in_gnomad")
    search_form.pass_gnomad.bind_value(request, "pass_gnomad")

    variant_type_results = {
        variant_type: Variant_results(variant_type).bind_visibility(
            variant_type_visibility, variant_type
        )
        for variant_type in all_variants_type
    }

    # Link an effect to clear page buttons
    search_form.clear.on_click(
        lambda: (
            search_form.reset_options(),
            request.update(reset_request(all_variants_type, chromosomes)),
            [result.clear_display() for result in list(variant_type_results.values())],
        )
    )
    # Link an effect to search form buttons
    search_form.search.on_click(
        lambda: (
            [result.clear_display() for result in list(variant_type_results.values())],
            ui.notify("Request sent to the API"),
            launch_variants_search(request, variant_type_results),
        )
    )
    # Link search form toggle to the button in the header
    header.search_form_button.on_click(
        lambda: (
            search_form.toggle(),
            variant_type_results["SNV-Indel"].refresh_selector(),
        )
    )
    Footer(elevated=True, fixed=False)
