# module main
# percentages are represented as a fractional number between 0 and 1, 0 being 0%, 0.5 being 50% and 1 being 100%

import os

FIXED = 'FIXED'                             # banks spend a fixed amount into the economy
PROFIT_PERCENTAGE = 'PROFIT PERCENTAGE'     # banks spend a percentage of their profit into the economy
CAPITAL_PERCENTAGE = 'CAPITAL PERCENTAGE'   # banks spend a percentage of their capital into the economy

QE_NONE = 'QE_NONE'         # no QE
QE_FIXED = 'QE_FIXED'       # fixed amount QE, adjusted for inflation
QE_RELATIVE = 'QE_RELATIVE' # QE amount relative to outstanding debt

SPENDING_MODES = [FIXED, PROFIT_PERCENTAGE, CAPITAL_PERCENTAGE]

growth_rate = 0.030      # growth rate of available money (IM2). This is money that circulates in the real economy
inflation_rate = 0.019   # inflation

initial_fixed_spending = 1000.0     # initial spending if bank spending mode is FIXED
pp = 0.02                           # percentage of profit that banks spend into the real economy
cp = 0.02                           # percentage of capital that banks spend into the real economy

mr = 0.04 # minimum reserve

pbdr = 0.1 # bank payback rate
nbdr = 0.05 # non bank payback rate

ecbi = 0.01     # ECB interest rate
pbi = 0.025     # commercial bank interest rate
savei = 0.005   # interest on savings

nmr = 1.00              # minimum % of money of a loan that is newly created. The rest is taken from im1 if possible.
min_bank_reserve = 0.00 # minimum % reserve a bank wants to hold in im1. This influences how much money will be created.

no_loss = True      # whether or not banks are ok running a loss
min_profit = 0.20   # minimum % in income (from interest) that is retained as profit (only if no loss is true).

qe_spending = QE_RELATIVE  # QE spending mode
qe = []                 # QE injected by ECB, adjusted for inflation. This amount is subtracted from om1 to keep track of money creation by ECB.
qe_trickle = 1.00       # percentage of QE that immediately flows through to IM2. Can be interpreted as a form of helicopter money.
qe_profit = False       # whether or not qe is interpreted as bank profit.
qe_fixed_initial = 0.0  # initial fixed QE
qe_relative = 0.025     # relative qe in % of IM2

im1 = [] # inside money on bank's account
im2 = [] # inside money that is on non bank accounts

lending = []    # money that has been borrowed per cycle
new_im = []     # money that has been created
debt = []       # outstanding debt on which interest is paid
payoff = []     # payoff of principal debt
interest = []   # interest paid

saving_rate = 0.2       # % of IM2 which is saved.
savings_interest = []   # interest earned from savings

om1 = [] # outside money on ECB account. Can be negative when new om money is created
om2 = [] # outside money on private banks' account

bank_profit = []    # bank profit: income from interest - payoff of loans and interests to ECB
bank_spending = []  # money banks spend into the real economy
bank_fixed = []     # fixed amount that banks spend into the real economy, adjusted for inflation
bank_debt = []      # outstanding debt of banks to the ECB
bank_payoff = []    # payoff of principal bank debt
bank_interest = []  # interest paid to ecb

growth = []     # growth per cycle
om_growth = []  # om growth per cycle

# initial parameters
initial_im2 = 100000.0  # initial amount of IM2. Needs to be > 0.


def runSimulation():
    # write parameters
    if os.path.exists('./generated data/parameters.txt'):
        os.remove('./generated data/parameters.txt')

    f = open('./generated data/parameters.txt', 'w')
    f.write(f'Initial IM2 = {initial_im2:.2f}\n')
    f.write('\n')
    f.write(f'IM2 growth rate = {growth_rate * 100} %\n')
    f.write(f'Inflation = {inflation_rate * 100} %\n')
    f.write('\n')
    f.write(f'Commercial payback rate (% of debt) = {nbdr * 100} %\n')
    f.write(f'Commercial interest rate (% of debt) = {pbi * 100} %\n')
    f.write('\n')
    f.write(f'Saving rate (% of IM2) = {saving_rate * 100}\n')
    f.write(f'Savings interest rate = {savei * 100} %\n')
    f.write('\n')
    f.write(f'Minimal required reserve = {mr * 100} %\n')
    f.write(f'Minimal desired reserve (IM) = {min_bank_reserve * 100} %\n')
    f.write('\n')
    f.write(f'Bank payback rate (% of debt) = {pbdr * 100} %\n')
    f.write(f'Bank interest rate (% of debt) = {ecbi * 100} %\n')
    f.write('\n')
    f.write(f'Minimal \'new IM %\' on loans = {nmr * 100} %\n')
    f.write('\n')
    f.write(f'No loss = {no_loss}\n')
    if no_loss:
        f.write(f'Minimal profit from interest = {min_profit * 100} %\n')
    f.write('\n')
    f.write(f'Initial fixed spending = {initial_fixed_spending:.2f}\n')
    f.write(f'% profit spending = {pp * 100} %\n')
    f.write(f'% capital spending = {cp * 100} %\n')
    f.write('\n')
    f.write(f'QE spending mode: {qe_spending}\n')
    if qe_spending == QE_FIXED:
        f.write(f'Initial QE = {qe_fixed_initial:.2f}\n')
    elif qe_spending == QE_RELATIVE:
        f.write(f'QE % of debt = {qe_relative * 100} %\n')
    #f.write(f'QE is bank profit = {qe_profit}\n')
    if qe_spending != QE_NONE:
        f.write(f'QE trickle = {qe_trickle * 100} %\n')
    f.close()

    for spending_mode in SPENDING_MODES:
        # initialize data output file
        if os.path.exists(f'./generated data/{spending_mode}.csv'):
            os.remove(f'./generated data/{spending_mode}.csv')

        f = open(f'./generated data/{spending_mode}.csv', 'w')
        f.write('OM 1,OM 2,OM total,OM growth,')
        f.write('QE,QE trickle,')
        f.write('Bank spending,Bank profit,Bank debt,Bank payoff,Bank interest,')
        f.write('IM 1,IM 2,Earned interest,Created IM,Debt,Payoff,Interest,')
        f.write('Growth,Lending,IM total,')
        f.write('Lending % IM2,Lending % IM total,')
        f.write('IM 1 % IM total,IM 2 % IM total,')
        f.write('Earned interest % IM 2,Earned interest % IM total,')
        f.write('Debt % IM 2,Debt % IM total,')
        f.write('Created % IM 2,Created % IM total\n')
        print(f'{spending_mode}')

        for i in range(500):
            if i == 0:
                initialize()
            else:
                # copy previous state
                im1.append(im1[i - 1])
                im2.append(im2[i - 1])
                lending.append(0.0)
                debt.append(debt[i - 1])
                payoff.append(0.0)
                interest.append(0.0)
                new_im.append(new_im[i - 1])

                om1.append(om1[i - 1])
                om2.append(om2[i - 1])
                bank_profit.append(0.0)
                bank_spending.append(0.0)
                bank_fixed.append(bank_fixed[i - 1] + bank_fixed[i - 1] * inflation_rate)
                bank_debt.append(bank_debt[i - 1])
                bank_payoff.append(0.0)
                bank_interest.append(0.0)

                growth.append(0.0)

                if qe_spending == QE_FIXED:
                    qe.append(qe[i - 1] + qe[i - 1] * inflation_rate)
                else:
                    qe.append(0.0) # determine after debt has been processed

                # calculate interest on savings from previous cycle and add to im2
                savings_interest.append(im2[i - 1] * saving_rate * savei)

                # determine growth
                growth[i] = im2[i] * growth_rate + im2[i] * growth_rate * inflation_rate + im2[i] * inflation_rate
                target_im2 = im2[i] + growth[i]

                # earn calculated interest
                im2[i] += savings_interest[i]
                im1[i] -= savings_interest[i]
                bank_profit[i] -= savings_interest[i]

                # calculate debt payoff and interest due
                payoff[i] = debt[i] * nbdr
                interest[i] = debt[i] * pbi

                bank_payoff[i] = bank_debt[i] * pbdr
                bank_interest[i] = bank_debt[i] * ecbi

                # pay non bank debts and interests. First clear newly created money
                if new_im[i] > payoff[i]:
                    new_im[i] -= payoff[i]
                else:
                    im1[i] += payoff[i] - new_im[i]
                    new_im[i] = 0

                im2[i] -= payoff[i] + interest[i]
                im1[i] += interest[i]
                debt[i] -= payoff[i]
                debt[i] = max(0.0, debt[i]) # avoid debt going negative due to rounding

                bank_profit[i] += interest[i] - bank_payoff[i] - bank_interest[i]

                # pay bank debts and interests, first use om2, then im1. If insufficient, get a new loan
                if om2[i] >= bank_payoff[i] + bank_interest[i]:
                    om2[i] -= bank_payoff[i] + bank_interest[i]
                else:
                    remaining_debt = bank_payoff[i] + bank_interest[i] - om2[i]
                    om2[i] = 0.0
                    if im1[i] >= remaining_debt:
                        im1[i] -= remaining_debt
                    else:
                        remaining_debt -= im1[i]
                        im1[i] = 0.0
                        bank_debt[i] += remaining_debt

                om1[i] += bank_interest[i]
                bank_debt[i] -= bank_payoff[i]
                bank_debt[i] = max(0.0, bank_debt[i]) # avoid bank debt going negative due to rounding

                # inject QE
                if qe_spending != QE_FIXED:
                    qe[i] = qe_relative * debt[i]

                im1[i] += qe[i] * (1 - qe_trickle)
                im2[i] += qe[i] * qe_trickle

                if (qe_profit):
                    bank_profit[i] += qe[i] * (1 - qe_trickle)

                #bank spending
                if spending_mode == FIXED:
                    # spend the fixed amount if possible, otherwise spend all of im1
                    if im1[i] >= bank_fixed[i]:
                        bank_spending[i] = bank_fixed[i]
                    else:
                        bank_spending[i] = im1[i]
                elif spending_mode == PROFIT_PERCENTAGE:
                    if bank_profit[i] >= 0.0:
                        bank_spending[i] = pp * bank_profit[i]
                    else: # profit can be negative
                        bank_spending[i] = 0,0
                else: # spending mode == CAPITAL_PERCENTAGE
                    bank_spending[i] = cp * im1[i]

                if no_loss:
                    bank_spending[i] = min(bank_spending[i], (1 - min_profit) * bank_profit[i])

                if bank_spending[i] + im2[i] > target_im2: #spending would increase ima above desired amount
                    bank_spending[i] = max(0.0, target_im2 - im2[i])

                im1[i] -= bank_spending[i]
                im2[i] += bank_spending[i]
                bank_profit[i] -= bank_spending[i]

                # grow economy through lending if needed
                lending[i] = max(0.0, target_im2 - im2[i])

                if lending[i] > 0.0:
                    im2[i] += lending[i]
                    debt[i] += lending[i]
                    create_im = lending[i] * nmr
                    min_desired_reserve = min_bank_reserve * debt[i]

                    # check im1 reserve
                    if im1[i] - lending[i] + create_im < min_desired_reserve:
                        if im1[i] >= min_desired_reserve:
                            create_im += lending[i] - create_im - im1[i] + min_desired_reserve
                        else:
                            create_im = lending[i]

                    im1[i] -= lending[i] - create_im
                    new_im[i] += create_im

                # update om in accordance to mr
                min_reserve = mr * debt[i]

                if om2[i] + im1[i] < min_reserve:
                    reserve_need = min_reserve - om2[i] - im1[i]
                    om_growth.append(max(0.0, reserve_need))

                    om1[i] -= reserve_need
                    om2[i] += reserve_need
                    bank_debt[i] += reserve_need
                else:
                    om_growth.append(0.0)

                # calculate percentages
                im_total = im1[i] + im2[i]
                lending_percentage_im2 = lending[i] * 100 / im2[i]
                lending_percentage_im_total = lending[i] * 100 / im_total

                im1_percentage_im_total = im1[i] * 100 / im_total
                im2_percentage_im_total = im2[i] * 100 / im_total

                savings_interest_percentage_im2 = savings_interest[i] * 100 / im2[i]
                savings_interest_percentage_im_total = savings_interest[i] * 100 / im_total

                debt_percentage_im2 = debt[i] * 100 / im2[i]
                debt_percentage_im_total = debt[i] * 100 / im_total

                created_percentage_im2 = new_im[i] * 100 / im2[i]
                created_percentage_im_total = new_im[i] * 100 / im_total

                f.write(f'{deflate(om1[i], i):.2f},{deflate(om2[i], i):.2f},{deflate(om1[i] + om2[i], i):.2f},{deflate(om1[1] + om2[i], i) - deflate(om1[i - 1] + om2[i - 1], i - 1):.2f},\
                        {deflate(qe[i], i):.2f},{deflate(qe_trickle * qe[i], i):.2f},\
                        {deflate(bank_spending[i], i):.2f},{deflate(bank_profit[i], i):.2f},{bank_debt[i]:.2f},{bank_payoff[i]:.2f},{bank_interest[i]:.2f},\
                        {deflate(im1[i], i):.2f},{deflate(im2[i], i):.2f},{deflate(savings_interest[i], i):.2f},{deflate(new_im[i], i):.2f},{deflate(debt[i], i):.2f},{deflate(payoff[i], i):.2f},{deflate(interest[i], i):.2f},\
                        {deflate(im2[i], i) - deflate(im2[i - 1], i - 1):.2f},{deflate(lending[i], i):.2f},{deflate(im1[i] + im2[i], i):.2f},\
                        {lending_percentage_im2:.2f},{lending_percentage_im_total:.2f},\
                        {im1_percentage_im_total:.2f},{im2_percentage_im_total:.2f},\
                        {savings_interest_percentage_im2:.2f},{savings_interest_percentage_im_total:.2f},\
                        {debt_percentage_im2:.2f},{debt_percentage_im_total:.2f},\
                        {created_percentage_im2:.2f},{created_percentage_im_total:.2f}\n')

                # check whether economy has 'stabilized'
                #if i > 0 \
                #        and (round(lending_percentage_im2[i], 2) == round(lending_percentage_im2[i - 1], 2)\
                #        and round(lending_percentage_im_total[i], 2) == round(lending_percentage_im_total[i - 1], 2)):
                #    break

        print()
        f.close()

def initialize():
    im1.clear()
    im2.clear()
    lending.clear()
    debt.clear()
    payoff.clear()
    interest.clear()
    new_im.clear()

    om1.clear()
    om2.clear()
    bank_profit.clear()
    bank_spending.clear()
    bank_fixed.clear()
    bank_debt.clear()
    bank_payoff.clear()
    bank_interest.clear()

    growth.clear()
    om_growth.clear()

    qe.clear()
    savings_interest.clear()

    im1.append(0.0)
    im2.append(initial_im2)
    lending.append(initial_im2)
    debt.append(initial_im2)
    payoff.append(0.0)
    interest.append(0.0)
    new_im.append(initial_im2)

    reserve = initial_im2 * mr
    om1.append(0.0 - reserve) # reflects om money creation
    om2.append(reserve)
    bank_profit.append(0.0)
    bank_spending.append(0.0)
    bank_fixed.append(initial_fixed_spending)
    bank_debt.append(reserve)
    bank_payoff.append(0.0)
    bank_interest.append(0.0)

    growth.append(0.0)
    om_growth.append(0.0)

    if qe_spending == QE_FIXED:
        qe.append(qe_fixed_initial)
    else:
        qe.append(qe_relative * initial_im2) # initial IM2 = initial debt

    savings_interest.append(0.0)

# only call after deflation has been applied in a cycle
def deflate(num, cycle):
    for i in range(cycle):
       num /= 1 + inflation_rate

    return num

runSimulation()