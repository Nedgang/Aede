##########
# IMPORT #
##########
from nicegui import ui


####################
# VARIANT SELECTOR #
####################
def variant_selector(variant_type: str) -> ui.aggrid:
    """
    Depending on the variant type, return an aggrid adapted to general display and variant
    selection.
    """
    if variant_type == "SNV-Indel":
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
                    {
                        "headerName": "AC",
                        "field": "AC",
                        "filter": "agNumberColumnFilter",
                    },
                    {
                        "headerName": "AN",
                        "field": "AN",
                        "filter": "agNumberColumnFilter",
                    },
                    {
                        "headerName": "AF",
                        "field": "AF",
                        "filter": "agNumberColumnFilter",
                    },
                    {
                        "headerName": "AC_Hom",
                        "field": "AC_Hom",
                        "filter": "agNumberColumnFilter",
                    },
                    {"headerName": "in gnomAD", "field": "inGnomad"},
                    {"headerName": "pass gnomAD", "field": "passGnomad"},
                    {
                        "headerName": "variant type",
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
    else:
        raise ValueError(f"{variant_type} not supported yet.")
