##########
# IMPORT #
##########
from nicegui import ui


########
# HOME #
########
@ui.page("/")
def home_page():
    """
    Basic home page for redirecting and allowing authentification in future update.
    """
    ui.navigate.to("/search")
