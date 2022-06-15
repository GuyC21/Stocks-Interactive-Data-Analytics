from turtle import color, title
from pandas_datareader import data, wb
import pandas_datareader as data
import pandas as pd
import numpy as np
import datetime
import matplotlib
import matplotlib.pyplot as plt
import cufflinks as cf
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import chart_studio as cs
from plotly.offline import download_plotlyjs,init_notebook_mode,plot,iplot
from plotly import tools
#init_notebook_mode(connected=True)
cf.go_offline()

#stocks registering 
def stock_register(data_source,start_date,end_date):
    tickers = []
    stockDFs = []
    counter = 0
    stock = input('enter stock symbol (type exit to continue): ')
    while (stock.lower()!='exit'):
        try:
            stock = stock.upper()
            stockDFs.append(data.DataReader(stock,data_source,start_date,end_date))
            tickers.append(stock)
            counter+=1
        except:
            print('stock has not been found, try again')
        stock = input('enter stock symbol (type exit to continue): ')
    bank_stocks = pd.concat(stockDFs,keys=tickers,axis=1)
    bank_stocks.columns.names = ['Bank Ticker','Stock Info']

    #Quality of life changes to the dataframes
    roundOrNot = input("type 'Yes' if you wanna round the data, 'No' if not: ")
    if roundOrNot.lower() == 'yes':
        x = input('how many digits would you like to see after the dot? ')
        bank_stocks = bank_stocks.round(int(x))
    returns_ratio = pd.DataFrame() #saving the returns

    for tick in tickers:
        returns_ratio[tick+' Return'] = bank_stocks[tick,'Close'].pct_change()

    return bank_stocks,returns_ratio

#analysing starts here
def ratios(returns_ratio):
    max_ratio = returns_ratio.idxmax()
    min_ratio = returns_ratio.idxmin()
    return max_ratio, min_ratio

#Risk defining
#Overall risk
def returns_std(returns_ratio):
    condition = input("to see overall risk value, type whatever you want, to look for specific years, enter 'spec': ")
    stdList = []
    while (condition.lower() == 'spec'):
        startCheck = input('from (yyyy-mm-dd): ')
        endCheck = input('to (yyyy-mm-dd): ')
        try:
            stdList.append(returns_ratio.loc[startCheck:endCheck].std())
        except:
            print('you probably entered a date not according to our format, please try again')
        condition = input("'Overall' to finish and add an overall view, 'spec' to add a specific one, anything else to go to next section: ")
        if (condition.lower() =='overall') and (len(stdList)>0):
            stdList.append(returns_ratio.std())
    if len(stdList) > 0:
        return stdList
    else:
        return returns_ratio.std()

#check for lowest opening price, for specific dates or overall at the same function
def lowest_open_price(returns_ratio):
    condition = input("type 'spec' to watch for specific dates lowest opening, anything else for overall view: ")
    lowestOpeningL = []
    lowestOpeningDL = []
    while condition == 'spec':
        startCheck = input('from (yyyy-mm-dd): ')
        endCheck = input('to (yyyy-mm-dd): ')
        try:
            lowestOpeningL.append(bank_stocks.loc[startCheck:endCheck].xs(key='Open',axis=1,level=1).min())
            lowestOpeningDL.append(bank_stocks.loc[startCheck:endCheck].xs(key='Open',axis=1,level=1).idxmin())
        except:
            print('you probably entered a date not according to our format, please try again')
        condition = input("'Overall' to finish and add an overall view, 'spec' to add a specific one, anything else to go to next section: ")
        if (condition.lower() =='overall') and (len(lowestOpeningL)> 0 ) and (len(lowestOpeningDL) > 0):
            lowestOpeningDL.append(bank_stocks.xs(key='Open',axis=1,level=1).idxmin())
            lowestOpeningL.append(bank_stocks.xs(key='Open',axis=1,level=1).min())
    if len(lowestOpeningL)> 0  and len(lowestOpeningDL) > 0:
        return lowestOpeningL, lowestOpeningDL
    else:
        return bank_stocks.xs(key='Open',axis=1,level=1).min(), bank_stocks.xs(key='Open',axis=1,level=1).idxmin()

#creating the relevent matplotlib graphs
def matplotgraphs(bank_stocks):
    def comparingLegend(bank_stocks): #a function to create correct legend values for the comparing graph
        legendValues = []
        counteredTickers = []
        for col in bank_stocks:
            counter = 0
            for item in counteredTickers:
                if col[0]==item:
                    counter+=1
            if counter<1:
                counteredTickers.append(col[0])
                legendValues.append(col[0]+' Closing $')
                legendValues.append(col[0]+' Mooving AVG')
        return legendValues

    sns.set_style('whitegrid')
    fig, axes = plt.subplots(2,2,figsize=(16,12))
    #returns graph
    sns.lineplot(data = bank_stocks.xs(key='Close',axis=1,level=1),ax=axes[0,0]).set(title='Returns Graph')
    #moving avg graph
    sns.lineplot(data = bank_stocks.xs(key='Close',axis=1,level=1).rolling(window=30).mean(),ax=axes[0,1]).set(title='Moving AVG graph')
    #corrolation heatmap
    sns.heatmap(data = bank_stocks.xs(key='Close',axis=1,level=1).corr(),annot=True,ax=axes[1,0]).set(title='Corr Heatmap')
    sns.color_palette('pastel')
    #comparing the closing price with the mooving avg
    returns = bank_stocks.xs(key='Close',axis=1,level=1)
    mooving =  bank_stocks.xs(key='Close',axis=1,level=1).rolling(window=30).mean()
    plt.plot(returns)
    plt.plot(mooving)
    plt.legend(comparingLegend(bank_stocks.head()),loc='best') #loc=(1.04,0.2))
    plt.title('closing value compared to 30 day mooving average')
    plt.tight_layout()
    return fig


#source
try:
    data_source = input('enter your preffered data_source (reccomended: yahoo): ')
    start_date = input('enter start date (format: yyyy-mm-dd): ')
    start_date = pd.to_datetime(start_date,)
    end_date = input('enter end date (format: yyyy-mm-dd): ')
    end_date = pd.to_datetime(end_date)
    #data_source = 'yahoo'
    #start_date = '2008-01-01'
    #end_date = '2022-09-06'

    #creating the data and showing it
    bank_stocks, returns_ratio = stock_register(data_source,start_date,end_date)
    print('\n',"Created data's head:")
    print(bank_stocks.head(), "\n")
    print("Created returns ratio data's head:")
    print(returns_ratio.head(), "\n")

    #simple analyzes
    max_ratio, min_ratio = ratios(returns_ratio)
    print('Highest return ratios happened at: \n', max_ratio, '\n')
    print('Lowest return ratios happened at: \n', min_ratio, '\n')

    diviation = returns_std(returns_ratio)
    if type(diviation) == "<class 'list'>":
        print('\n standard diviation respectively to the order of the dates you entered \n',diviation)
    else:
        print('\n','overall standard daviation of the return ratios: \n', diviation)

    lowOpenPrice, lowOpenPriceDate = lowest_open_price(bank_stocks)
    print('Lowest opening price of each stock you entered is: \n', lowOpenPrice,'\n which happened at: \n', lowOpenPriceDate)

    #graphs
    #returns line plot
    matplotgraphs(bank_stocks)
    plt.show()

except:
    print("re-run app, you've entered wrong formatted date")
