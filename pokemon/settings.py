"""Pokemon Pipeline settings and constants"""

# Base URL for Pokemon API
BASE_URL = "https://pokeapi.co/api/v2"

# API endpoints
POKEMON_LIST_URL = f"{BASE_URL}/pokemon"
POKEMON_DETAIL_URL = f"{BASE_URL}/pokemon"
BERRY_LIST_URL = f"{BASE_URL}/berry"
BERRY_DETAIL_URL = f"{BASE_URL}/berry"
ABILITY_URL = f"{BASE_URL}/ability"
MOVE_URL = f"{BASE_URL}/move"
TYPE_URL = f"{BASE_URL}/type"

# Pagination settings
DEFAULT_LIMIT = 20
MAX_POKEMON_ID = 1010  # Current total Pokemon count
