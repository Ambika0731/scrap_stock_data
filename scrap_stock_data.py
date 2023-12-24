import pandas as pd
from bs4 import BeautifulSoup
import pandas as pd
import requests
from yahoo_fin import stock_info as si
from yahoo_fin import options
import json
import os
# import yfinance as yahooFin
import matplotlib.pyplot as plt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns


def get_broad_market_indices(url, headers):
    """ Function to get list of broad market indices """
    
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    lable = soup.find("optgroup")

    options = lable.find_all("option")
    option_dict = {
        option.text.strip().replace(" ", "_").lower(): option["value"]
        for option in options
    }
    return option_dict

def save_broad_market_indices_data(indices_name, indices_value, headers):
    """ Function to save data of different Board market indices """
    
    indices_url = f"https://www1.nseindia.com/live_market/dynaContent/live_watch/stock_watch/{indices_value}.json"

    response = requests.get(url=indices_url, headers=headers)
    indices_file = pd.DataFrame(response.json()["data"])
    indices_file.to_csv(f"CSV/{indices_name}.csv", index=False)
    # indices_file.head()


def get_final_items(filename):
    """ Function to get fundamental data of nifty 50 
        and to apply listed filters sequentially on the data """
        
    final_dict = {}
    dataframe = pd.read_csv(filename)
    symbol_list = list(dataframe["symbol"])
    for symbol in symbol_list:
        try:
            quote = si.get_quote_table(f"{symbol}.NS")
            stats = si.get_stats_valuation(f"{symbol}.NS").fillna(0)
            other_stats = si.get_stats(f"{symbol}.NS").fillna(0)
            other_stats_dict = dict(
                zip(other_stats["Attribute"].to_list(), other_stats["Value"].to_list())
            )
            stats_dict = dict(zip(stats[0].to_list(), stats[1].to_list()))
            try:
                if (
                    (quote["EPS (TTM)"]) > 4
                    and (quote["PE Ratio (TTM)"]) < 30
                    and (float(stats_dict["Price/Book (mrq)"])) < 15
                    and (
                        float(
                            str(other_stats_dict["Return on Equity (ttm)"]).replace(
                                "%", ""
                            )
                        )
                    )
                    > 20
                    and (float(other_stats_dict["Total Debt/Equity (mrq)"])) < 75
                    and (
                        float(
                            str(other_stats_dict["% Held by Insiders 1"]).replace(
                                "%", ""
                            )
                        )
                    )
                    > 30
                ):
                    final_dict[symbol] = {}
                    final_dict[symbol]["EPS"] = quote["EPS (TTM)"]
                    final_dict[symbol]["P/E"] = quote["PE Ratio (TTM)"]
                    final_dict[symbol]["P/B"] = float(stats_dict["Price/Book (mrq)"])
                    final_dict[symbol]["ROE"] = float(
                        str(other_stats_dict["Return on Equity (ttm)"]).replace("%", "")
                    )
                    final_dict[symbol]["D/E"] = float(
                        other_stats_dict["Total Debt/Equity (mrq)"]
                    )
                    final_dict[symbol]["SOB"] = float(
                        str(other_stats_dict["% Held by Insiders 1"]).replace("%", "")
                    )
            except Exception as e:
                print("Error -", e)
        except:
            pass
    return final_dict


def get_five_year_records(final_list):
    """ function to retrive price data of final stocks(final.csv)""" 
    
    for item in final_list:
        
        #retriving 5 years data of symbol/ticker available in the final list
        five_year_data = si.get_data(
            f"{item}.NS",
            start_date="23/03/2018",
            end_date="23/03/2023",
            index_as_date=True,
        )
        five_year_data["date"] = five_year_data.index
        file_list = ["date", "open", "high", "low", "close", "adjclose"]
        five_year_data[file_list].to_csv(f"CSV/{item}_5year.csv", index=False)
        
        # item_name = yahooFin.Ticker(f"{item}.NS")
        # five_year_data = item_name.history(period="5y")
        # five_year_data['Date'] = five_year_data.index
        # five_year_data['Date'] = pd.to_datetime(five_year_data['Date']).dt.date
        # file_list = ["Date","Open","High","Low","Close","Volume"]
        # five_year_data[file_list].to_csv(f"{item}_5year.csv",index=False)
        
        # plotting the graph between year and price of the final ticker/symbol
        DF = pd.DataFrame()
        DF["Adj_close"] = five_year_data["adjclose"]
        DF = DF.set_index(five_year_data["date"])
        plt.plot(DF)
        plt.gcf().autofmt_xdate()
        plt.savefig(f"PNG/{item}.png")
        plt.close()


def get_weight(final_list):
    """ function to get the weights of these stocks for the Max Sharpe portfolio """
    
    for item in final_list:
        five_year_data = pd.read_csv(f"CSV/{item}_5year.csv")
        five_year_data = five_year_data.set_index(
            pd.DatetimeIndex(five_year_data["date"].values)
        )
        five_year_data.drop(columns=["date"], axis=1, inplace=True)
        mu = expected_returns.mean_historical_return(five_year_data)
        S = risk_models.sample_cov(five_year_data)

        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe()
        cleaned_weights = ef.clean_weights()

        portfolio_performance_list = [
            'Expected annual return', 'Annual volatility', 'Sharpe Ratio']
        print(f"STOCK NAME : {item}")
        portfolio_performance = ef.portfolio_performance(verbose=True)
        portfolio_performance_dict = dict(zip(
            portfolio_performance_list, portfolio_performance))
        
        # saving the weights in json file with their respective ticker/symbol name
        with open(f"JSON/{item}_weights.json", "w") as outfile:
            json.dump(dict(cleaned_weights), outfile, indent=4)
        
        with open(f"JSON/{item}_portfolio.json",'w') as outfile:
            json.dump(portfolio_performance_dict, outfile, indent=4)


if __name__ == "__main__":
    
    url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/equities_stock_watch.htm"
    headers = {
        "Accept": "application/json, text/javascript, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB, en-US",
        "Connection": "keep-alive",
        "Cookie": "NSE-TEST-1 = 1960845322.20480.0000",
        "User-Agent": "Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    folders = ['CSV','JSON','PNG']
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)
            
    option_dict = get_broad_market_indices(url, headers)
    for key, value in option_dict.items():
        save_broad_market_indices_data(key, value + "StockWatch", headers)
    
    # retriving the tickers of nifty 50 from csv file and preparing final csv
    filename = "CSV/nifty_50.csv"
    final_dict = get_final_items(filename)
    
    # saving final symbol/ticker with EPS, P/E, P/B, ROE, etc. data 
    with open("JSON/final.json", "w") as outfile:
        json.dump(final_dict, outfile, indent=4)

    # saving the symbols/tickers name in final.csv that satisfied the required filters
    with open("CSV/final.csv", "w") as f:
        symbol_list = ['symbol']
        symbol_list.extend(list(final_dict.keys()))
        for value in symbol_list:
            f.write("%s\n" % (value))

    # f = open("JSON/final.json")
    # final_dict = json.load(f)

    final_list = list(final_dict.keys())
    get_five_year_records(final_list)
    get_weight(final_list)

