from datetime import date, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.dates as mdates
from matplotlib.colors import Normalize
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from yfinance import Ticker
from typing import List

months = ['Jan','Feb','Mar','Apr','Mai','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# Define the date range to retrieve data for
start_date = str(date.today()-timedelta(days=5*365))
end_date = str(date.today())

# Dividend Settings
month_period = 6

# helper function
def get_rid_of_shit(x:str):
    arr = x.split(",")[:-1]
    return arr[0]+","+arr[1]
correct = np.vectorize(get_rid_of_shit)


def three_layer_linear_regressor(series: pd.Series, tag:str, timings: List[int] = [36,24,12,6,3], 
                                 in_months: bool = True, repeat: int = 3):
    # model at different pred depth
    model_zoo = list()
    for timing in timings:
        y = series.iloc[timing:].to_numpy()         # use all but the first timeframe as target data
        # train set window split
        X = np.array([[series.to_numpy()[idx+offset] for offset in range(timing)] \
             for idx in range(len(series)-timing)])  # use all but the last timeframe as training data                
        for it in range(repeat):  
            model = LinearRegression()
            model.fit(X, y)
            model_zoo.append(model)

    # first merge using all depths
    model_layer_two = list()
    for it in range(repeat):
        X = list()
        for idx in range(max(timings),len(series)):
            X.append([
                model_zoo[it::repeat][num].predict(
                np.array([series.iloc[idx-timings[num]+offset] for offset in range(timings[num])]).reshape(1,-1)
                )[0] \
                    for num in range(len(model_zoo[it::repeat]))])
        X = np.array(X)
        y = series.iloc[max(timings):].to_numpy()
        model = LinearRegression()
        model.fit(X, y)
        model_layer_two.append(model)
    
    # general model using all versions at all depths
    X = list()
    for idx in range(max(timings),len(series)):
        X.append([
            model_layer_two[it].predict(np.array([
                model_zoo[it::repeat][num].predict(
                np.array([series.iloc[idx-timings[num]+offset] for offset in range(timings[num])]).reshape(1,-1)
                )[0] for num in range(len(model_zoo[it::repeat]))
            ]).reshape(1,-1))[0] for it in range(len(model_layer_two))])
    X = np.array(X)
    y = series.iloc[max(timings):].to_numpy()
    model = LinearRegression()
    model.fit(X, y)

    # predictions with general model for future year
    if in_months:
        future_index = pd.date_range(date.today(), periods=12, freq='M')
        input_vec = [[
            model_layer_two[it].predict(np.array([
                model_zoo[it::repeat][num].predict(
                np.array([series.iloc[-timings[num]+month+offset] for offset in range(timings[num])]).reshape(1,-1)
                )[0] for num in range(len(model_zoo[it::repeat]))
            ]).reshape(1,-1))[0] for it in range(len(model_layer_two))]
        for month in range(12)]

        future_year_preds = pd.DataFrame({'Date': future_index, tag: np.clip(model.predict(input_vec),0,None) }).set_index('Date')
    else:
        future_index = pd.date_range(date.today(), periods=1, freq='Y')
        input_vec = [[
            model_layer_two[it].predict(np.array([
                model_zoo[it::repeat][num].predict(
                np.array([series.iloc[-timings[num]+1+offset] for offset in range(timings[num])]).reshape(1,-1)
                )[0] for num in range(len(model_zoo[it::repeat]))
            ]).reshape(1,-1))[0] for it in range(len(model_layer_two))]]
        future_year_preds = pd.DataFrame({'Date': future_index, tag: model.predict(input_vec) }).set_index('Date')

    # output
    return pd.concat([series, future_year_preds[tag]])


def create_plot_tickers(tickers: List[Ticker], syms: List[str], types:List[str]):

    all_total_return, all_dividends, all_stock_prices, all_stock_peRatio = [list(),list(),list(),list()]
    for ticker,inv_type in zip(tickers,types):
        df = ticker.history(start=start_date, end=end_date, interval='1mo')

        # fill NaN values with previous row values
        df['Close'] = df['Close'].fillna(method='ffill').fillna(method='bfill')
        df['Dividends'] = df['Dividends'].fillna(0)

        # train and use linear regression model to predict changes in stock price and dividends for next year
        timings = [36,24,12,6,3]  # time windows for regressors 
        monthly_close = three_layer_linear_regressor(df["Close"], "Close", timings, in_months=True)
        dividends = three_layer_linear_regressor(df["Dividends"], "Dividends", timings, in_months=True)

        # format results
        monthly_close.index = pd.DatetimeIndex([str(date).split(" ")[0] for date in monthly_close.index])
        monthly_close.index.name = "Date"
        dividends.index = pd.DatetimeIndex([str(date).split(" ")[0] for date in dividends.index])
        dividends.index.name = "Date"

        # extract annual earnings and fill in NaNs
        earnings = None
        try: 
            earnings = ticker.earnings_history
            earnings["Date"] = pd.DatetimeIndex(correct(earnings["Earnings Date"]))
            earnings = earnings.set_index("Date")["Reported EPS"].fillna(method='ffill').fillna(method='bfill')
            earnings = earnings[pd.to_datetime('now').year-5<=pd.DatetimeIndex(earnings.index).year]
            earnings = earnings[pd.DatetimeIndex(earnings.index).year<=pd.to_datetime('now').year]
            earnings = earnings[(pd.DatetimeIndex(earnings.index).month<=pd.to_datetime('now').month).__or__(pd.DatetimeIndex(earnings.index).year<pd.to_datetime('now').year)]
            earnings = earnings.groupby(pd.DatetimeIndex(earnings.index).year).first()
        except: 
            earnings = pd.DataFrame(np.zeros(len(monthly_close[:-12:12]))+ticker.info["epsTrailingTwelveMonths"],index=monthly_close[:-12:12].index)[0]
        
        # train a linear regression model to predict changes in earnings
        timings = [3,2,1]  # time windows for regressors
        annual_earnings = three_layer_linear_regressor(earnings, "Earnings", timings, in_months=False)

        # Calculate the monthly returns for each ticker
        monthly_returns = monthly_close.pct_change().replace(float('inf'), 0)

        # Calculate the cumulative growth for each ticker
        cumulative_growth = (1 + monthly_returns).cumprod()

        # Calculate the total return (growth + dividends) for each ticker
        total_return = cumulative_growth * (1 + dividends / monthly_close.shift(1).replace(0,1)).cumprod()

        #if inv_type == "Fund" or inv_type == "ETF":
        #    try:
        #        cap_gain = ticker.actions["Capital Gains"].fillna(method='ffill').fillna(method='bfill')
        #        cap_gain.index = pd.DatetimeIndex([str(date).split(" ")[0] for date in earnings.index])
        #        cap_gain.index.name = "Date"
        #    except:
        #        cap_gain = pd.DataFrame(np.ones(len(monthly_close)),index=monthly_close.index)[0]

        all_dividends.append(dividends)
        all_total_return.append(total_return)
        all_stock_prices.append(monthly_close)
        all_stock_peRatio.append(pd.DataFrame(monthly_close.iloc[::12].to_numpy()/annual_earnings.clip(lower=1e-8).to_numpy(),index=monthly_close.iloc[::12].index)[0])


    # Plot cumulative growth and dividends
    ax1  = plt.figure(1,figsize=(10, 8)).gca()
    ax2  = plt.figure(2,figsize=(10, 8)).gca()
    ax3  = plt.figure(3,figsize=(10, 8)).gca()
    ax4  = plt.figure(4,figsize=(10, 8)).gca()
    if inv_type == "Stock" or inv_type == "REIT":
        fig5 = plt.figure(5,figsize=(10, 8))
        ax5  = fig5.gca()
    ax6  = plt.figure(6,figsize=(10, 8)).gca()
    ax7  = plt.figure(7,figsize=(10, 8)).gca()

    all_stock_prices = pd.concat(all_stock_prices, axis=1, keys=syms).fillna(method='ffill').fillna(method='bfill')
    all_dividends = pd.concat(all_dividends, axis=1, keys=syms).fillna(0)
    all_stock_peRatio = pd.concat(all_stock_peRatio, axis=1, keys=syms).fillna(method='ffill').fillna(method='bfill')
    all_total_return = pd.concat(all_total_return, axis=1, keys=syms).fillna(method='ffill').fillna(method='bfill')*100
    if inv_type == "Stock" or inv_type == "REIT": corr_mat = all_stock_prices.corr()
    all_annual_yields = pd.DataFrame(((all_stock_prices.iloc[12::12].to_numpy()/all_stock_prices.iloc[:-12:12].to_numpy())-1)*100,
                                     columns=all_stock_prices.columns, index=all_stock_prices.iloc[12::12].index)
    all_annual_volatility = pd.DataFrame([(all_stock_prices.iloc[it*12:(it+1)*12].std().to_numpy()/all_stock_prices.iloc[(it+1)*12].to_numpy())*100 for it in range((len(all_stock_prices)//12))],
                                     columns=all_stock_prices.columns, index=(all_stock_prices.iloc[12::12]).iloc[:(len(all_stock_prices)//12)].index)

    all_stock_prices.plot.line(ax=ax1)
    all_dividends.plot.bar(ax=ax2,stacked=True)
    all_stock_peRatio.plot.line(ax=ax3)
    all_total_return.plot.line(ax=ax4)
    if inv_type == "Stock" or inv_type == "REIT":
        sm.graphics.plot_corr(corr_mat,xnames=all_stock_prices.columns,ax=ax5,normcolor=(0,1),cmap=cm.get_cmap('jet'))
        fig5.colorbar(cm.ScalarMappable(norm=Normalize(vmin=0,vmax=1), cmap=cm.get_cmap('jet')), ax=ax5)
    all_annual_yields.plot.line(ax=ax6)
    all_annual_volatility.plot.line(ax=ax7)

    ax1.set_ylabel('Stock Price in $')
    ax2.set_ylabel('Dividends in $')
    ax3.set_ylabel('P/E-Ratio')
    ax4.set_ylabel('Total Return in %')
    if inv_type == "Stock" or inv_type == "REIT": ax5.set_title('Correlation of Tickers')
    ax6.set_ylabel('Annual Yield in %')
    ax7.set_ylabel('Annual Volatility in %')

    ax2.set_xticks(ax2.get_xticks()[::month_period], labels=[months[it%12] \
                    for it in range(0,len(ax2.get_xticks()),month_period)])
    ax1.axvspan(mdates.date2num(all_stock_prices.index[-12]),mdates.date2num(all_stock_prices.index[-1]), facecolor='green', alpha=0.2)
    ax2.axvspan(ax2.get_xticks()[-3]+(ax2.get_xlim()[-1]-ax2.get_xticks()[-1]), \
                ax2.get_xlim()[-1], facecolor='green', alpha=0.2)
    ax3.axvspan(mdates.date2num(all_stock_peRatio.index[-2]), mdates.date2num(all_stock_peRatio.index[-1]), facecolor='green', alpha=0.2)
    ax4.axvspan(mdates.date2num(all_total_return.index[-12]), mdates.date2num(all_total_return.index[-1]), facecolor='green', alpha=0.2)
    ax6.axvspan(mdates.date2num(all_annual_yields.index[-2]),mdates.date2num(all_annual_yields.index[-1]), facecolor='green', alpha=0.2)
    ax7.axvspan(mdates.date2num(all_annual_yields.index[-2]),mdates.date2num(all_annual_yields.index[-1]), facecolor='green', alpha=0.2)
    plt.show()


def etf_pos_corr_plot(t10hold: List[pd.DataFrame], syms: List[str]):
    SYM_DF = pd.concat([pd.DataFrame(hold.T["SYM"].to_numpy(),columns=[sym]).T for sym,hold in zip(syms,t10hold)]).T
    ASSETS_DF = pd.concat([pd.DataFrame(hold.T["Assets"].to_numpy(),columns=[sym]).T for sym,hold in zip(syms,t10hold)]).T
    Corr_Mat = pd.DataFrame()
    for sym in syms:
        col = dict()
        total = np.sum(ASSETS_DF[sym].to_numpy())
        for o_sym in syms:
            num = 0
            for ticker,perc in zip(SYM_DF[sym].to_list(),ASSETS_DF[sym].to_list()): 
                if ticker in SYM_DF[o_sym].to_list(): 
                    num += total/perc
            col[o_sym] = num/total
        Corr_Mat[sym] = pd.Series(col)
    plt.figure(1,figsize=(10, 8))
    plt.imshow(Corr_Mat,cmap=cm.get_cmap('jet'),norm=Normalize(vmin=0,vmax=1))
    plt.colorbar(cm.ScalarMappable(norm=Normalize(vmin=0,vmax=1), cmap=cm.get_cmap('jet')))
    plt.title("Correlation Matrix of ETFs\nTop 10 Holdings")
    plt.xlim((-0.5,len(syms)-1+0.5))
    plt.ylim((-0.5,len(syms)-1+0.5))
    plt.gca().set_xticks([num-0.5 for num in [*range(len(syms))]],minor=True,visible=False)
    plt.gca().set_yticks([num-0.5 for num in [*range(len(syms))]],minor=True,visible=False)
    plt.gca().set_xticks([*range(len(syms))],labels=syms)
    plt.gca().set_yticks([*range(len(syms))],labels=syms)
    plt.gca().grid(which='minor',c='k',lw=3.0)
    plt.show()

 # old code 
 # simple yearly linear_regressor
    #X = df['Close'].iloc[:-12].to_numpy().reshape(-1, 1)  # use all but the last year as training data
    #y = df['Close'].iloc[12:].to_numpy()   # use all but the first year as target data
    #year_model = LinearRegression()
    #year_model.fit(X, y)
    #future_index = pd.date_range(date.today(), periods=12, freq='M')
    #future_year_preds = pd.DataFrame({'Date': future_index, 'Close': [year_model.predict(price.reshape(1, -1))[0] \
    #                                    for price in df['Close'].iloc[-12:].to_numpy()]}).set_index('Date')
    #monthly_close = pd.concat([df['Close'], future_year_preds['Close']])
    
    # Grab the dividends for each ticker
    #X = df['Dividends'].iloc[:-12].to_numpy().reshape(-1, 1)  # use all but the last year as training data
    #y = df['Dividends'].iloc[12:].to_numpy()   # use all but the first year as target data
    #year_model = LinearRegression()
    #year_model.fit(X, y)
    #future_index = pd.date_range(date.today(), periods=12, freq='M')
    #future_year_preds = pd.DataFrame({'Date': future_index, 'Dividends': [year_model.predict(price.reshape(1, -1))[0] \
    #                                    for price in df['Dividends'].iloc[-12:].to_numpy()]}).set_index('Date')
    #dividends = pd.concat([df['Dividends'], future_year_preds['Dividends']])  