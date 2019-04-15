# module constants

INFINITY = float('inf')

# Euro constants
FIXED = 'FIXED'  # banks spend a fixed amount into the economy
PROFIT_PERCENTAGE = 'PROFIT PERCENTAGE'  # banks spend a percentage of their profit into the economy
RESERVE_PERCENTAGE = 'RESERVE PERCENTAGE'  # banks spend a percentage of their reserve into the economy
CAPITAL_PERCENTAGE = 'CAPITAL PERCENTAGE'  # banks spend a percentage of their capital (reserve + financial assets) into the economy
SPENDING_MODES = [FIXED, PROFIT_PERCENTAGE, RESERVE_PERCENTAGE, CAPITAL_PERCENTAGE]

GROW_INITIAL = 'GROW INITIAL'
GROW_CURRENT = 'GROW_CURRENT'
GROWTH_TARGETS = [GROW_INITIAL, GROW_CURRENT]

ASSET_GROWTH = 'ASSET GROWTH'  # a percentage of what is added to the financial market trickles to the real economy
ASSET_CAPITAL = 'ASSET_CAPITAL'  # a percentage of what exists in the financial market trickles to the real economy
ASSET_TRICKLE_MODES = [ASSET_GROWTH, ASSET_CAPITAL]

QE_NONE = 'QE_NONE'  # no QE
QE_FIXED = 'QE_FIXED'  # fixed amount QE, adjusted for initial_inflation_rate
QE_RELATIVE = 'QE_RELATIVE'  # QE amount relative to outstanding debt

QE_MODES = [QE_NONE, QE_FIXED, QE_RELATIVE]

# SuMSy constants
MAX_DEM_TIERS = 5

NONE = 'NONE'
FIXED_SPENDING = 'FIXED'
PER_CAPITA = 'PER_CAPITA'
COMMON_GOOD_SPENDING = [NONE, FIXED_SPENDING, PER_CAPITA]
