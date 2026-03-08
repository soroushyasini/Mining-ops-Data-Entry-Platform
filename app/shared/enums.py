from enum import Enum


class GrindingFacility(str, Enum):
    ROBAT_SEFID = "robat_sefid"
    SHEN_BETON = "shen_beton"
    KAVIAN = "kavian"


class RecordStatus(str, Enum):
    REGISTERED = "registered"
    COSTED = "costed"
    PAID = "paid"


class EntityType(str, Enum):
    TRUCK = "truck"
    BUNKER = "bunker"
    LAB_BATCH = "lab_batch"


class SampleType(str, Enum):
    K = "K"
    L = "L"
    CR = "CR"
    T = "T"
    RC = "RC"
