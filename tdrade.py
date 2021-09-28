from pathlib import Path #python3 only
from dotenv import load_dotenv
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
import os
import pprint
import pandas as pd
import numpy as np
import datetime
from os.path import exists
import csv

# set up pretty printer
pp = pprint.PrettyPrinter(indent=4)
# Import the client
from td.client import TDClient
from td.orders import Order, OrderLeg
from td.enums import ORDER_SESSION, DURATION, ORDER_INSTRUCTIONS, ORDER_ASSET_TYPE


# Create a new session, credentials path is required.
TDSession = TDClient(
    client_id=os.getenv('CLIENT_ID'),
    redirect_uri=os.getenv('REDIRECT_URI'),
    credentials_path=os.getenv('CREDENTIALS_FILE_PATH')
)

# Login to the session
TDSession.login()


total_cash = os.getenv('TOTAL_CASH')

def perc_calc(p):
	return total_cash*(p/100)


tickers = { 
	'MSFT': [15], 
	'QQQ': [35],
	'VOO': [50]
}

# Grab real-time quotes for 'AMZN' (Amazon) and 'SQ' (Square)
multiple_quotes = TDSession.get_quotes(instruments=list(tickers.keys()))

# pp.pprint(multiple_quotes)

for key,value in multiple_quotes.items():
	tickers[key] += [
		perc_calc(tickers[key][0]),
		value['askPrice'],
		round(perc_calc(tickers[key][0])/value['askPrice']),
		round(perc_calc(tickers[key][0])/value['askPrice']) * value['askPrice'],
		value['52WkHigh'],
		value['52WkLow'],]
	tickers[key].insert(0, datetime.datetime.now())
	# tickers[key].append(round(tickers[key][1]/tickers[key][2]))

# print(tickers)
df = pd.DataFrame(data=tickers, index=['date', 'percentage','total','price','shares bought', 'order total','52WkHigh', '52WkLow'])
print(df)
print('')
# df_t_ = df.T
# df_t_.to_csv(os.getenv('CSV_PATH'), index=True, mode='a')


order = {
  "orderType": "MARKET",
  "session": "NORMAL",
  "duration": "DAY",
  "orderStrategyType": "SINGLE",
  "orderLegCollection": []
}

account_id = TDSession.get_accounts()[0]['securitiesAccount']['accountId']
for tck in tickers:
	order['orderLegCollection'] = [{
      "instruction": "Buy",
      "quantity": tickers[tck][4],
      "instrument": {
        "symbol": tck,
        "assetType": "EQUITY"
      }
    }]
    # PLACES ORDER
	# order_resp = TDSession.place_order(account=account_id, order=order)
	order_resp = {'status_code': 201, 'order_id': '44541234768'}
	if order_resp['status_code'] == 201:
		tickers[tck].append(order_resp['order_id'])
		print("transaction successful")
	else:
		tickers[tck].append('FAILED')
		print("transaction failed")
	# pp.pprint(order_resp)

# pp.pprint(order)
# print(order)


df = pd.DataFrame(data=tickers, index=['date', 'percentage','total','price','shares bought', 'actual total','52WkHigh', '52WkLow', 'order id'])
# print(df)

df_t_ = df.T
df_t_.to_csv(os.getenv('CSV_PATH'), index=True, mode='a', date_format='%m/%d/%Y %H:%M:%S')

total_spent = round(sum([x[5] for x in tickers.values()]), 2)

perc_diff = round(((total_cash-total_spent)/total_spent)*100, 2)
reserve = round(total_cash-total_spent, 2)
with open(os.getenv('RESERVES_PATH')) as fp:
	total_reserves = fp.readline()
total_reserves = round(float(total_reserves) + reserve, 2)

print('')
print(f'total spent: ${total_spent}')
print(f'percentage difference: {perc_diff}%')
print(f'reserve: ${reserve}')
print(f'reserve total: ${total_reserves}')
print('')


# update reserves
# Writing to file
f = open(os.getenv('RESERVES_PATH'), 'w')
f.writelines(str(total_reserves))
f.close()

reserve_tick = 'VOO'

# invest reserves
order['orderLegCollection'] = [{
      "instruction": "Buy",
      "quantity": int(total_reserves//tickers[reserve_tick][3]),
      "instrument":  {
      	"symbol": 'VOO',
        "assetType": "EQUITY"
      }
    }]


# if reserves available invest
if tickers[reserve_tick][3] < total_reserves:
	reserve_order = {reserve_tick : tickers[reserve_tick]}

	reserve_spent = round((int(total_reserves//tickers[reserve_tick][3])*tickers['VOO'][3]),2)
	reserve_perc = round((reserve_spent/total_reserves)*100, 2)

	reserve_order[reserve_tick][0] = reserve_perc
	reserve_order[reserve_tick][4] = int(total_reserves//tickers[reserve_tick][3])


# 	order_resp = TDSession.place_order(account=account_id, order=order)
	order_resp = {'status_code': 201, 'order_id': '44541234768'}
	if order_resp['status_code'] == 201:
		reserve_order[reserve_tick][8] = order_resp['order_id']
		print("transaction successful")
	else:
		reserve_order[reserve_tick][8] = 'FAILED'
		print("transaction failed")

# update reserves
	total_reserves = round(total_reserves - (int(total_reserves//tickers[reserve_tick][3])*tickers['VOO'][3]),2)
	f = open(os.getenv('RESERVES_PATH'), 'w')
	f.writelines(str(total_reserves))
	f.close()

	# write transaction
	df = pd.DataFrame(data=reserve_order, index=['date', 'reserve percentage','total','price','shares bought', 'order total','52WkHigh', '52WkLow', 'order id'])

	df_t_ = df.T
	df_t_.to_csv(os.getenv('CSV_PATH'), index=True, mode='a', date_format='%m/%d/%Y %H:%M:%S')
	