##########
# IMPORT #
##########
from nicegui import ui


########################
# VARIANT CONSEQUENCES #
########################
def variant_consequences(variant_type: str) -> ui.aggrid:
    """
    Depending on the variant type, return an aggrid adapted to general display details on
    selected variant consequences.
    """
    if variant_type == "SNV-Indel":
        return ui.aggrid(
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
    else:
        raise ValueError(f"{variant_type} not supported yet.")
