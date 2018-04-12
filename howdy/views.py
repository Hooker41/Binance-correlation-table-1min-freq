from django.shortcuts import render
from django.views.generic import TemplateView
from binance.client import Client
from django.http import HttpResponse
import json
import pandas as pd

client = Client('8gGprOSNg8hEhAibVFalU8JjMjMB5TqNhbJqkJNpUxVMdTlzawYDnnqZ0tnKeXZn', 'L8shsvxWJnZVaaR2PasdYfZFogs5LMLhrG3FKp3yTLg8tYjaURjaaJNijzOVt4NX')

# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        prices = client.get_all_tickers()

        return render(request, 'index.html', {
            'prices':prices
        })

class AboutPageView(TemplateView):
    template_name = "about.html"

def merge_dfs_on_column(dataframes, labels, col):
    series_dict = {}
    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]
        
    return pd.DataFrame(series_dict)

def get_crypto_data(pair):
    candles = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1MINUTE, "12 hours ago UTC")
    candle_list = []

    for candle in candles:
        list = {
            "OpenTime": float(candle[0]),
            "Open": float(candle[1]),
            "High": float(candle[2]),
            "Low": float(candle[3]),
            "Close": float(candle[4]),
            "Volume": float(candle[5]),
            "CloseTime": float(candle[6]),
            "QuoteAssetVolume": float(candle[7]),
            "NumberOfTrades": float(candle[8]),
            "TakerBuyBaseAssetVol": float(candle[9]),
            "TakeBuyQuoteAssetVol": float(candle[10]),
            "Ignore": float(candle[11])
        }
        candle_list.append(list)
    return pd.DataFrame(candle_list)


def GetPrice(request):

    altcoins = ['ETH','XRP','LTC','EOS','TRX','ADA','NEO','BNB']

    altcoin_data = {}
    for altcoin in altcoins:
        coinpair = '{}BTC'.format(altcoin)
        crypto_price_candle_ary = get_crypto_data(coinpair)
        altcoin_data[altcoin] = crypto_price_candle_ary

    # Merge USD price of each altcoin into single dataframe, "close price" column
    combined_df = merge_dfs_on_column(list(altcoin_data.values()), list(altcoin_data.keys()), 'Close')

    corr_matrix = combined_df.pct_change().corr(method='pearson')
    # corr_matrix.to_csv("corr_table.csv")

    # corr_matrix.to_json(orient='index')

    return HttpResponse(corr_matrix.to_json(orient='split'))
