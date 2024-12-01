import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from sys import argv

# On Linux or with different python version the commented out code might be needed!


# Parameters
SMA_PERIOD = 50     # For quarter 200 moving average
TICKER_SMA_COLORS = ["red",
                     "blueviolet",
                     "lightcoral",
                     "plum",
                     "deeppink",
                     "maroon"]


# Function to get DAX data
def get_dax_data():
    dax = yf.download('^GDAXI', period='2y', interval='1d')
    return dax

# Function to get LevDAX daily ETF data
def get_lvdx_data():
    lvdx = yf.download('LVDX.DE', period='2y', interval='1d')
    return lvdx

# Function to calculate Simple Moving Average
def calculate_sma(data, smaPeriod):
    data[f'SMA{smaPeriod}'] = data['Close'].rolling(window=smaPeriod).mean()
    return data
def calculate_sma200(data): return calculate_sma(data, 200)


# Function to check for warning signals
def check_signals(dax_data, lvdx_data, sma_period):
    '''DAX Routine'''
    # Calculate SMA200 for DAX
    dax_data = calculate_sma200(dax_data)

    # Calculate 1 month, 3 month, 1 year and 150 SMA for DAX
    dax_data = calculate_sma(dax_data, sma_period)
    dax_data = calculate_sma(dax_data, 31)  # month sma support
    dax_data = calculate_sma(dax_data, 92)  # quarter sma support
    dax_data = calculate_sma(dax_data, 150) # three quater 200sma support
    dax_data = calculate_sma(dax_data, 365) # year sma support
    
    # Latest DAX price and SMA200
    latest_dax_price = dax_data['Close'].iloc[-1].tolist() #[0]
    latest_dax_sma200 = dax_data['SMA200'].iloc[-1].tolist()

    latest_dax_sma50,latest_dax_smaq,latest_dax_sma150 = (0, 0, 0)
    latest_dax_smas,latest_dax_sma_keys = (list(),list())
    for sma in dax_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            latest_dax_smas.append(dax_data[sma].iloc[-1].tolist())
            latest_dax_sma_keys.append(sma)
            if '150' in sma: latest_dax_sma150 = dax_data[sma].iloc[-1].tolist()
            elif '92' in sma: latest_dax_smaq = dax_data[sma].iloc[-1].tolist()
            elif '50' in sma: latest_dax_sma50 = dax_data[sma].iloc[-1].tolist()
    
    '''LevDAX daily Routine'''
    # Calculate SMA200 for LevDAX daily
    lvdx_data = calculate_sma200(lvdx_data)

    # Calculate 1 month, 3 month, 1 year and 150 SMA for LevDAX daily
    lvdx_data = calculate_sma(lvdx_data, sma_period)
    lvdx_data = calculate_sma(lvdx_data, 31)  # month sma support
    lvdx_data = calculate_sma(lvdx_data, 92)  # quarter sma support
    lvdx_data = calculate_sma(lvdx_data, 150) # three quater 200sma support
    lvdx_data = calculate_sma(lvdx_data, 365) # year sma support
    
    # Latest LevDAX daily price and SMA500
    latest_lvdx_price = lvdx_data['Close'].iloc[-1].tolist() #[0]
    latest_lvdx_sma200 = lvdx_data['SMA200'].iloc[-1].tolist()

    latest_lvdx_sma50,latest_lvdx_smaq,latest_lvdx_sma150 = (0, 0, 0)
    latest_lvdx_smas,latest_lvdx_sma_keys = (list(),list())
    for sma in lvdx_data.columns: #.get_level_values('Price'):
        if 'SMA' in sma: 
            latest_lvdx_smas.append(lvdx_data[sma].iloc[-1].tolist())
            latest_lvdx_sma_keys.append(sma)
            if '150' in sma: latest_lvdx_sma150 = lvdx_data[sma].iloc[-1].tolist()
            elif '92' in sma: latest_lvdx_smaq = lvdx_data[sma].iloc[-1].tolist()
            elif '50' in sma: latest_lvdx_sma50 = lvdx_data[sma].iloc[-1].tolist()
    
    print("{:34s} {:>10.4f}".format("Latest DAX Price:",round(latest_dax_price,4)))
    print("{:34s} {:>10.4f}\n".format("Latest DAX SMA200:",round(latest_dax_sma200,4)))
    print("{:34s} {:>10.4f}".format("Latest DAX SMA50 Diff:",round(latest_dax_price-latest_dax_sma50,4)))
    print("{:34s} {:>10.4f}".format("Latest DAX SMA Quarter Diff:",round(latest_dax_price-latest_dax_smaq,4)))
    print("{:34s} {:>10.4f}".format("Latest DAX SMA150 Diff:",round(latest_dax_price-latest_dax_sma150,4)))
    print("-"*45)
    print("-"*45)
    print("{:34s} {:>10.4f}".format("Latest LVDX.DE Price:",round(latest_lvdx_price,4)))
    print("{:34s} {:>10.4f}\n".format("Latest LVDX.DE SMA200:",round(latest_lvdx_sma200,4)))
    print("{:34s} {:>10.4f}".format("Latest LVDX.DE SMA50 Diff:",round(latest_lvdx_price-latest_lvdx_sma50,4)))
    print("{:34s} {:>10.4f}".format("Latest LVDX.DE SMA Quarter Diff:",round(latest_lvdx_price-latest_lvdx_smaq,4)))
    print("{:34s} {:>10.4f}\n\n".format("Latest LVDX.DE SMA150 Diff:",round(latest_lvdx_price-latest_lvdx_sma150,4)))
    
    
    # Conditions
    below_dax_sma200 = latest_dax_price < latest_dax_sma200
    below_dax_sma150 = latest_dax_price < latest_dax_sma150
    below_dax_smaq = latest_dax_price < latest_dax_smaq
    above_dax_smaq = latest_dax_price > latest_dax_smaq
    below_dax_sma50 = latest_dax_price < latest_dax_sma50
    below_dax_sma = [latest_dax_price < latest_dax_sma for latest_dax_sma in latest_dax_smas]
    below_lvdx_sma200 = latest_lvdx_price < latest_lvdx_sma200
    below_lvdx_sma150 = latest_lvdx_price < latest_lvdx_sma150
    below_lvdx_smaq = latest_lvdx_price < latest_lvdx_smaq
    above_lvdx_smaq = latest_lvdx_price > latest_lvdx_smaq
    below_lvdx_sma50 = latest_lvdx_price < latest_lvdx_sma50
    below_lvdx_sma = [latest_lvdx_price < latest_lvdx_sma for latest_lvdx_sma in latest_lvdx_smas]
    
    # Decision Logic
    if below_dax_sma200:
        print("WARNING: DAX is below SMA200. Market trend is too bearish. Sell the LevDax daily ETF completely!")
    elif below_dax_sma150:
        print("WARNING: DAX is below SMA150. Market trend is very bearish. Move 50% or at least Gains into Global All-Cap ESG!")
    elif below_dax_smaq:
        print("WARNING: DAX is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into EU All-Cap ESG!")
    elif below_dax_sma50:
        print("WARNING: DAX is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_dax_sma:
        print("Attention: DAX is below SMA for ",np.array(latest_dax_sma_keys)[below_dax_sma]," Consider reducing leveraged position!")
    elif below_lvdx_sma200:
        print("WARNING: LevDax daily ETF is below SMA200. Market trend is too bearish. Sell the LevDax daily ETF completely!")
    elif below_lvdx_sma150:
        print("WARNING: LevDax daily ETF is below SMA150. Market trend is very bearish. Move 50% or at least Gains into Global All-Cap ESG!")
    elif below_lvdx_smaq:
        print("WARNING: LevDax daily ETF is below SMAq. Market trend is bearish. Move 25% or at least 50% Gains into EU All-Cap ESG!")
    elif below_lvdx_sma50:
        print("WARNING: LevDax daily ETF is below SMA50. Market trend is slightly bearish. Stop saving plan!")    
    elif True in below_lvdx_sma:
        print("Attention: LevDax daily ETF is below SMA for ",np.array(latest_lvdx_sma_keys)[below_lvdx_sma]," Consider reducing leveraged position!")
    else:
        print("Market conditions are stable. No immediate action needed.")
    print("\n")
    if above_dax_smaq and below_dax_sma50: print("If previously below DAX SMAq consider adding to your leveraged position!")
    elif above_lvdx_smaq and below_lvdx_sma50: print("If previously below DAX SMAq consider adding to your leveraged position!")
    print("\n")

def plot_scraped_data(ticker_data, sma_period, ticker_name): # ticker="^GDAXI"):
    # Plotting
    fig1, ax1 = plt.subplots(figsize=(14, 7))

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
    ax1.set_title(f'{ticker_name} Index (Last 2 Years)')
    plt.show()


# Main function
def main(sma_period):
    # Get data
    dax_data = get_dax_data()
    lvdx_data = get_lvdx_data()
    
    # Check signals
    check_signals(dax_data, lvdx_data, sma_period)

    # Plot the scraped data
    plot_scraped_data(dax_data, sma_period, ticker_name='DAX')  #, ticker="^GDAXI")
    plot_scraped_data(lvdx_data, sma_period, ticker_name='LevDAX')  #, ticker="LVDX.DE")
    
# Run the script
if __name__ == "__main__":
    if len(argv)>1: V1X_THRESHOLD = int(argv[1])
    if len(argv)>2: SMA_PERIOD = int(argv[2])
    main(V1X_THRESHOLD,SMA_PERIOD)