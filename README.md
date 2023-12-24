1. Create a virtual environment with requirement.txt.

2. Activate the virtual environment and run the python file scrap_stock_data.py .

3. Above python file will scarp data of Broad Market Indices and save the data in csv file and these files are saved in 'CSV' folder(1st task of the assignment).

3. Above python file will also generate the required result using nifty_50.csv data and after applying the filter mentioned in 2nd point of assignment the final result will be saved in final.csv file again in CSV folder. Also, saved the data of tickers that satisfied the filters in final.json file and this is saved under 'JSON' folder.(2nd point of the assignment)

4. Above python file will also fetch the prices data, create the plot on 5 years of Adj. close price data. plots will be saved in 'PNG' folder. And for understanding and reusability purpose 5years data of final stocks are saved in CSV folder(ex:- StockName_5years.csv).

6. Weight of stocks for Max Sharpe portfolio are save in json format for the stocks available in final.csv file. We can find the json data in JSON file( i.e. filename "stockName"_weights.json) in JSON folder .

7. Portfolio performance of stocks present in final.csv file is save in "stock_name"_portfolio.json and saved under JSON folder

