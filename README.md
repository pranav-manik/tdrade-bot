# tdrade-bot
automated stock transactions for TD Ameritrade based on tickers and percentages given, also keeps track of and reinvests reserves as necessary

# Requirements
python 3.8+

# Set up
fill out a .env file with the following info
```
CLIENT_ID='fsajfhsdakfjhasd234678736q4dh3q'
REDIRECT_URI='http://localhost/'
CREDENTIALS_FILE_PATH='/path/to/file.json'
CSV_PATH='/path/to/file.csv'
RESERVES_PATH='/path/to/file.txt'
TOTAL_CASH=1500
```
set tickers og your choice for under tickers with percentages in tdrade.py
```
tickers = { 
	'MSFT': [15], 
	'QQQ': [35],
	'VOO': [50]
}
```

change reserve_tick to a ticker you already have to invest reserves
```
reserve_tick = 'VOO'
```