from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"
DICTIONARY_DIR = BASE_DIR / "dictionaries"
EXAMPLE_DIR = BASE_DIR / "examples"

for path in [DATA_DIR, RAW_DATA_DIR, OUTPUT_DIR, LOG_DIR]:
    path.mkdir(parents=True, exist_ok=True)

MAX_PRODUCTS = 300
MIN_REVIEWS_PER_PRODUCT = 20
TIME_WINDOW_MONTHS = 24
SNAPSHOT_FREQ_DAYS = 30

REQUEST_DELAY_SECONDS = 2
MAX_RETRIES = 3
USER_AGENT = "SemanticDriftMonitor/0.1 academic-research"

ABSTRACTION_THRESHOLD = 2.5

ALERT_THRESHOLD_DRIFT = 0.35
ALERT_THRESHOLD_SKEPTICISM = 0.20
ALERT_THRESHOLD_LOCKIN = 0.40

PROMO_LEXICON_PATH = DICTIONARY_DIR / "promo_sunscreen_en.yaml"
SKEPTICISM_LEXICON_PATH = DICTIONARY_DIR / "skepticism_en.yaml"
VALUE_LEXICON_PATH = DICTIONARY_DIR / "value_en.yaml"
SCENARIO_LEXICON_PATH = DICTIONARY_DIR / "scenarios_sunscreen_en.yaml"
CONCRETENESS_LEXICON_PATH = DICTIONARY_DIR / "concreteness_sunscreen_en.yaml"

