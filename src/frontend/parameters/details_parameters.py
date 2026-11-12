##########
# IMPORT #
##########
from nicegui import ui


#############
# FUNCTIONS #
#############
def variant_details_label_column(variant_type: str) -> dict:
    """
    Return a dic containing label: column/field of informations of interest for this
    particular variant_type details.
    """
    if variant_type == "SNV-Indel":
        return {
            "Chromosome": "chrom",
            "Position": "pos",
            "ID": "id",
            "Reference": "ref",
            "Alternative": "alt",
            "Filter": "filter",
            "DP": "DP",
            "Variant type": "variant_type",
        }
    else:
        raise ValueError(f"{variant_type} not parametered yet")


def variant_frequencies_label_column(variant_type: str) -> dict:
    """
    Return a dic containing label: column/field of informations of interest for this
    particular variant_type frequencies.
    """
    if variant_type == "SNV-Indel":
        return {
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
    else:
        raise ValueError(f"{variant_type} not parametered yet")


def variant_gnomad_label_column(variant_type: str) -> dict:
    """
    Return a dic containing label: column/field of informations of interest for this
    particular variant_type gnomAD details.
    """
    if variant_type == "SNV-Indel":
        return {
            "Present in gnomAD": "inGnomad",
            "Pass gnomAD QC": "passGnomad",
            "Not covered by gnomAD": "notCoveredByGnomad",
        }
    else:
        raise ValueError(f"{variant_type} not parametered yet")


def complementary_freq_details(variant_type: str) -> list:
    """
    Return list of complementary information to the frequency table depending on the
    variant type.
    """
    if variant_type == "SNV-Indel":
        return ["AC_Hom", "grpmax"]
    else:
        raise ValueError(f"{variant_type} not parametered yet")
