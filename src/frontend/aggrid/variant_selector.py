##########
# IMPORT #
##########
from nicegui import ui


####################
# VARIANT SELECTOR #
####################
def variant_selector(rows: list(dict)) -> ui.aggrid:
    return ui.aggrid(
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
            "rowData": rows,
            "rowSelection": {"mode": "singleRow"},
        },
        theme="balham",
        auto_size_columns=True,
    ).classes("w-full h-9/10")
