import numpy as np

''' Current Portfolio '''
#tick = [USAe,JapH,R_EU,Amum,spgIT,EUm,tdiv,wSC,QuantgMF, R_EM, EM_SC,EM_IMI,QED_AP,CSI300]
pos  = [5256,1904,1439,1416,1167,1086, 801,733.5,730.08,658.95,340.44,233.25,214.78,183.22]   # Positions in Currency
divy = [1.12,2.36,3.75,0.00,0.44,0.00,5.19, 0.00,  1.89,  4.31,  2.34,  2.61,  5.50,  0.00]   # Dividend Yield in %
divCon = np.array(divy)/sum(divy)   # Total Porfolio Dividend Yield Contribution of single Positions

start_pos = pos
total_val = sum(pos)
start_alloc = np.array(pos)/total_val
total_divy = np.sum(start_alloc*divy)
alloc = start_alloc

print("Current Portfolio Value is {:.2f}€".format(total_val))
print("Current Portfolio Yield is {:.2f}%".format(total_divy))
print("This Years' Expected Dividends are {:.2f}€".format(total_val*total_divy/100))
print("Portfolio Allocations:",[round(p/sum(pos)*100,2) for p in pos])


''' Simple Extrapolated Future Portfolio Predcition via Simulation with Expected Parameters '''
## Simulation Parameters
years = 35  # amount of years you expect to execute savingsplan
tax = 26    # in % contains other reductions as well not just tax
taxFreeGain = 1200  # in currency
monthlySavingsRate = 1500  # in currency
save_alloc = np.array([24.0,10.0,10.0,10.0, 8.0, 7.5, 6.0, 5.0, 6.0, 5.0, 2.5, 2.5, 2, 1.5])/100
realisticGrowth = np.array([8,6.5,5,11.5,10,6,7.5,4.5,6.5,7,6,5.5,4,7]) # real 7.4 -> potential pes/bear avg 5.5
expGrowth = np.array([10,8,7,15,12.5,8,9.5,6.5,8,7,8,7.5,4.75,8]) # opt/bull 9.37 -> potential opt/bull avg 11.5  -> sim uses this

print("\n")
DRIP_alloc = (divCon+save_alloc)/2
print("Defensive Portfolio growth estimation = {:.2f}%".format(sum(realisticGrowth*((save_alloc+alloc)/2))))
print("Expect Portfolio to grow {:.2f}%".format(sum(expGrowth*((save_alloc+alloc)/2))))
print("DRIP Allocations:",[round(a*100,2) for a in DRIP_alloc],"\n")
growthFactor = sum(expGrowth*((DRIP_alloc+save_alloc+start_alloc)/3))
afterTaxMult = (100 - tax)/100
ysr = monthlySavingsRate*12
pos = np.array(pos)


## Simulate Growth through Dividends and Gains
counter = 0
for year in range(years):

    ## Simulate Tax on Dividends minus annual tax-free Income
    yearly_div = total_val*total_divy/100
    if yearly_div>taxFreeGain: yearly_div = (yearly_div-taxFreeGain)*afterTaxMult+taxFreeGain

    pos = pos + pos*expGrowth/100 + DRIP_alloc*yearly_div 
    if total_val<(100-growthFactor)*ysr: pos = pos + save_alloc*ysr
    elif counter==0: 
        print("Reached free rolling Snowball-Effect after", year, "years.\n")
        counter += 1
    total_val = sum(pos)
    alloc = np.array(pos)/total_val
    total_divy = np.sum(alloc*divy)  


print("After",years,"years:")
print("Total Portfolio Value is {:.2f}€".format(total_val))
print("Portfolio Yield is {:.2f}%".format(total_divy))
print("Expected Dividends are {:.2f}€".format(total_val*total_divy/100))
print("Portfolio Allocations:",[round(p/sum(pos)*100,2) for p in pos],"\n")

## Retirement Restructuring
print("Retire and sell non-dividend positions for High Yield World ETF:")
## Simulate Tax on Gains
pos = np.array([p if d>0 else ((p-sp-ysr*years*SaAl)*afterTaxMult+sp+ysr*years*SaAl) for d,p,sp,SaAl in zip(divy,pos,start_pos,save_alloc)])
divy = [d if d>0 else 3.5 for d in divy]  # assume sold for high yield etf with 3.5% dividend yield (e.g. vanguard ftse all-world HY) 
total_val = sum(pos)
alloc = np.array(pos)/total_val
total_divy = np.sum(alloc*divy)
print("Total Portfolio Value is {:.2f}€".format(total_val))
print("Portfolio Yield is {:.2f}%".format(total_divy))
print("Expected Dividends are {:.2f}€".format(total_val*total_divy/100))
new_alloc = list() 
hyw_etf = 0
for d,a in zip(divy,alloc):
    if not(d==3.5): new_alloc.append(a)
    else: hyw_etf += a
new_alloc.append(hyw_etf)
print("Portfolio Allocations:",[round(a*100,2) for a in new_alloc],"\n")