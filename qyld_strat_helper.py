import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from sys import argv

# On Linux or with different python version the commented out code might be needed!


# Parameters
VNX_THRESHOLD = 33  # Define high volatility as VNX > 33
SMA_PERIOD = 50     # For quarter 200 moving average
TICKER_SMA_COLORS = ["red",
                     "blueviolet",
                     "lightcoral",
                     "plum",
                     "deeppink",
                     "maroon"]
VNX_M75_COLORS = ["gold",
                  "orange",
                  "chocolate"]



# Function to get VXN data
def get_vnx_data():
    vnx = yf.download('^VXN', period='2y', interval='1d')
    return vnx

# Function to get Nasdaq 100 data
def get_nasdaq100_data():
    ndx100 = yf.download('^NDX', period='2y', interval='1d')
    return ndx100

# Function to get NDX Covered Call ETF data
def get_qyld_data():
    qyld = yf.download('QYLD', period='2y', interval='1d')
    return qyld

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
def check_signals(nxd100_data, qyld_data, vnx_data, vnx_thresh, sma_period):
    '''VNX Routine'''
    # Calculate M75 for VNX
    vnx_data = calculate_m75(vnx_data, 7)  # week m75 support
    vnx_data = calculate_m75(vnx_data, 14) # 14d m75 support
    vnx_data = calculate_m75(vnx_data, 30) # month m75 support

    # Latest VNX value and short period SMA
    latest_vnx = vnx_data['Close'].iloc[-1].tolist() #[0]
    latest_vnx_m75_7 = vnx_data['M75_7'].iloc[-1].tolist()
    latest_vnx_m75_14 = vnx_data['M75_14'].iloc[-1].tolist()
    latest_vnx_m75_30 = vnx_data['M75_30'].iloc[-1].tolist()
    
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
    
    '''QYLD Routine'''
    # Calculate SMA200 for AMUMBO
    qyld_data = calculate_sma200(qyld_data)

    # Calculate 1 month, 3 month, 1 year and 150 SMA for AMUMBO
    qyld_data = calculate_sma(qyld_data, sma_period)
    qyld_data = calculate_sma(qyld_data, 31)  # month sma support
    qyld_data = calculate_sma(qyld_data, 92)  # quarter sma support
    qyld_data = calculate_sma(qyld_data, 150) # three quater 200sma support
    qyld_data = calculate_sma(qyld_data, 365) # year sma support
    
    # Latest AMUMBO price and SMA500
    latest_qyld_price = qyld_data['Close'].iloc[-1].tolist() #[0]
    latest_qyld_sma200 = qyld_data['SMA200'].iloc[-1].tolist()

    latest_qyld_sma50,latest_qyld_smaq,latest_qyld_sma150 = (0, 0, 0)
    latest_qyld_smas,latest_qyld_sma_keys = (list(),list())
    for sma in qyld_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            latest_qyld_smas.append(qyld_data[sma].iloc[-1].tolist())
            latest_qyld_sma_keys.append(sma)
            if '150' in sma: latest_qyld_sma150 = qyld_data[sma].iloc[-1].tolist()
            elif '92' in sma: latest_qyld_smaq = qyld_data[sma].iloc[-1].tolist()
            elif '50' in sma: latest_qyld_sma50 = qyld_data[sma].iloc[-1].tolist()
    
    print("\n\n{:34s} {:>9.4f}\n".format("Latest VNX:",round(latest_vnx,4)))
    print("{:34s} {:>9.4f}".format("Latest VNX M75 Week Diff:",round(vnx_thresh-latest_vnx_m75_7,4)))
    print("{:34s} {:>9.4f}".format("Latest VNX M75 Month Diff:",round(vnx_thresh-latest_vnx_m75_7,4)))
    print("-"*41)
    print("{:34s} {:>9.4f}".format("Latest Nasdaq 100 Price:",round(latest_nxd100_price,4)))
    print("{:34s} {:>9.4f}\n".format("Latest Nasdaq 100 SMA200:",round(latest_nxd100_sma200,4)))
    print("{:34s} {:>9.4f}".format("Latest Nasdaq 100 SMA50 Diff:",round(latest_nxd100_price-latest_nxd100_sma50,4)))
    print("{:34s} {:>9.4f}".format("Latest Nasdaq 100 SMA Quarter Diff:",round(latest_nxd100_price-latest_nxd100_smaq,4)))
    print("{:34s} {:>9.4f}".format("Latest Nasdaq 100 SMA150 Diff:",round(latest_nxd100_price-latest_nxd100_sma150,4)))
    print("-"*41)
    print("-"*41)
    print("{:34s} {:>9.4f}".format("Latest QYLD Price:",round(latest_qyld_price,4)))
    print("{:34s} {:>9.4f}\n".format("Latest QYLD SMA200:",round(latest_qyld_sma200,4)))
    print("{:34s} {:>9.4f}".format("Latest QYLD SMA50 Diff:",round(latest_qyld_price-latest_qyld_sma50,4)))
    print("{:34s} {:>9.4f}".format("Latest QYLD SMA Quarter Diff:",round(latest_qyld_price-latest_qyld_smaq,4)))
    print("{:34s} {:>9.4f}\n\n".format("Latest QYLD SMA150 Diff:",round(latest_qyld_price-latest_qyld_sma150,4)))
    
    
    # Conditions
    high_volatility = (latest_vnx > vnx_thresh) or (latest_vnx_m75_7 > vnx_thresh*0.9) or\
        (latest_vnx_m75_14 > vnx_thresh*0.8) or (latest_vnx_m75_30 > vnx_thresh*0.75) 
    below_nxd100_sma200 = latest_nxd100_price < latest_nxd100_sma200
    below_nxd100_sma150 = latest_nxd100_price < latest_nxd100_sma150
    below_nxd100_smaq = latest_nxd100_price < latest_nxd100_smaq
    above_nxd100_smaq = latest_nxd100_price > latest_nxd100_smaq
    below_nxd100_sma50 = latest_nxd100_price < latest_nxd100_sma50
    below_nxd100_sma = [latest_nxd100_price < latest_nxd100_sma for latest_nxd100_sma in latest_nxd100_smas]
    below_qyld_sma200 = latest_qyld_price < latest_qyld_sma200
    below_qyld_sma150 = latest_qyld_price < latest_qyld_sma150
    below_qyld_smaq = latest_qyld_price < latest_qyld_smaq
    above_qyld_smaq = latest_qyld_price > latest_qyld_smaq
    below_qyld_sma50 = latest_qyld_price < latest_qyld_sma50
    below_qyld_sma = [latest_qyld_price < latest_qyld_sma for latest_qyld_sma in latest_qyld_smas]
    
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
        print("WARNING: Nasdaq 100 is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into TDIV!")
    elif below_nxd100_sma50:
        print("WARNING: Nasdaq 100 is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_nxd100_sma:
        print("Attention: Nasdaq 100 is below SMA for ",np.array(latest_nxd100_sma_keys)[below_nxd100_sma]," Consider reducing covered call position!")
    elif high_volatility and below_qyld_sma200:
        print("WARNING: High volatility and QYLD below SMA200. Reduce exposure to NDX products!")
    elif below_qyld_sma200:
        print("WARNING: QYLD is below SMA200. Market trend is too bearish. Sell the NDX covered call ETF completely!")
    elif below_qyld_sma150:
        print("WARNING: QYLD is below SMA150. Market trend is very bearish. Move 50% or at least Gains into Global All-Cap ESG!")
    elif below_qyld_smaq:
        print("WARNING: QYLD is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into TDIV!")
    elif below_qyld_sma50:
        print("WARNING: QYLD is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_qyld_sma:
        print("Attention: QYLD is below SMA for ",np.array(latest_qyld_sma_keys)[below_qyld_sma]," Consider reducing covered call position!")
    else:
        print("Market conditions are stable. No immediate action needed.")
    print("\n")
    if above_nxd100_smaq and below_nxd100_sma50 and not(high_volatility): print("If previously below Nasdaq 100 SMAq consider adding to your covered call position!")
    elif above_qyld_smaq and below_qyld_sma50 and not(high_volatility): print("If previously below Nasdaq 100 SMAq consider adding to your covered call position!")
    print("\n")

def plot_scraped_data(ticker_data, vnx_data, vnx_thresh, sma_period, ticker_name): # ticker="^GSPC"):
    # Plotting
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot Ticker and its SMA200 on the same plot
    ax1.plot(ticker_data.index, ticker_data['Close'], label=f'{ticker_name} Close', color='blue', alpha=0.6)
    adjust_factor = int(((min(ticker_data['Close'])*0.1)//500 + 1)*500 if (min(ticker_data['Close'])*0.1)>100 else (
        ((min(ticker_data['Close'])*0.1)//50 + 1)*50 if (min(ticker_data['Close'])*0.1)>10 else ((min(ticker_data['Close'])*0.1)//5 + 1)*5))
    scale = np.array(range(int(adjust_factor*round(min(ticker_data['Close'])/adjust_factor))-adjust_factor, int(max(ticker_data['Close']))+adjust_factor, adjust_factor))
    ax1.fill_between(ticker_data.index, np.zeros_like(ticker_data['Close'])+min(scale), ticker_data['Close'],
                     #np.zeros_like(ticker_data['Close',ticker])+min(ticker_data['Close',ticker]), 
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

    # Create a second y-axis for VNX
    ax2 = ax1.twinx()
    ax2.plot(vnx_data.index, vnx_data['Close'], label='VNX Close', color='darkgreen', alpha=0.6)
    count = 0
    for m75 in vnx_data.columns: #.get_level_values('Price'):
        if 'M75_' in m75: 
            ax2.plot(vnx_data.index, vnx_data[m75], label=f'VNX {m75}', color=VNX_M75_COLORS[count], linestyle='--')
            count += 1
    ax2.axhline(y=vnx_thresh, color='black', linestyle='-.', label='VNX Threshold')
    scale = np.array(range(int(5*round(min(vnx_data['Close'])/5)), int(max(max(vnx_data['Close']),vnx_thresh*2+1)), 5))
    scale = np.insert(scale, np.where(scale == 5*(round(vnx_thresh/5)+1))[0], vnx_thresh)
    ax2.fill_between(vnx_data.index, np.zeros_like(vnx_data['Close'])+min(scale), vnx_data['Close'],
                     #np.zeros_like(vnx_data['Close',"^VNX"])+min(vnx_data['Close',"^VNX"]), 
                     #vnx_data['Close',"^VNX"], 
                     color='lime', alpha=0.3)
    #ax2.fill_between(vnx_data[vnx_data['Close',"^VNX"]>vnx_thresh].index, np.zeros_like(vnx_data[vnx_data['Close',"^VNX"]>vnx_thresh]['Close',"^VNX"])+vnx_thresh, vnx_data[vnx_data['Close',"^VNX"]>vnx_thresh]['Close',"^VNX"], color='crimson', alpha=0.3)
    ax2.set_ylabel('VNX Index', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.legend(loc='upper center')
    ax2.set_yticks(scale)

    # Title and grid
    plt.title(f'{ticker_name} Index and VNX Index (Last 2 Years)')
    #plt.grid(True)
    plt.show()


# Main function
def main(vnx_thresh, sma_period):
    # Get data
    vnx_data = get_vnx_data()
    nxd100_data = get_nasdaq100_data()
    qyld_data = get_qyld_data()
    
    # Check signals
    check_signals(nxd100_data, qyld_data, vnx_data, vnx_thresh, sma_period)

    # Plot the scraped data
    plot_scraped_data(nxd100_data, vnx_data, vnx_thresh, sma_period, ticker_name='Nasdaq 100')  #, ticker="^GSPC")
    plot_scraped_data(qyld_data, vnx_data, vnx_thresh, sma_period, ticker_name='QYLD')  #, ticker="18MF.DE")
    
    
# Run the script
if __name__ == "__main__":
    if len(argv)>1: VNX_THRESHOLD = int(argv[1])
    if len(argv)>2: SMA_PERIOD = int(argv[2])
    main(VNX_THRESHOLD,SMA_PERIOD)