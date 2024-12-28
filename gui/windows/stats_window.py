from PyQt6.QtWidgets import (QWidget, QVBoxLayout,)

import pyqtgraph as pg



class StatsWindow(QWidget):
    def __init__(self, price_data, product_name):
        super().__init__()
        self.setWindowTitle(f"Статистика цен - {product_name}")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Создаем график
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('white')
        plot_widget.showGrid(x=True, y=True)

        dates = list(price_data.keys())
        prices_card = [float(price_data[date]['price_card_ozon']) for date in dates]
        prices_discount = [float(price_data[date]['price_discount']) for date in dates]
        prices_regular = [float(price_data[date]['price']) for date in dates]

        # Добавляем линии на график
        plot_widget.plot(range(len(dates)), prices_card, pen='b', name='Цена с Ozon картой')
        plot_widget.plot(range(len(dates)), prices_discount, pen='g', name='Цена со скидкой')
        plot_widget.plot(range(len(dates)), prices_regular, pen='r', name='Обычная цена')

        # Добавляем легенду
        plot_widget.addLegend()

        layout.addWidget(plot_widget)

