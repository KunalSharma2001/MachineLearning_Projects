from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting #framework for back testing
from lumibot.strategies.strategy import Strategy # using for creting strategy
from lumibot.traders import Trader # using for creating trader
from datetime import datetime
from alpaca_trade_api import REST # to get the news
from timedelta import Timedelta # to get the time difference

# creating variable to told the variable data
API_KEY = "PKNDQ8L53O4VW0FD8FYN"
API_SECRET = "v3BCXfi54nwHVQJ2eg9Aos8jX2gu5WUB1XO8bbAx"
BASE_URL = "https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY" : API_KEY,
    "API_SECRET" : API_SECRET,
    "PAPER": True # since we are not using real cash...
}

# when we start the BOT, the initialize method will run once, the on_trading_iteration will run every time the bot whenever we recieve a new data/transaction.
class MLTrader(Strategy):
    def initialize(self, symbol:str = "SPY", cash_at_risk:float = .5):
        self.symbol = symbol
        self.spleetime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        
    def position_sizing(self):
        cash = self.get_cash() # getting the cash that we have
        last_price = self.get_last_price(self.symbol) # getting the last price of the trade
        # we need to calculate the position size, it will be calculated on the basis of the metric called cash at risk
        quantity = round(cash * self.cash_at_risk / last_price) # tell us abt the units we are getting per amount that we wanna risk
        return cash, last_price, quantity
    
    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')
    
    def get_news(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        return news
        
        
    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        if cash > last_price:
            if self.last_trade == None:
                news = self.get_news()
                print(news)
                order = self.create_order(
                    self.symbol,
                    quantity, # buy this many quantity of stocks
                    "buy",
                    type = "bracket",
                    take_profit_price = last_price * 1.20, #take 20% profit
                    stop_loss_price = last_price * 0.95 #take 5% loss only
                )
                self.submit_order(order)
                self.last_trade = "buy"

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol": "SPY", "cash_at_risk": .5})

start_date = datetime(2023, 12, 15) # starting from Dec 15, 2023
end_date = datetime(2023, 12, 31) # ending till Dec 31, 2023
strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol": "SPY", "cash_at_risk": .5}
)