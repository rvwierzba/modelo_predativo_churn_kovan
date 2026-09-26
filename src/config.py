import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
EXCEL_PATH = os.path.join(DATA_DIR, "datasets_case_modulo2_5yrs.xlsx")
CSV_PATH = os.path.join(DATA_DIR, "datasets_case_modulo2_5yrs.csv")

SHEETS = {
    "D1": "Dataset 1", # Monthly aggregated transactions
    "D2": "Dataset 2", # Product mix by brand
    "D3": "Dataset 3", # CRM activity & AM contacts
    "D4": "Dataset 4", # Firmographics
    "RAW": "raw data"   # Detailed transaction line items
}

TARGET_SEGMENTS = ["MID MARKET", "STRATEGIC ACCOUNT", "GLOBAL ACCOUNT", "LARGE ENTERPRISE", "PUBLIC SECTOR", "SMALL MARKET", "ALL"]
DEFAULT_TARGET_SEGMENT = "MID MARKET"

RANDOM_STATE = 42
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
MODELS_DIR = os.path.join(BASE_DIR, "models_saved")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Financial Constants from Case (PDF)
NRR_BASE_REVENUE_B2B = 1_840_000_000 # R$ 1.84 billion total revenue
NRR_STRATEGIC_REVENUE = 1_310_000_000 # R$ 1.31 billion strategic segment
CONTRACTION_ANNUAL_LOSS = 248_000_000 # R$ 248 million lost to contraction
AM_TOTAL_CAPACITY_PLANS_PER_Q = 138 # 46 AMs * 3 plans/quarter
