from enum import Enum


class GrindingFacility(str, Enum):
    ROBAT_SEFID = "robat_sefid"
    SHEN_BETON = "shen_beton"
    KAVIAN = "kavian"


class RecordStatus(str, Enum):
    REGISTERED = "registered"
    COSTED = "costed"
    INVOICED = "invoiced"
    PAID = "paid"


class EntityType(str, Enum):
    TRUCK = "truck"
    BUNKER = "bunker"
    LAB_BATCH = "lab_batch"
    GRINDING = "grinding"
    PAYMENT_GROUP = "payment_group"


class SampleType(str, Enum):
    K = "K"
    L = "L"
    CR = "CR"
    T = "T"
    RC = "RC"
