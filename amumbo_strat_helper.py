import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from sys import argv

# On Linux or with different python version the commented out code might be needed!


# Parameters
VIX_THRESHOLD = 28  # Define high volatility as VIX > 28
SMA_PERIOD = 50     # For quarter 200 moving average
TICKER_SMA_COLORS = ["red",
                     "blueviolet",
                     "lightcoral",
                     "plum",
                     "deeppink",
                     "maroon"]
VIX_M75_COLORS = ["gold",
                  "orange",
                  "chocolate"]



# Function to get VIX data
def get_vix_data():
    vix = yf.download('^VIX', period='2y', interval='1d')
    return vix

# Function to get S&P 500 data
def get_sp500_data():
    sp500 = yf.download('^GSPC', period='2y', interval='1d')
    return sp500

# Function to get Amumbo data
def get_amumbo_data():
    amumbo = yf.download('18MF.DE', period='2y', interval='1d')
    return amumbo

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
def check_signals(sp500_data, amumbo_data, vix_data, vix_thresh, sma_period):
    '''VIX Routine'''
    # Calculate M75 for VIX
    vix_data = calculate_m75(vix_data, 7)  # week m75 support
    vix_data = calculate_m75(vix_data, 14) # 14d m75 support
    vix_data = calculate_m75(vix_data, 30) # month m75 support

    # Latest VIX value and short period SMA
    latest_vix = vix_data['Close'].iloc[-1].tolist() #[0]
    latest_vix_m75_7 = vix_data['M75_7'].iloc[-1].tolist()
    latest_vix_m75_14 = vix_data['M75_14'].iloc[-1].tolist()
    latest_vix_m75_30 = vix_data['M75_30'].iloc[-1].tolist()
    
    '''S&P 500 Routine'''
    # Calculate SMA200 for S&P 500
    sp500_data = calculate_sma200(sp500_data)

    # Calculate 1 month, 3 month, 1 year and 150 SMA for S&P 500
    sp500_data = calculate_sma(sp500_data, sma_period)
    sp500_data = calculate_sma(sp500_data, 31)  # month sma support
    sp500_data = calculate_sma(sp500_data, 92)  # quarter sma support
    sp500_data = calculate_sma(sp500_data, 150) # three quater 200sma support
    sp500_data = calculate_sma(sp500_data, 365) # year sma support
    
    # Latest S&P 500 price and SMA200
    latest_sp500_price = sp500_data['Close'].iloc[-1].tolist() #[0]
    latest_sp500_sma200 = sp500_data['SMA200'].iloc[-1].tolist()

    latest_sp500_sma50,latest_sp500_smaq,latest_sp500_sma150 = (0, 0, 0)
    latest_sp500_smas,latest_sp500_sma_keys = (list(),list())
    for sma in sp500_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            latest_sp500_smas.append(sp500_data[sma].iloc[-1].tolist())
            latest_sp500_sma_keys.append(sma)
            if '150' in sma: latest_sp500_sma150 = sp500_data[sma].iloc[-1].tolist()
            elif '92' in sma: latest_sp500_smaq = sp500_data[sma].iloc[-1].tolist()
            elif '50' in sma: latest_sp500_sma50 = sp500_data[sma].iloc[-1].tolist()
    
    '''Amumbo Routine'''
    # Calculate SMA200 for AMUMBO
    amumbo_data = calculate_sma200(amumbo_data)

    # Calculate 1 month, 3 month, 1 year and 150 SMA for AMUMBO
    amumbo_data = calculate_sma(amumbo_data, sma_period)
    amumbo_data = calculate_sma(amumbo_data, 31)  # month sma support
    amumbo_data = calculate_sma(amumbo_data, 92)  # quarter sma support
    amumbo_data = calculate_sma(amumbo_data, 150) # three quater 200sma support
    amumbo_data = calculate_sma(amumbo_data, 365) # year sma support
    
    # Latest AMUMBO price and SMA500
    latest_amumbo_price = amumbo_data['Close'].iloc[-1].tolist() #[0]
    latest_amumbo_sma200 = amumbo_data['SMA200'].iloc[-1].tolist()

    latest_amumbo_sma50,latest_amumbo_smaq,latest_amumbo_sma150 = (0, 0, 0)
    latest_amumbo_smas,latest_amumbo_sma_keys = (list(),list())
    for sma in amumbo_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            latest_amumbo_smas.append(amumbo_data[sma].iloc[-1].tolist())
            latest_amumbo_sma_keys.append(sma)
            if '150' in sma: latest_amumbo_sma150 = amumbo_data[sma].iloc[-1].tolist()
            elif '92' in sma: latest_amumbo_smaq = amumbo_data[sma].iloc[-1].tolist()
            elif '50' in sma: latest_amumbo_sma50 = amumbo_data[sma].iloc[-1].tolist()
    
    print("\n\n{:34s} {:>9.4f}\n".format("Latest VIX:",round(latest_vix,4)))
    print("{:34s} {:>9.4f}".format("Latest VIX M75 Week Diff:",round(vix_thresh-latest_vix_m75_7,4)))
    print("{:34s} {:>9.4f}".format("Latest VIX M75 Month Diff:",round(vix_thresh-latest_vix_m75_7,4)))
    print("-"*41)
    print("{:34s} {:>9.4f}".format("Latest S&P 500 Price:",round(latest_sp500_price,4)))
    print("{:34s} {:>9.4f}\n".format("Latest S&P 500 SMA200:",round(latest_sp500_sma200,4)))
    print("{:34s} {:>9.4f}".format("Latest S&P 500 SMA50 Diff:",round(latest_sp500_price-latest_sp500_sma50,4)))
    print("{:34s} {:>9.4f}".format("Latest S&P 500 SMA Quarter Diff:",round(latest_sp500_price-latest_sp500_smaq,4)))
    print("{:34s} {:>9.4f}".format("Latest S&P 500 SMA150 Diff:",round(latest_sp500_price-latest_sp500_sma150,4)))
    print("-"*41)
    print("-"*41)
    print("{:34s} {:>9.4f}".format("Latest Amumbo Price:",round(latest_amumbo_price,4)))
    print("{:34s} {:>9.4f}\n".format("Latest Amumbo SMA200:",round(latest_amumbo_sma200,4)))
    print("{:34s} {:>9.4f}".format("Latest Amumbo SMA50 Diff:",round(latest_amumbo_price-latest_amumbo_sma50,4)))
    print("{:34s} {:>9.4f}".format("Latest Amumbo SMA Quarter Diff:",round(latest_amumbo_price-latest_amumbo_smaq,4)))
    print("{:34s} {:>9.4f}\n\n".format("Latest Amumbo SMA150 Diff:",round(latest_amumbo_price-latest_amumbo_sma150,4)))
    
    
    # Conditions
    high_volatility = (latest_vix > vix_thresh) or (latest_vix_m75_7 > vix_thresh*0.9) or\
        (latest_vix_m75_14 > vix_thresh*0.8) or (latest_vix_m75_30 > vix_thresh*0.75) 
    below_sp500_sma200 = latest_sp500_price < latest_sp500_sma200
    below_sp500_sma150 = latest_sp500_price < latest_sp500_sma150
    below_sp500_smaq = latest_sp500_price < latest_sp500_smaq
    above_sp500_smaq = latest_sp500_price > latest_sp500_smaq
    below_sp500_sma50 = latest_sp500_price < latest_sp500_sma50
    below_sp500_sma = [latest_sp500_price < latest_sp500_sma for latest_sp500_sma in latest_sp500_smas]
    below_amumbo_sma200 = latest_amumbo_price < latest_amumbo_sma200
    below_amumbo_sma150 = latest_amumbo_price < latest_amumbo_sma150
    below_amumbo_smaq = latest_amumbo_price < latest_amumbo_smaq
    above_amumbo_smaq = latest_amumbo_price > latest_amumbo_smaq
    below_amumbo_sma50 = latest_amumbo_price < latest_amumbo_sma50
    below_amumbo_sma = [latest_amumbo_price < latest_amumbo_sma for latest_amumbo_sma in latest_amumbo_smas]
    
    # Decision Logic
    if high_volatility and below_sp500_sma200:
        print("WARNING: High volatility and S&P 500 below SMA200. Sell the Amundi Leveraged ETF completely!")
    elif high_volatility:
        print("WARNING: High volatility detected. Stop saving plan! Reduce exposure to leveraged products!")
    elif below_sp500_sma200:
        print("WARNING: S&P 500 is below SMA200. Market trend is too bearish. Sell the Amundi Leveraged ETF completely!")
    elif below_sp500_sma150:
        print("WARNING: S&P 500 is below SMA150. Market trend is very bearish. Move 50% or at least Gains into Global All-Cap ESG!")
    elif below_sp500_smaq:
        print("WARNING: S&P 500 is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into USA ESG!")
    elif below_sp500_sma50:
        print("WARNING: S&P 500 is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_sp500_sma:
        print("Attention: S&P 500 is below SMA for ",np.array(latest_sp500_sma_keys)[below_sp500_sma]," Consider reducing leveraged position!")
    elif high_volatility and below_amumbo_sma200:
        print("WARNING: High volatility and Amumbo below SMA200. Sell the Amundi Leveraged ETF completely!")
    elif below_amumbo_sma200:
        print("WARNING: Amumbo is below SMA200. Market trend is too bearish. Sell the Amundi Leveraged ETF completely!")
    elif below_amumbo_sma150:
        print("WARNING: Amumbo is below SMA150. Market trend is very bearish. Move 50% or at least Gains into ACWI IMI!")
    elif below_amumbo_smaq:
        print("WARNING: Amumbo is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into ACWI IMI!")
    elif below_amumbo_sma50:
        print("WARNING: Amumbo is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_amumbo_sma:
        print("Attention: Amumbo is below SMA for ",np.array(latest_amumbo_sma_keys)[below_amumbo_sma]," Consider reducing leveraged position!")
    else:
        print("Market conditions are stable. No immediate action needed.")
    print("\n")
    if above_sp500_smaq and below_sp500_sma50 and not(high_volatility): print("If previously below S&P 500 SMAq consider adding to your leverage position!")
    elif above_amumbo_smaq and below_amumbo_sma50 and not(high_volatility): print("If previously below S&P 500 SMAq consider adding to your leverage position!")
    print("\n")

def plot_scraped_data(ticker_data, vix_data, vix_thresh, sma_period, ticker_name): # ticker="^GSPC"):
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

    # Create a second y-axis for VIX
    ax2 = ax1.twinx()
    ax2.plot(vix_data.index, vix_data['Close'], label='VIX Close', color='darkgreen', alpha=0.6)
    count = 0
    for m75 in vix_data.columns: #.get_level_values('Price'):
        if 'M75_' in m75: 
            ax2.plot(vix_data.index, vix_data[m75], label=f'VIX {m75}', color=VIX_M75_COLORS[count], linestyle='--')
            count += 1
    ax2.axhline(y=vix_thresh, color='black', linestyle='-.', label='VIX Threshold')
    scale = np.array(range(int(5*round(min(vix_data['Close'])/5)), int(max(max(vix_data['Close']),vix_thresh*2+1)), 5))
    scale = np.insert(scale, np.where(scale == 5*(round(vix_thresh/5)+1))[0], vix_thresh)
    ax2.fill_between(vix_data.index, np.zeros_like(vix_data['Close'])+min(scale), vix_data['Close'],
                     #np.zeros_like(vix_data['Close',"^VIX"])+min(vix_data['Close',"^VIX"]), 
                     #vix_data['Close',"^VIX"], 
                     color='lime', alpha=0.3)
    #ax2.fill_between(vix_data[vix_data['Close',"^VIX"]>vix_thresh].index, np.zeros_like(vix_data[vix_data['Close',"^VIX"]>vix_thresh]['Close',"^VIX"])+vix_thresh, vix_data[vix_data['Close',"^VIX"]>vix_thresh]['Close',"^VIX"], color='crimson', alpha=0.3)
    ax2.set_ylabel('VIX Index', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.legend(loc='upper center')
    ax2.set_yticks(scale)

    # Title and grid
    plt.title(f'{ticker_name} Index and VIX Index (Last 2 Years)')
    #plt.grid(True)
    plt.show()


# Main function
def main(vix_thresh, sma_period):
    # Get data
    vix_data = get_vix_data()
    sp500_data = get_sp500_data()
    amumbo_data = get_amumbo_data()
    
    # Check signals
    check_signals(sp500_data, amumbo_data, vix_data, vix_thresh, sma_period)

    # Plot the scraped data
    plot_scraped_data(sp500_data, vix_data, vix_thresh, sma_period, ticker_name='S&P 500')  #, ticker="^GSPC")
    plot_scraped_data(amumbo_data, vix_data, vix_thresh, sma_period, ticker_name='Amumbo')  #, ticker="18MF.DE")
    
    
# Run the script
if __name__ == "__main__":
    if len(argv)>1: VIX_THRESHOLD = int(argv[1])
    if len(argv)>2: SMA_PERIOD = int(argv[2])
    main(VIX_THRESHOLD,SMA_PERIOD)