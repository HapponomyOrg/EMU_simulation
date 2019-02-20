# module constants

# Euro constants
FIXED = 'FIXED'                             # banks spend a fixed amount into the economy
PROFIT_PERCENTAGE = 'PROFIT PERCENTAGE'     # banks spend a percentage of their profit into the economy
CAPITAL_PERCENTAGE = 'CAPITAL PERCENTAGE'   # banks spend a percentage of their capital into the economy

SPENDING_MODES = [FIXED, PROFIT_PERCENTAGE, CAPITAL_PERCENTAGE]

QE_NONE = 'QE_NONE'         # no QE
QE_FIXED = 'QE_FIXED'       # fixed amount QE, adjusted for inflation
QE_RELATIVE = 'QE_RELATIVE' # QE amount relative to outstanding debt

QE_MODES = [QE_NONE, QE_FIXED, QE_RELATIVE]

# SuMSy constants
MAX_DEM_TIERS = 5

NONE = 'NONE'
FIXED_SPENDING = 'FIXED'
PER_CAPITA = 'PER_CAPITA'
COMMON_GOOD_SPENDING = [NONE, FIXED_SPENDING, PER_CAPITA]