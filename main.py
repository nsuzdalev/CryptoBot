from prices_report import send_prices_block
from forecast_block import send_forecast_block
from levels_block import send_levels_block
from btc_dominance_block import send_btc_dominance_block
from news_block import send_news_block
from jumps_block import send_jumps_block
from liquidation_levels_block import send_liquidation_levels_block

def main():
    send_prices_block()
    send_forecast_block()
    send_levels_block()
    send_btc_dominance_block()
    send_news_block()
    send_jumps_block()
    send_liquidation_levels_block()

if __name__ == "__main__":
    main()
