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
    with ui.header().classes("items-center justify-between"):
        ui.label("onlinePOPGEN").classes("text-h3")
        # ui.button("Search")
        ui.switch("Dark mode").bind_value(ui.dark_mode())

    with left_drawer, ui.card().classes("w-full"):
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
                    test_feature = "ENST00000450305,ENST00000456328,ENST00000488147,ENST00000831140,ENST00000831141,ENST00000831145,ENST00000831146,ENST00000831154,ENST00000831157,ENST00000831158,ENST00000831161,ENST00000831165,ENST00000831170,ENST00000831172,ENST00000831173,ENST00000831177,ENST00000831185,ENST00000831189,ENST00000831201,ENST00000831204,ENST00000831205,ENST00000831206,ENST00000831210,ENST00000831215,ENST00000831217,ENST00000831218,ENST00000831219,ENST00000831222,ENST00000831225,ENST00000831228,ENST00000831229,ENST00000831230,ENST00000831231,ENST00000831232,ENST00000831237,ENST00000831239,ENST00000831240,ENST00000831242,ENST00000831243,ENST00000831245,ENST00000831246,ENST00000831248,ENST00000831253,ENST00000831261,ENST00000831272,ENST00000831275,ENST00000831276,ENST00000831279,ENST00000831281,ENST00000831287,ENST00000831289,ENST00000831290,ENST00000831291,ENST00000831292,ENST00000831295,ENST00000831298,ENST00000831299,ENST00000831302,ENST00000831305,ENST00000831311,ENST00000831312,ENST00000831314,ENST00000831319,ENST00000831323,ENST00000831324,ENST00000831325,ENST00000831326,ENST00000831333,ENST00000831334,ENST00000831336,ENST00000831337,ENST00000831338,ENST00000831340,ENST00000831341,ENST00000831344,ENST00000831351,ENST00000831355,ENST00000831357,ENST00000831359,ENST00000831361,ENST00000831363,ENST00000831369,ENST00000831370,ENST00000831371,ENST00000831376,ENST00000831381,ENST00000831382,ENST00000831387,ENST00000831392,ENST00000831394,ENST00000831395,ENST00000831396,ENST00000831398,ENST00000831405,ENST00000831408,ENST00000831414,ENST00000831417,ENST00000831423,ENST00000831424,ENST00000831430,ENST00000831433,ENST00000831438,ENST00000831439,ENST00000831444,ENST00000831447,ENST00000831457,ENST00000831460,ENST00000831463,ENST00000831464,ENST00000831465,ENST00000831467,ENST00000831470,ENST00000831480,ENST00000831481,ENST00000831482,ENST00000831484,ENST00000831487,ENST00000831491,ENST00000831499,ENST00000831500,ENST00000831504,ENST00000831505,ENST00000831506,ENST00000831507,ENST00000831508,ENST00000831509,ENST00000831514,ENST00000831517,ENST00000831559,ENST00000831678,ENST00000831698,ENST00000831699,ENST00000831700,ENST00000831701,ENST00000831702,ENST00000831703,ENST00000831704,ENST00000831705,ENST00000831706,ENST00000831707,ENST00000831738,ENST00000831739,ENST00000831746,ENST00000831747,ENST00000832823,ENST00000832824,ENST00000832825,ENST00000832826,ENST00000832827,ENST00000832828,ENST00000832829,ENST00000832830,ENST00000832831,ENST00000832832,ENST00000832833,ENST00000832834,ENST00000832835,ENST00000832836,ENST00000832837,ENST00000832838,ENST00000832839,ENST00000832840,ENST00000832841,ENST00000832842,ENST00000832843,ENST00000832844,ENST00000832845,ENST00000832846,ENST00000832847,ENST00000832848,ENST00000832849,NR_024540.1,NR_046018.2"
                    ui.select(
                        label="Select a feature",
                        options=test_feature.split(","),
                        multiple=True,
                        clearable=True,
                    ).bind_value_to(
                        GENERAL_STATE, f"selected_{variant}_features"
                    ).classes("w-full")
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

    with ui.footer(fixed=False):
        ui.label("Ceci est le bas de la page pour rajouter pleeeeeeins de trucs!")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
