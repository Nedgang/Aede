##########
# IMPORT #
##########
from nicegui import ui

from src.frontend.pages import home_page, search_page

########
# MAIN #
########
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
