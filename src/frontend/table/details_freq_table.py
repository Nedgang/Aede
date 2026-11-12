##########
# IMPORT #
##########
from nicegui import ui


#####################
# FREQUENCIES TABLE #
#####################
def details_freq_table(variant_type: str) -> ui.table:
    if variant_type == "SNV-Indel":
        return ui.table(
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
        )
    else:
        raise ValueError(f"{variant_type} not parametered yet")
