"""
Есть файл с данными. Каждая строка это одна биржевая свеча (OHLCV). Нужно проитерироваться по всем свечам и на каждой
свече рассчитать значение индикатора RSI 14. Проверить полученное значение на два сигнальных уровня 30% и 70%. При 30%
совершить сделку на покупку актива на 100$. Т.е. на 100$ купить актива по цене Close текущей свечи. При 70% совершить
продажу купленного актива в последней сделке. После окончания рассчёта, нужно закрыть открытые сделки по Close
последней свечи, если есть открытые сделки.
Надо получить:
Список PNL каждой сделки. Суммарный PNL. График PNL в любом виде.
Полезные ссылки:
https://academyfx.ru/indikator-rsi
https://www.binance.com/ru/blog/all/%D1%87%D1%82%D0%BE-%D1%82%D0%B0%D0%BA%D0%BE%D0%B5-pnl--%D0%BA%D0%B0%D0%BA-%D1%80%D0%B0%D1%81%D1%81%D1%87%D0%B8%D1%82%D0%B0%D1%82%D1%8C-%D0%BF%D1%80%D0%B8-%D1%82%D0%BE%D1%80%D0%B3%D0%BE%D0%B2%D0%BB%D0%B5-%D0%BD%D0%B0-%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B1%D0%B8%D1%80%D0%B6%D0%B5-binance-421499824684902245
"""
import matplotlib.pyplot as plt


# generator for reading file lines
def input_generator(file_path: str = "test.csv"):
    with open(file_path, "r") as source:
        # skip header
        source.readline()
        is_eof = False
        while not is_eof:
            line = source.readline()
            if line:
                yield line.strip('\n').split("^")
            else:
                is_eof = True


def get_rsi(window: list):
    # getting all gain and loss in window
    gain, loss = [], []
    for i in range(window_height - 1):

        # getting lists of  gain and loss
        close_now = float(window[i][-2])
        close_next = float(window[i + 1][-2])
        if close_now < close_next:
            gain.append(close_next - close_now)
        elif close_now > close_next:
            loss.append(close_now - close_next)

    # getting the RSI value
    average_gain = sum(gain) / window_height
    average_loss = sum(loss) / window_height
    if average_loss == 0:
        rsi = 100
    else:
        rsi = 100 - (100 / (1 + average_gain / average_loss))

    return rsi


def get_pnl(window: list):
    last_row = window[-1]
    pnl = (float(last_row[1]) - float(last_row[-2])) * float(last_row[-1])
    return pnl


def make_transaction(window: list):
    if rsi <= 30:
        volume_of_buying = float(window[-1][-2]) * 100
        transactions.append(volume_of_buying)
        pnl = get_pnl(window)
    elif rsi >= 70 and len(transactions) > 0:
        last_volume_of_buying = transactions.pop()
        dollars_after_selling = last_volume_of_buying / float(window[-1][-2])
        print("$", dollars_after_selling)
        pnl = get_pnl(window)
    else:
        return 0
    return pnl


if __name__ == '__main__':
    window_height = 14
    row_reader = input_generator("btcusdt.csv")

    # pnl list for every transaction
    pnls = []

    # working with first iteration of sliding window
    window = []
    for i in range(window_height):
        window.append(next(row_reader))

    rsi = get_rsi(window)
    # print(rsi)
    transactions = []
    pnls.append(make_transaction(window))

    # working with others sliding windows
    for row in row_reader:
        del window[0]
        window.append(row)
        rsi = get_rsi(window)
        pnls.append(make_transaction(window))

    print(f"Summary PNL: {sum(pnls)}")

    x = [i for i in range(len(pnls))]
    plt.plot(x, pnls)
    plt.savefig("results.png")
