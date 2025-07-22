from prices_report import build_prices_block
from forecast_block import build_forecast_block
from levels_block import build_levels_block
from btc_dominance_block import build_btc_dominance_block
from news_block import build_news_block
from jumps_block import build_jumps_block
from liquidation_levels_block import build_liquidation_levels_block

def main():
    build_prices_block()
    build_forecast_block()
    build_levels_block()
    build_btc_dominance_block()
    build_news_block()
    build_jumps_block()
    build_liquidation_levels_block()

if __name__ == "__main__":
    main()
