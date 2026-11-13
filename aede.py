##########
# IMPORT #
##########
# import requests
from nicegui import ui

from src.frontend.pages import home_page, search_page

#############
# FUNCTIONS #
#############
# def clear_results(variants: list(str)):
#     for variant_type in variants:
#         GENERAL_STATE["result_table_" + variant_type].options["rowData"].clear()
#         GENERAL_STATE[f"selected_{variant_type}_variant"] = False
#         GENERAL_STATE[f"details_variant_{variant_type}"] = {
#             col: ""
#             for col in list(details_label_column.values())
#             + list(frequencies_label_column.values())
#             + list(gnomAD_label_column.values())
#         }
#         GENERAL_STATE[f"details_table_{variant_type}"].update_rows(
#             [
#                 {key: row[key] if key == "pop" else "" for key in row}
#                 for row in GENERAL_STATE[f"details_table_{variant_type}"].rows
#             ]
#         )
#         GENERAL_STATE[f"csq_table_{variant_type}"].options["rowData"].clear()
#         GENERAL_STATE[f"display_{variant_type}_csq"] = False


########
# MAIN #
########
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
