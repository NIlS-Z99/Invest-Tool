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
SP500_SMA_COLORS = ["red",
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

# Function to calculate Simple Moving Average
def calculate_sma(data, smaPeriod):
    data[f'SMA{smaPeriod}'] = data['Close'].rolling(window=smaPeriod).mean()
    return data
def calculate_sma200(data): return calculate_sma(data, 200)

def calculate_m75(data, smaPeriod):
    data[f'M75_{smaPeriod}'] = data['Close'].rolling(window=smaPeriod).apply(lambda x: np.percentile(x, 75), raw=True)
    return data

# Function to check for warning signals
def check_signals(sp500_data, vix_data, vix_thresh, sma_period):
    # Calculate SMA for VIX
    vix_data = calculate_m75(vix_data, 7)
    vix_data = calculate_m75(vix_data, 14)
    vix_data = calculate_m75(vix_data, 30)

    # Latest VIX value and short period SMA
    latest_vix = vix_data['Close'].iloc[-1].tolist() #[0]
    latest_vix_m75_7 = vix_data['M75_7'].iloc[-1].tolist()
    latest_vix_m75_14 = vix_data['M75_14'].iloc[-1].tolist()
    latest_vix_m75_30 = vix_data['M75_30'].iloc[-1].tolist()
    
    # Calculate SMA200 for S&P 500
    sp500_data = calculate_sma200(sp500_data)

    # Calculate 1 month, 3 month, 1 year and 400 SMA for S&P 500
    sp500_data = calculate_sma(sp500_data, sma_period)
    sp500_data = calculate_sma(sp500_data, 31)  # month sma support
    sp500_data = calculate_sma(sp500_data, 92)  # quarter sma support
    sp500_data = calculate_sma(sp500_data, 150) # three quater 200sma support
    sp500_data = calculate_sma(sp500_data, 365) # year sma support
    

    # Latest S&P 500 price and SMA200
    latest_price = sp500_data['Close'].iloc[-1].tolist() #[0]
    latest_sma200 = sp500_data['SMA200'].iloc[-1].tolist()

    latest_sma50,latest_smaq,latest_sma150 = (0, 0, 0)
    latest_smas,latest_sma_keys = (list(),list())
    for sma in sp500_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            latest_smas.append(sp500_data[sma].iloc[-1].tolist())
            latest_sma_keys.append(sma)
            if '150' in sma: latest_sma150 = sp500_data[sma].iloc[-1].tolist()
            elif '92' in sma: latest_smaq = sp500_data[sma].iloc[-1].tolist()
            elif '50' in sma: latest_sma50 = sp500_data[sma].iloc[-1].tolist()
        
    
    print("\n\n{:24s} {:>9.4f}".format("Latest VIX:",round(latest_vix,4)))
    print("{:24s} {:>9.4f}".format("Latest S&P 500 Price:",round(latest_price,4)))
    print("{:24s} {:>9.4f}".format("Latest SMA50 Diff:",round(latest_price-latest_sma50,4)))
    print("{:24s} {:>9.4f}".format("Latest SMA Quarter Diff:",round(latest_price-latest_smaq,4)))
    print("{:24s} {:>9.4f}".format("Latest SMA150 Diff:",round(latest_price-latest_sma150,4)))
    print("{:24s} {:>9.4f}\n".format("Latest S&P 500 SMA200:",round(latest_sma200,4)))
    
    # Conditions
    high_volatility = (latest_vix > vix_thresh) or (latest_vix_m75_7 > vix_thresh*0.9) or\
        (latest_vix_m75_14 > vix_thresh*0.8) or (latest_vix_m75_30 > vix_thresh*0.75) 
    below_sma200 = latest_price < latest_sma200
    below_sma150 = latest_price < latest_sma150
    below_smaq = latest_price < latest_smaq
    above_smaq = latest_price > latest_smaq
    below_sma50 = latest_price < latest_sma50
    below_sma = [latest_price < latest_sma for latest_sma in latest_smas]
    
    # Decision Logic
    if high_volatility and below_sma200:
        print("WARNING: High volatility and S&P 500 below SMA200. Sell the Amundi Leveraged ETF completely!")
    elif high_volatility:
        print("WARNING: High volatility detected. Stop saving plan! Reduce exposure to leveraged products!")
    elif below_sma200:
        print("WARNING: S&P 500 is below SMA200. Market trend is too bearish. Sell the Amundi Leveraged ETF completely!")
    elif below_sma150:
        print("WARNING: S&P 500 is below SMA150. Market trend is very bearish. Move 50% or at least Gains into ACWI IMI!")
    elif below_smaq:
        print("WARNING: S&P 500 is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into ACWI IMI!")
    elif below_sma50:
        print("WARNING: S&P 500 is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_sma:
        print("Attention: S&P 500 is below SMA for ",np.array(latest_sma_keys)[below_sma]," Consider reducing leveraged position!")
    else:
        print("Market conditions are stable. No immediate action needed.")
    print("\n")
    if above_smaq and below_sma50 and not(high_volatility): print("If previously below SMAq consider adding to your leverage position!")
    print("\n")

def plot_scraped_data(sp500_data, vix_data, vix_thresh, sma_period):
    # Plotting
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot S&P 500 and its SMA200 on the same plot
    ax1.plot(sp500_data.index, sp500_data['Close'], label='S&P 500 Close', color='blue', alpha=0.6)
    scale = np.array(range(int(500*round(min(sp500_data['Close'])/500))-500, int(max(sp500_data['Close']))+500, 500))
    ax1.fill_between(sp500_data.index, np.zeros_like(sp500_data['Close'])+min(scale), sp500_data['Close'],
                     #np.zeros_like(sp500_data['Close',"^GSPC"])+min(sp500_data['Close',"^GSPC"]), 
                     #sp500_data['Close',"^GSPC"], 
                     color='cyan', alpha=0.3)
    count = 0
    for sma in sp500_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            print(sma, "=>", sp500_data[sma])
            ax1.plot(sp500_data.index, sp500_data[sma], label=f'S&P 500 {sma}', color=SP500_SMA_COLORS[count], 
                     linestyle='solid' if '200' in sma else ('dashed' if (str(sma_period) in sma) or \
                                       ('150' in sma) else 'dotted'))
            count += 1
    ax1.set_xlabel('Date')
    ax1.set_ylabel('S&P 500 Index', color='blue')
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
    ax2.fill_between(vix_data.index, np.zeros_like(vix_data['Close'])+min(vix_data['Close']), vix_data['Close'],
                     #np.zeros_like(vix_data['Close',"^VIX"])+min(vix_data['Close',"^VIX"]), 
                     #vix_data['Close',"^VIX"], 
                     color='lime', alpha=0.3)
    #ax2.fill_between(vix_data[vix_data['Close',"^VIX"]>vix_thresh].index, np.zeros_like(vix_data[vix_data['Close',"^VIX"]>vix_thresh]['Close',"^VIX"])+vix_thresh, vix_data[vix_data['Close',"^VIX"]>vix_thresh]['Close',"^VIX"], color='crimson', alpha=0.3)
    ax2.set_ylabel('VIX Index', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.legend(loc='upper center')
    scale = np.array(range(int(5*round(min(vix_data['Close'])/5)), int(max(max(vix_data['Close']),vix_thresh*2+1)), 5))
    scale = np.insert(scale, np.where(scale == 5*(round(vix_thresh/5)+1))[0], vix_thresh)
    ax2.set_yticks(scale)

    # Title and grid
    plt.title('S&P 500 Index and VIX Index (Last 2 Years)')
    #plt.grid(True)
    plt.show()


# Main function
def main(vix_thresh, sma_period):
    # Get data
    vix_data = get_vix_data()
    sp500_data = get_sp500_data()
    
    # Check signals
    check_signals(sp500_data, vix_data, vix_thresh, sma_period)

    # Plot the scraped data
    plot_scraped_data(sp500_data, vix_data, vix_thresh, sma_period)
    
    
# Run the script
if __name__ == "__main__":
    if len(argv)>1: VIX_THRESHOLD = int(argv[1])
    if len(argv)>2: SMA_PERIOD = int(argv[2])
    main(VIX_THRESHOLD,SMA_PERIOD)