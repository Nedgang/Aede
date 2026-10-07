##########
# IMPORT #
##########
import glob
import os

import requests
from nicegui import ui


#############
# FUNCTIONS #
#############
def run_variant_search() -> None:
    """
    Send the get request to the API, handle the answer and return a dict with results
    from database search.
    """
    ans = requests.get("http://localhost:8000/query/v1/variants/", params=REQUEST)
    if ans.ok:
        for variant in ans.json()[0]:
            GENERAL_STATE["result_table_" + variant].options["rowData"].clear()
            GENERAL_STATE["result_table_" + variant].options["rowData"].extend(
                ans.json()[0][variant]
            )
        ui.notify("Results received!")
    else:
        ui.notify(ans.json()["detail"], type="negative")


def run_csq_search(request) -> None:
    """ """
    ans = requests.get("http://localhost:8000/query/v1/csq", params=request)
    if ans.ok:
        GENERAL_STATE[f"csq_table_{request['variant_type']}"].options["rowData"].clear()
        GENERAL_STATE[f"csq_table_{request['variant_type']}"].options["rowData"].extend(
            ans.json()
        )
    else:
        ui.notify(ans.json()["detail"], type="negative")


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


async def output_selected_row(variant_type):
    row = await GENERAL_STATE[f"result_table_{variant_type}"].get_selected_row()
    if row:
        GENERAL_STATE[f"selected_{variant_type}_variant"] = True
        GENERAL_STATE[f"details_variant_{variant_type}"] = row
        GENERAL_STATE[f"details_table_{variant_type}"].update_rows(
            [
                {
                    "pop": "All",
                    "AC": row["AC"],
                    "AN": row["AN"],
                    "AF": row["AF"],
                },
                {
                    "pop": "XY",
                    "AC": row["AC_XY"],
                    "AN": row["AN_XY"],
                    "AF": row["AF_XY"],
                },
                {
                    "pop": "XX",
                    "AC": row["AC_XX"],
                    "AN": row["AN_XX"],
                    "AF": row["AF_XX"],
                },
                {
                    "pop": "grpmax",
                    "AC": row["AC_grpmax"],
                    "AN": row["AN_grpmax"],
                    "AF": row["AF_grpmax"],
                },
            ]
        )
        GENERAL_STATE[f"select_{variant_type}_features"].set_options(
            row["Feature"].split(",") if row["Feature"] is not None else []
        )
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
                {
                    "pop": "All",
                    "AC": "",
                    "AN": "",
                    "AF": "",
                },
                {
                    "pop": "XY",
                    "AC": "",
                    "AN": "",
                    "AF": "",
                },
                {
                    "pop": "XX",
                    "AC": "",
                    "AN": "",
                    "AF": "",
                },
                {
                    "pop": "grpmax",
                    "AC": "",
                    "AN": "",
                    "AF": "",
                },
            ]
        )
        GENERAL_STATE[f"select_{variant_type}_features"].set_options([])
        GENERAL_STATE[f"csq_table_{variant_type}"].options["rowData"].clear()


####################
# GLOBAL VARIABLES #
####################
# Finding options from data structure, which lead to automatic update of the front with
# data upload
all_variants_type = sorted(
    [dir.name for dir in os.scandir("../Mneme/") if dir.is_dir()]
)
chromosomes = sorted(
    {
        auto
        for auto in {chr.split("/")[-1] for chr in glob.iglob("../Mneme/*/chr*")}
        if auto.split("chr")[-1].isdigit()
    },
    key=lambda c: int(c.split("chr")[-1]),
) + sorted(
    {
        gono
        for gono in {chr.split("/")[-1] for chr in glob.iglob("../Mneme/*/chr*")}
        if not gono.split("chr")[-1].isdigit()
    },
    key=lambda c: c.split("chr")[-1],
)

with open("../Mneme/genes.tsv") as file:
    gene_to_chrom = {
        line.strip().split("\t")[0]: line.strip().split("\t")[1]
        for line in file
        if line.strip().split("\t")[0] != "SYMBOL"
    }

REQUEST = reset_request()

details_label_column = {
    "Chromosome": "chrom",
    "Position": "pos",
    "ID": "id",
    "Reference": "ref",
    "Alternative": "alt",
    "Filter": "filter",
    "DP": "DP",
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
    GENERAL_STATE.setdefault(f"display_{variant_type}_csq", False)
    GENERAL_STATE.setdefault(f"display_{variant_type}_variants", True)
    GENERAL_STATE.setdefault(f"selected_{variant_type}_variant", False)


########
# MAIN #
########
@ui.page("/")
def search_page():
    # PAGE & WIDGETS DESCRIPTION
    left_drawer = ui.left_drawer(bordered=True, elevated=True)
    with ui.header(elevated=True).classes():
        ui.image("logo/RF-Inserm_Simplifie_rvb_Blanc.png").classes("w-64")
        ui.label("onlinePOPGEN").classes("text-h3")
        ui.button(icon="wysiwyg", on_click=lambda: left_drawer.toggle())
        ui.switch("Dark mode").bind_value(ui.dark_mode())

    with left_drawer, ui.column().classes("w-full"):
        ui.label("Request").classes("text-h5")
        # Variant type selection
        ui.select(
            options=(all_variants_type),
            label="Variant type",
            multiple=True,
            on_change=lambda: GENERAL_STATE.update(
                {var: var in REQUEST["variant_type"] for var in all_variants_type},
            ),
            validation=lambda b: (
                "Must select at least one variant type" if b == [] else None
            ),
        ).bind_value(REQUEST, "variant_type").classes("w-full")
        # Gene search
        select_gene = (
            ui.select(
                label="Gene",
                options=list(gene_to_chrom.keys()),
                with_input=True,
                clearable=True,
            )
            .bind_value(REQUEST, "gene")
            .classes("w-full")
        )
        # ID search
        ui.input(label="Variant ID").bind_value(REQUEST, "id").classes("w-full")
        # Feature
        with open("../Mneme/feature.txt", "r") as file:
            ui.select(
                label="Feature ID",
                options=[feature for feature in file],
                with_input=True,
                multiple=True,
                clearable=True,
            ).bind_value(REQUEST, "feature").classes("w-full")
        # Variant impact
        with open("../Mneme/impact.txt", "r") as file:
            ui.select(
                label="Variant impact",
                options=[impact for impact in file],
                with_input=True,
                multiple=True,
                clearable=True,
            ).bind_value(REQUEST, "impact").classes("w-full")
        # Consequence selection
        with open("../Mneme/consequences.txt", "r") as file:
            ui.select(
                label="Variant consequence",
                options=[csq for csq in file],
                with_input=True,
                multiple=True,
                clearable=True,
            ).bind_value(REQUEST, "csq").classes("w-full")
        # Chromosome choice
        select_chr = (
            ui.select(
                label="Chromosome",
                options=chromosomes,
            )
            .bind_value(REQUEST, "chr")
            .classes("w-1/2")
        )
        # Selection start
        start_value = (
            ui.number(label="Start", min=0, value=REQUEST["start"], precision=0)
            .bind_value(REQUEST, "start")
            .classes("w-1/2")
        )
        # Selection stop
        stop_value = (
            ui.number(label="End", min=0, value=REQUEST["stop"], precision=0)
            .bind_value(REQUEST, "stop")
            .classes("w-1/2")
        )
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
        with ui.row().classes("w-full"):
            ui.button(
                "Reset",
                color="red",
                on_click=lambda: REQUEST.update(reset_request()),
            )
            ui.space()
            ui.button(
                "Search",
                on_click=lambda left_drawer=left_drawer: (
                    run_variant_search(),
                    ui.notify("Request sent to the API"),
                ),
            )
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
    select_gene.on_value_change(
        lambda c, select_chr=select_chr: (
            select_chr.set_value(gene_to_chrom[c.value])
            if c.value is not None
            else None,
            select_chr.disable() if c.value is not None else select_chr.enable(),
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

    for variant in all_variants_type:
        # Variants result row
        with ui.row().classes("w-full").bind_visibility(GENERAL_STATE, variant):
            with (
                ui.row()
                .classes("w-full")
                .bind_visibility(GENERAL_STATE, f"display_{variant}_variants")
            ):
                with (
                    ui.card().classes("w-75/100 h-105"),
                ):
                    with ui.row():
                        ui.label(variant).classes("text-h5")
                        col_select = ui.button(icon="menu")
                    GENERAL_STATE["result_table_" + variant] = (
                        ui.aggrid(
                            {
                                "columnDefs": [
                                    {"field": "chrom"},
                                    {"field": "pos", "filter": "agNumberColumnFilter"},
                                    {"field": "id", "filter": "agTextColumnFilter"},
                                    {"field": "ref", "filter": "agTextColumnFilter"},
                                    {"field": "alt", "filter": "agTextColumnFilter"},
                                    {"field": "filter", "filter": "agTextColumnFilter"},
                                    {"field": "AC", "filter": "agNumberColumnFilter"},
                                    {"field": "AN", "filter": "agNumberColumnFilter"},
                                    {"field": "AF", "filter": "agNumberColumnFilter"},
                                    {
                                        "field": "AC_Hom",
                                        "filter": "agNumberColumnFilter",
                                    },
                                    {"field": "inGnomad"},
                                    {"field": "passGnomad"},
                                ],
                                "rowData": [],
                                "rowSelection": {"mode": "singleRow"},
                            },
                            theme="balham",
                            auto_size_columns=True,
                        )
                        .on(
                            "rowSelected",
                            lambda _, variant=variant: output_selected_row(variant),
                        )
                        .classes("w-full h-9/10")
                    )
                    # Allowing columns selection
                    with col_select, ui.menu(), ui.column().classes("'gap-0 p-2'"):
                        for column in [
                            i
                            for i in GENERAL_STATE[f"result_table_{variant}"].options[
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
                                on_change=lambda e, variant=variant, column=column: (
                                    GENERAL_STATE[
                                        f"result_table_{variant}"
                                    ].run_grid_method(
                                        "setColumnsVisible",
                                        [column["field"]],
                                        e.value,
                                    )
                                ),
                            )
                with ui.card().classes("w-23/100 h-105"):
                    with ui.row().classes("w-full"):
                        ui.label(f"Details on {variant}").classes("text-h5")
                        ui.switch("CSQ").bind_value_to(
                            GENERAL_STATE, f"display_{variant}_csq"
                        )
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
                                    f"details_variant_{variant}",
                                    backward=lambda a, detail=detail: (
                                        f"{a[details_label_column[detail]]}"
                                    ),
                                )
                        with ui.tab_panel("freq"):
                            GENERAL_STATE[f"details_table_{variant}"] = ui.table(
                                columns=[
                                    {
                                        "name": "pop_type",
                                        "label": "",
                                        "field": "pop",
                                        "align": "center",
                                    },
                                    {
                                        "name": "AC",
                                        "label": "AC",
                                        "field": "AC",
                                        "align": "center",
                                        "sortable": True,
                                    },
                                    {
                                        "name": "AN",
                                        "label": "AN",
                                        "field": "AN",
                                        "align": "center",
                                        "sortable": True,
                                    },
                                    {
                                        "name": "AF",
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
                                        f"details_variant_{variant}",
                                        backward=lambda a, freq=freq: (
                                            f"{a[frequencies_label_column[freq]]}"
                                        ),
                                    )
                        with ui.tab_panel("gnomad"), ui.grid(columns=2):
                            for detail in gnomAD_label_column:
                                ui.label(detail)
                                ui.label().bind_text_from(
                                    GENERAL_STATE,
                                    f"details_variant_{variant}",
                                    backward=lambda a, detail=detail: (
                                        f"{a[gnomAD_label_column[detail]]}"
                                    ),
                                )
            # CSQ result row
            with (
                ui.row()
                .classes("w-full")
                .bind_visibility_from(GENERAL_STATE, f"display_{variant}_csq")
            ):
                with ui.card().classes("w-23/100 h-105"):
                    ui.label(f"Feature affected from {variant} variant").classes(
                        "text-h5"
                    )
                    ui.switch("Display variants panel", value=True).bind_value(
                        GENERAL_STATE, f"display_{variant}_variants"
                    )
                    GENERAL_STATE[f"select_{variant}_features"] = (
                        ui.select(
                            label="Select a feature",
                            options=[],
                            multiple=True,
                            clearable=True,
                        )
                        .bind_value_to(GENERAL_STATE, f"selected_{variant}_features")
                        .classes("w-full")
                    )
                    with ui.row().classes("w-full"):
                        ui.button("Search").bind_enabled_from(
                            GENERAL_STATE, f"selected_{variant}_variant"
                        ).on_click(
                            lambda variant=variant: run_csq_search(
                                {
                                    "variant_type": variant,
                                    "chr": GENERAL_STATE[f"details_variant_{variant}"][
                                        "chrom"
                                    ],
                                    "variant_key": GENERAL_STATE[
                                        f"details_variant_{variant}"
                                    ]["variant_key"],
                                    "features": GENERAL_STATE[
                                        f"selected_{variant}_features"
                                    ],
                                }
                            )
                        )
                with ui.card().classes("w-75/100 h-105"):
                    with ui.row():
                        ui.label(f"CSQ on {variant}").classes("text-h5")
                        col_select = ui.button(icon="menu")
                    GENERAL_STATE["csq_table_" + variant] = ui.aggrid(
                        {
                            "columnDefs": [
                                {
                                    "field": "Consequence",
                                    "filter": "agTextColumnFilter",
                                },
                                {"field": "IMPACT", "filter": "agTextColumnFilter"},
                                {"field": "SYMBOL", "filter": "agTextColumnFilter"},
                                {"field": "Gene", "filter": "agTextColumnFilter"},
                                {
                                    "field": "Feature_type",
                                    "filter": "agTextColumnFilter",
                                },
                                {"field": "Feature", "filter": "agTextColumnFilter"},
                                {"field": "BIOTYPE", "filter": "agTextColumnFilter"},
                                {"field": "EXON", "filter": "agTextColumnFilter"},
                                {"field": "INTRON", "filter": "agTextColumnFilter"},
                                {
                                    "field": "CDS_position",
                                    "filter": "agTextColumnFilter",
                                },
                                {
                                    "field": "Amino_acids",
                                    "filter": "agTextColumnFilter",
                                },
                                {"field": "Codons", "filter": "agTextColumnFilter"},
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
                            for i in GENERAL_STATE["csq_table_" + variant].options[
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
                                on_change=lambda e, variant=variant, column=column: (
                                    GENERAL_STATE[
                                        "csq_table_" + variant
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
