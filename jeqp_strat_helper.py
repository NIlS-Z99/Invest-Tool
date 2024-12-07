import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from sys import argv

# On Linux or with different python version the commented out code might be needed!


# Parameters
VXN_THRESHOLD = 33  # Define high volatility as VXN > 33
SMA_PERIOD = 50     # For quarter 200 moving average
TICKER_SMA_COLORS = ["red",
                     "blueviolet",
                     "lightcoral",
                     "plum",
                     "deeppink",
                     "maroon"]
VXN_M75_COLORS = ["gold",
                  "orange",
                  "chocolate"]



# Function to get VXN data
def get_vxn_data():
    vxn = yf.download('^VXN', period='2y', interval='1d')
    return vxn

# Function to get Nasdaq 100 data
def get_nasdaq100_data():
    ndx100 = yf.download('^NDX', period='2y', interval='1d')
    return ndx100

# Function to get NDX Covered Call ETF data
def get_jeqp_data():
    jeqp = yf.download('JEQP.DE', period='2y', interval='1d')
    return jeqp

# Function to calculate Simple Moving Average
def calculate_sma(data, smaPeriod):
    data[f'SMA{smaPeriod}'] = data['Close'].rolling(window=smaPeriod).mean()
    return data
def calculate_sma200(data): return calculate_sma(data, 200)

# Function to calculate Moving 75%-ile
def calculate_m75(data, m75Period):
    data[f'M75_{m75Period}'] = data['Close'].rolling(window=m75Period).apply(lambda x: np.percentile(x, 75), raw=True)
    return data

# Function to check for warning signals
def check_signals(nxd100_data, jeqp_data, vxn_data, vxn_thresh, sma_period):
    '''VXN Routine'''
    # Calculate M75 for VXN
    vxn_data = calculate_m75(vxn_data, 7)  # week m75 support
    vxn_data = calculate_m75(vxn_data, 14) # 14d m75 support
    vxn_data = calculate_m75(vxn_data, 30) # month m75 support

    # Latest VXN value and short period SMA
    latest_vxn = vxn_data['Close'].iloc[-1].tolist() #[0]
    latest_vxn_m75_7 = vxn_data['M75_7'].iloc[-1].tolist()
    latest_vxn_m75_14 = vxn_data['M75_14'].iloc[-1].tolist()
    latest_vxn_m75_30 = vxn_data['M75_30'].iloc[-1].tolist()
    
    '''Nasdaq 100 Routine'''
    # Calculate SMA200 for Nasdaq 100
    nxd100_data = calculate_sma200(nxd100_data)

    # Calculate 1 month, 3 month, 1 year and 150 SMA for Nasdaq 100
    nxd100_data = calculate_sma(nxd100_data, sma_period)
    nxd100_data = calculate_sma(nxd100_data, 31)  # month sma support
    nxd100_data = calculate_sma(nxd100_data, 92)  # quarter sma support
    nxd100_data = calculate_sma(nxd100_data, 150) # three quater 200sma support
    nxd100_data = calculate_sma(nxd100_data, 365) # year sma support
    
    # Latest Nasdaq 100 price and SMA200
    latest_nxd100_price = nxd100_data['Close'].iloc[-1].tolist() #[0]
    latest_nxd100_sma200 = nxd100_data['SMA200'].iloc[-1].tolist()

    latest_nxd100_sma50,latest_nxd100_smaq,latest_nxd100_sma150 = (0, 0, 0)
    latest_nxd100_smas,latest_nxd100_sma_keys = (list(),list())
    for sma in nxd100_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            latest_nxd100_smas.append(nxd100_data[sma].iloc[-1].tolist())
            latest_nxd100_sma_keys.append(sma)
            if '150' in sma: latest_nxd100_sma150 = nxd100_data[sma].iloc[-1].tolist()
            elif '92' in sma: latest_nxd100_smaq = nxd100_data[sma].iloc[-1].tolist()
            elif '50' in sma: latest_nxd100_sma50 = nxd100_data[sma].iloc[-1].tolist()
    
    '''JEQP Routine'''
    # Calculate SMA200 for JEQP
    jeqp_data = calculate_sma200(jeqp_data)

    # Calculate 1 month, 3 month, 1 year and 150 SMA for JEQP
    jeqp_data = calculate_sma(jeqp_data, sma_period)
    jeqp_data = calculate_sma(jeqp_data, 31)  # month sma support
    jeqp_data = calculate_sma(jeqp_data, 92)  # quarter sma support
    jeqp_data = calculate_sma(jeqp_data, 150) # three quater 200sma support
    jeqp_data = calculate_sma(jeqp_data, 365) # year sma support
    
    # Latest JEQP price and SMA500
    latest_jeqp_price = jeqp_data['Close'].iloc[-1].tolist() #[0]
    latest_jeqp_sma200 = jeqp_data['SMA200'].iloc[-1].tolist()

    latest_jeqp_sma50,latest_jeqp_smaq,latest_jeqp_sma150 = (0, 0, 0)
    latest_jeqp_smas,latest_jeqp_sma_keys = (list(),list())
    for sma in jeqp_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            latest_jeqp_smas.append(jeqp_data[sma].iloc[-1].tolist())
            latest_jeqp_sma_keys.append(sma)
            if '150' in sma: latest_jeqp_sma150 = jeqp_data[sma].iloc[-1].tolist()
            elif '92' in sma: latest_jeqp_smaq = jeqp_data[sma].iloc[-1].tolist()
            elif '50' in sma: latest_jeqp_sma50 = jeqp_data[sma].iloc[-1].tolist()
    
    print("\n\n{:37s} {:>10.4f}\n".format("Latest VXN:",round(latest_vxn,4)))
    print("{:37s} {:>10.4f}".format("Latest VXN M75 Week Diff:",round(vxn_thresh-latest_vxn_m75_7,4)))
    print("{:37s} {:>10.4f}".format("Latest VXN M75 Month Diff:",round(vxn_thresh-latest_vxn_m75_7,4)))
    print("-"*48)
    print("{:37s} {:>10.4f}".format("Latest Nasdaq 100 Price:",round(latest_nxd100_price,4)))
    print("{:37s} {:>10.4f}\n".format("Latest Nasdaq 100 SMA200:",round(latest_nxd100_sma200,4)))
    print("{:37s} {:>10.4f}".format("Latest Nasdaq 100 SMA50 Diff:",round(latest_nxd100_price-latest_nxd100_sma50,4)))
    print("{:37s} {:>10.4f}".format("Latest Nasdaq 100 SMA Quarter Diff:",round(latest_nxd100_price-latest_nxd100_smaq,4)))
    print("{:37s} {:>10.4f}".format("Latest Nasdaq 100 SMA150 Diff:",round(latest_nxd100_price-latest_nxd100_sma150,4)))
    print("-"*48)
    print("-"*48)
    print("{:37s} {:>10.4f}".format("Latest JEQP Price:",round(latest_jeqp_price,4)))
    print("{:37s} {:>10.4f}\n".format("Latest JEQP SMA200:",round(latest_jeqp_sma200,4)))
    print("{:37s} {:>10.4f}".format("Latest JEQP SMA50 Diff:",round(latest_jeqp_price-latest_jeqp_sma50,4)))
    print("{:37s} {:>10.4f}".format("Latest JEQP SMA Quarter Diff:",round(latest_jeqp_price-latest_jeqp_smaq,4)))
    print("{:37s} {:>10.4f}\n\n".format("Latest JEQP SMA150 Diff:",round(latest_jeqp_price-latest_jeqp_sma150,4)))
    
    
    # Conditions
    high_volatility = (latest_vxn > vxn_thresh) or (latest_vxn_m75_7 > vxn_thresh*0.9) or\
        (latest_vxn_m75_14 > vxn_thresh*0.8) or (latest_vxn_m75_30 > vxn_thresh*0.75) 
    below_nxd100_sma200 = latest_nxd100_price < latest_nxd100_sma200
    below_nxd100_sma150 = latest_nxd100_price < latest_nxd100_sma150
    below_nxd100_smaq = latest_nxd100_price < latest_nxd100_smaq
    above_nxd100_smaq = latest_nxd100_price > latest_nxd100_smaq
    below_nxd100_sma50 = latest_nxd100_price < latest_nxd100_sma50
    below_nxd100_sma = [latest_nxd100_price < latest_nxd100_sma for latest_nxd100_sma in latest_nxd100_smas]
    below_jeqp_sma200 = latest_jeqp_price < latest_jeqp_sma200
    below_jeqp_sma150 = latest_jeqp_price < latest_jeqp_sma150
    below_jeqp_smaq = latest_jeqp_price < latest_jeqp_smaq
    above_jeqp_smaq = latest_jeqp_price > latest_jeqp_smaq
    below_jeqp_sma50 = latest_jeqp_price < latest_jeqp_sma50
    below_jeqp_sma = [latest_jeqp_price < latest_jeqp_sma for latest_jeqp_sma in latest_jeqp_smas]
    
    # Decision Logic
    if high_volatility and below_nxd100_sma200:
        print("WARNING: High volatility and Nasdaq 100 below SMA200. Sell the NDX covered call ETF completely!")
    elif high_volatility:
        print("WARNING: High volatility detected. Stop saving plan! Reduce exposure to NDX products!")
    elif below_nxd100_sma200:
        print("WARNING: Nasdaq 100 is below SMA200. Market trend is too bearish. Sell the NDX covered call ETF completely!")
    elif below_nxd100_sma150:
        print("WARNING: Nasdaq 100 is below SMA150. Market trend is very bearish. Move 50% or at least Gains into Global All-Cap ESG!")
    elif below_nxd100_smaq:
        print("WARNING: Nasdaq 100 is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into JGPI!")
    elif below_nxd100_sma50:
        print("WARNING: Nasdaq 100 is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_nxd100_sma:
        print("Attention: Nasdaq 100 is below SMA for ",np.array(latest_nxd100_sma_keys)[below_nxd100_sma]," Consider reducing covered call position!")
    elif high_volatility and below_jeqp_sma200:
        print("WARNING: High volatility and JEQP below SMA200. Reduce exposure to NDX products!")
    elif below_jeqp_sma200:
        print("WARNING: JEQP is below SMA200. Market trend is too bearish. Sell the NDX covered call ETF completely!")
    elif below_jeqp_sma150:
        print("WARNING: JEQP is below SMA150. Market trend is very bearish. Move 50% or at least Gains into Global All-Cap ESG!")
    elif below_jeqp_smaq:
        print("WARNING: JEQP is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into JGPI!")
    elif below_jeqp_sma50:
        print("WARNING: JEQP is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_jeqp_sma:
        print("Attention: JEQP is below SMA for ",np.array(latest_jeqp_sma_keys)[below_jeqp_sma]," Consider reducing covered call position!")
    else:
        print("Market conditions are stable. No immediate action needed.")
    print("\n")
    if above_nxd100_smaq and below_nxd100_sma50 and not(high_volatility): print("If previously below Nasdaq 100 SMAq consider adding to your covered call position!")
    elif above_jeqp_smaq and below_jeqp_sma50 and not(high_volatility): print("If previously below Nasdaq 100 SMAq consider adding to your covered call position!")
    print("\n")

def plot_scraped_data(ticker_data, vxn_data, vxn_thresh, sma_period, ticker_name): # ticker="^NDX"):
    # Plotting
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot Ticker and its SMA200 on the same plot
    ax1.plot(ticker_data.index, ticker_data['Close'], label=f'{ticker_name} Close', color='blue', alpha=0.6)
    adjust_factor = int(((min(ticker_data['Close'])*0.1)//250 + 1)*250 if (min(ticker_data['Close'])*0.1)>100 else (
        ((min(ticker_data['Close'])*0.1)//25 + 1)*25 if (min(ticker_data['Close'])*0.1)>10 else ((min(ticker_data['Close'])*0.1)//2.5 + 1)*2.5))
    scale = np.array(range(int(adjust_factor*round(min(ticker_data['Close'])/adjust_factor))-adjust_factor, int(max(ticker_data['Close']))+adjust_factor, adjust_factor))
    ax1.fill_between(ticker_data.index, np.zeros_like(ticker_data['Close'])+min(scale), ticker_data['Close'],
                     #np.zeros_like(ticker_data['Close',ticker])+min(scale), 
                     #ticker_data['Close',ticker], 
                     color='cyan', alpha=0.3)
    count = 0
    for sma in ticker_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            ax1.plot(ticker_data.index, ticker_data[sma], label=f'{ticker_name} {sma}', color=TICKER_SMA_COLORS[count], 
                     linestyle='solid' if '200' in sma else ('dashed' if (str(sma_period) in sma) or \
                     ('150' in sma) else 'dotted'))
            count += 1
    ax1.set_xlabel('Date')
    ax1.set_ylabel(f'{ticker_name} Index', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_yticks(scale)
    ax1.legend(loc='upper left')

    # Create a second y-axis for VXN
    ax2 = ax1.twinx()
    ax2.plot(vxn_data.index, vxn_data['Close'], label='VXN Close', color='darkgreen', alpha=0.6)
    count = 0
    for m75 in vxn_data.columns: #.get_level_values('Price'):
        if 'M75_' in m75: 
            ax2.plot(vxn_data.index, vxn_data[m75], label=f'VXN {m75}', color=VXN_M75_COLORS[count], linestyle='--')
            count += 1
    ax2.axhline(y=vxn_thresh, color='black', linestyle='-.', label='VXN Threshold')
    scale = np.array(range(int(5*round(min(vxn_data['Close'])/5)), int(max(max(vxn_data['Close']),round(vxn_thresh*1.75)+1)), 5))
    scale = np.insert(scale, np.where(scale == 5*(round(vxn_thresh/5)+1))[0], vxn_thresh)
    ax2.fill_between(vxn_data.index, np.zeros_like(vxn_data['Close'])+min(scale), vxn_data['Close'],
                     #np.zeros_like(vxn_data['Close',"^VXN"])+min(scale), 
                     #vxn_data['Close',"^VXN"], 
                     color='lime', alpha=0.3)
    #ax2.fill_between(vxn_data[vxn_data['Close',"^VXN"]>vxn_thresh].index, np.zeros_like(vxn_data[vxn_data['Close',"^VXN"]>vxn_thresh]['Close',"^VXN"])+vxn_thresh, vxn_data[vxn_data['Close',"^VXN"]>vxn_thresh]['Close',"^VXN"], color='crimson', alpha=0.3)
    ax2.set_ylabel('VXN Index', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.legend(loc='upper center')
    ax2.set_yticks(scale)

    plt.title(f'{ticker_name} Index and VXN Index (Last 2 Years)')
    plt.show()


# Main function
def main(vxn_thresh, sma_period):
    # Get data
    vxn_data = get_vxn_data()
    nxd100_data = get_nasdaq100_data()
    jeqp_data = get_jeqp_data()
    
    # Check signals
    check_signals(nxd100_data, jeqp_data, vxn_data, vxn_thresh, sma_period)

    # Plot the scraped data
    plot_scraped_data(nxd100_data, vxn_data, vxn_thresh, sma_period, ticker_name='Nasdaq 100')  #, ticker="^NDX")
    plot_scraped_data(jeqp_data, vxn_data, vxn_thresh, sma_period, ticker_name='JEQP')  #, ticker="JEQP.DE")
    
    
# Run the script
if __name__ == "__main__":
    if len(argv)>1: VXN_THRESHOLD = int(argv[1])
    if len(argv)>2: SMA_PERIOD = int(argv[2])
    main(VXN_THRESHOLD,SMA_PERIOD)