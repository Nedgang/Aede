##########
# IMPORT #
##########
import glob
import os

import requests
from nicegui import ui

####################
# GLOBAL VARIABLES #
####################
# Finding options from data structure, which lead to automatic update of the front with
# data upload
variants_type = sorted([dir.name for dir in os.scandir("../Mneme/") if dir.is_dir()])
chromosomes = sorted({chr.split("/")[-1] for chr in glob.iglob("../Mneme/*/chr*")})
chromosomes = sorted(
    {auto for auto in chromosomes if auto.split("chr")[-1].isdigit()},
    key=lambda c: int(c.split("chr")[-1]),
) + sorted(
    {gono for gono in chromosomes if not gono.split("chr")[-1].isdigit()},
    key=lambda c: c.split("chr")[-1],
)

REQUEST = {
    "variant_type": [variants_type[0]],
    "csq": [],
    "id": "w5Ux3Tb71F03",
    "gene": "",
    "chr": chromosomes[0],
    "start": 0,
    "stop": 0,
    "only_pass": False,
    "gnomad_regions": False,
    "in_gnomad": False,
    "pass_gnomad": False,
}

GENERAL_STATE = {bdd: bdd in REQUEST["variant_type"] for bdd in variants_type}
for bdd in variants_type:
    GENERAL_STATE.setdefault("result_table_" + bdd, None)
    GENERAL_STATE.setdefault("details_variant_" + bdd, None)
GENERAL_STATE["results"] = None

details_label_column = {
    "Chromosome": "chrom",
    "Position": "pos",
    "ID": "id",
    "Reference": "ref",
    "Alternative": "alt",
    "Filter": "filter",
    "DP": "DP",
    "CSQ": "first_csq_symbol",
}

frequencies_label_column = {
    "AC": "AC",
    "AN": "AN",
    "AF": "AF",
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


#############
# FUNCTIONS #
#############
def run_search() -> None:
    """
    Send the get request to the API, handle the answer and return a dict with results
    from database search.
    """
    ans = requests.get("http://localhost:8000/query", params=REQUEST)
    if ans.status_code == 200:
        for variant in ans.json()[0]:
            GENERAL_STATE["result_table_" + variant].remove_rows(
                GENERAL_STATE["result_table_" + variant].rows
            )
            GENERAL_STATE["result_table_" + variant].add_rows(ans.json()[0][variant])


def reset_request() -> None:
    pass


def is_request_correct(request_form: dict) -> bool:
    return False


########
# MAIN #
########
@ui.page("/")
def search_page():
    ui.dark_mode().enable()
    # PAGE & WIDGETS DESCRIPTION
    with ui.header().classes("items-center"):
        ui.label("POPGEN Online").classes("text-h3")
        ui.input("Request")
        ui.button("Search")

    with ui.row().classes("w-full"):
        with ui.card().classes("w-1/6"):
            ui.label("Request").classes("text-h5")
            # Variant type selection
            ui.select(
                options=(variants_type),
                label="Variant type",
                multiple=True,
                on_change=lambda: GENERAL_STATE.update(
                    {var: var in REQUEST["variant_type"] for var in variants_type},
                ),
            ).bind_value(REQUEST, "variant_type").classes("w-full")

            # Consequence selection
            ui.select(
                options=(["missense_variant", "nosens", "synonyme"]),
                label="Variant consequence",
                multiple=True,
            ).bind_value(REQUEST, "csq").classes("w-full")
            # ID search
            ui.input(label="Variant ID").bind_value(REQUEST, "id")
            # Gene search
            # Or input chips + split?
            ui.input(label="Gene").bind_value(REQUEST, "gene")
            # Chromosome choice
            ui.select(
                options=chromosomes,
                label="Chromosome",
            ).bind_value(REQUEST, "chr").classes("w-full")
            # Selection start
            start_value = ui.number(
                label="Start", min=0, value=REQUEST["start"], precision=0
            ).bind_value(REQUEST, "start")
            # Selection stop
            stop_value = ui.number(
                label="End", min=0, value=REQUEST["stop"], precision=0
            ).bind_value(REQUEST, "stop")
            # Quality selection
            ui.switch("PASS variants only", value=REQUEST["only_pass"]).bind_value_to(
                REQUEST, "only_pass"
            )
            # gnomAD covered region
            gnomad_region_switch = ui.switch(
                "gnomAD covered regions only",
                value=REQUEST["gnomad_regions"],
            ).bind_value(REQUEST, "gnomad_regions")
            # in_gnomAD
            in_gnomad_switch = ui.switch(
                "Variant in gnomAD",
                value=REQUEST["in_gnomad"],
            ).bind_value(REQUEST, "in_gnomad")
            # pass_gnomAD
            pass_gnomad_switch = ui.switch(
                "Variant pass in gnomAD",
                value=REQUEST["pass_gnomad"],
            ).bind_value(REQUEST, "pass_gnomad")
            # request = ui.textarea(label="Requête").bind_value_from(request, "chr")
            ui.separator()
            with ui.row().classes():
                ui.button(
                    "Reset",
                    color="red",
                    on_click=lambda: reset_request(),
                )
                ui.button(
                    "Search",
                    on_click=lambda: (
                        run_search(),
                        ui.notify("Request sent to the API"),
                    ),
                )

        with ui.column().classes("w-3/5"):
            for variant in variants_type:
                with (
                    ui.card()
                    .bind_visibility(GENERAL_STATE, variant)
                    .classes("w-full h-100")
                ):
                    ui.label(variant).classes("text-h5")
                    GENERAL_STATE["result_table_" + variant] = ui.table(
                        columns=[
                            {"name": "chr", "label": "chr", "field": "chrom"},
                            {
                                "name": "pos",
                                "label": "pos",
                                "field": "pos",
                                "sortable": True,
                            },
                            {
                                "name": "id",
                                "label": "id",
                                "field": "id",
                                "filter": "agNumberColumnFilter",
                            },
                            {"name": "ref", "label": "ref", "field": "ref"},
                            {"name": "alt", "label": "alt", "field": "alt"},
                            {
                                "name": "filter",
                                "label": "filter",
                                "field": "filter",
                            },
                            {
                                "name": "AC",
                                "label": "AC",
                                "field": "AC",
                                "sortable": True,
                            },
                            {
                                "name": "AN",
                                "label": "AN",
                                "field": "AN",
                                "sortable": True,
                            },
                            {
                                "name": "AF",
                                "label": "AF",
                                "field": "AF",
                                "sortable": True,
                            },
                            {
                                "name": "AC_Hom",
                                "label": "AC_Hom",
                                "field": "AC_Hom",
                            },
                            {
                                "name": "in_gnomAD",
                                "label": "in_gnomAD",
                                "field": "in_gnomAD",
                            },
                            {
                                "name": "pass_gnomad",
                                "label": "pass_gnomad",
                                "field": "pass_gnomad",
                            },
                            {"name": "CSQ", "label": "CSQ", "field": "CSQ"},
                        ],
                        rows=[],
                        column_defaults={
                            "headerClasses": "uppercase text-primary center",
                            "align": "center",
                            "width": "70px",
                            "style": "text-wrap: wrap",
                        },
                        selection="single",
                    ).classes("w-full h-9/10")

        with ui.column().classes("w-1/6"):
            for variant in variants_type:
                with ui.card().bind_visibility(GENERAL_STATE, variant).classes("h-100"):
                    ui.label(f"Details on {variant}").classes("text-h5")
                    with ui.tabs().classes("w-full") as tabs:
                        id_tab = ui.tab("Informations")
                        ui.tab("Frequencies")
                        ui.tab("gnomAD")
                    with ui.tab_panels(tabs, value=id_tab).classes("w-full"):
                        with ui.tab_panel("Informations"), ui.grid(columns=2):
                            for detail in details_label_column:
                                ui.label(detail)
                                ui.label().bind_text_from(
                                    GENERAL_STATE["result_table_" + variant],
                                    "selected",
                                    backward=lambda a, detail=detail: (
                                        f"{a[0][details_label_column[detail]]}"
                                        if a != []
                                        else ""
                                    ),
                                )
                        with ui.tab_panel("Frequencies"), ui.grid(columns=2):
                            for detail in frequencies_label_column:
                                ui.label(detail)
                                ui.label().bind_text_from(
                                    GENERAL_STATE["result_table_" + variant],
                                    "selected",
                                    backward=lambda a, detail=detail: (
                                        f"{a[0][frequencies_label_column[detail]]}"
                                        if a != []
                                        else ""
                                    ),
                                )
                        with ui.tab_panel("gnomAD"):
                            for detail in gnomAD_label_column:
                                ui.label(detail)
                                ui.label().bind_text_from(
                                    GENERAL_STATE["result_table_" + variant],
                                    "selected",
                                    backward=lambda a, detail=detail: (
                                        f"{a[0][gnomAD_label_column[detail]]}"
                                        if a != []
                                        else ""
                                    ),
                                )

    with ui.footer():
        ui.label("Ceci est le bas de la page pour rajouter pleeeeeeins de trucs!")

    # WIDGETS INTERACTIONS
    # Switchs interactions with one another
    gnomad_region_switch.on(
        "click",
        lambda: (
            in_gnomad_switch.set_value(False),
            pass_gnomad_switch.set_value(False)
            if not gnomad_region_switch.value
            else None,
        ),
    )
    in_gnomad_switch.on(
        "click",
        lambda: (
            pass_gnomad_switch.set_value(False)
            if not in_gnomad_switch.value
            else gnomad_region_switch.set_value(True)
        ),
    )
    pass_gnomad_switch.on(
        "click",
        lambda: (
            in_gnomad_switch.set_value(True),
            gnomad_region_switch.set_value(True) if pass_gnomad_switch.value else None,
        ),
    )
    # Start can't be higher than Stop
    start_value.on(
        "change",
        lambda: (
            None
            if stop_value.value is None or start_value.value is None
            else (
                stop_value.set_value(start_value.value)
                if stop_value.value < start_value.value
                else None
            )
        ),
    )
    stop_value.on(
        "change",
        lambda: (
            None
            if stop_value.value is None or start_value.value is None
            else (
                start_value.set_value(stop_value.value)
                if stop_value.value < start_value.value
                else None
            )
        ),
    )


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
