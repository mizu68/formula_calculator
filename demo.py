
from formula_calculator import calculator
from formula_calculator.channel_demo.data_channel import StockChannel


if __name__ == '__main__':
    fomula = "max(rolling(close,20))-shift(close,20-argmax(rolling(close,20)))"
    channel = StockChannel('000002.SZ','3S').run()
    for i in calculator(channel,fomula,'factor1'):
        print(i)