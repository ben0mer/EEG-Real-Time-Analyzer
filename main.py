import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtChart import QCategoryAxis
from PyQt5.QtCore import QRunnable, QThreadPool, QTimer, QObject, pyqtSignal

class Worker(QRunnable):
    '''
    Worker thread
    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'PyQt5 PlotWidget ile Çoklu Grafikler ve Açıklamalar'
        self.width = 800
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Grafikleri içerecek olan QChart nesnesi
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.NoAnimation)
        # Grafikleri çizdirme ve açıklamaları ekleme
        for i in range(14):
            series = QLineSeries()
            offset = i * 10  # Her grafik için farklı bir offset değeri
            for j in range(10):
                series.append(j, random.random() * 10 + offset)
            self.chart.addSeries(series)

        for i in range(14):
            offset = i * 10
            offset_series = QLineSeries()
            for j in range(78):
                offset_series.append(j, offset)
            pen = QPen(Qt.gray)  # Soluk gri renk
            pen.setStyle(Qt.DashLine)  # Çizgi stili
            pen.setWidth(0.5)  # Çizgi kalınlığı
            offset_series.setPen(pen)
            self.chart.addSeries(offset_series)

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_last_value)
        # self.timer.start(10)  # Timer'ı her 1000 ms (1 saniye) tetikle
        # Eksenleri ayarlama
        self.axisX = QValueAxis()
        self.axisX.setRange(0, 500)
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.axisX.setGridLineVisible(False)

        self.axisY = QCategoryAxis()
        self.axisY.setRange(-10, 150)
        self.axisY.append("AF4", 0)
        self.axisY.append("F8", 10)
        self.axisY.append("F4", 20)
        self.axisY.append("FC6", 30)
        self.axisY.append("T8", 40)
        self.axisY.append("P8", 50)
        self.axisY.append("O2", 60)
        self.axisY.append("O1", 70)
        self.axisY.append("P7", 80)
        self.axisY.append("T7", 90)
        self.axisY.append("FC5", 100)
        self.axisY.append("F3", 110)
        self.axisY.append("F7", 120)
        self.axisY.append("AF3", 130)
        #Yazıların tam değerinin sol tarafında gözükmesi için
        self.axisY.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        # Diğer harfler için benzer şekilde ekleme yapabilirsiniz.
        self.chart.addAxis(self.axisY, Qt.AlignLeft)
        self.axisY.setGridLineVisible(False)
        for series in self.chart.series():
            series.attachAxis(self.axisX)
            series.attachAxis(self.axisY)

        # Legend'i etkinleştirme ve konumlandırma
        self.chart.legend().setVisible(False)

        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(chart_view)

        # Merkezi widget ayarla ve göster
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.show()
    def update_last_value(self):
        # Yeni gelen veri
        i = 1
        for series in self.chart.series():

            # Serideki mevcut nokta sayısı
            points_count = series.count()
            # Eğer seri zaten maksimum uzunluğa ulaştıysa, ilk noktayı kaldır
            if points_count >= 100:
                series.remove(0)
            # Serinin sonuna yeni noktayı ekle
            if points_count > 0:
                # Mevcut verileri kaydır
                for i in range(points_count):
                    
                    point = series.at(i)
                    series.replace(i, point.x() - 1, point.y())
            # Serinin sonuna yeni noktayı ekle
            series.append(100, 1)
            i+=1
            print(i)
    def start_update(self):
        # Worker'ı başlatmak için bu fonksiyonu kullanın
        worker = Worker(self.update_last_value)
        QThreadPool.globalInstance().start(worker)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    # Timer yerine start_update kullanarak worker'ı başlatın
    update_timer = QTimer()
    update_timer.timeout.connect(ex.start_update)
    update_timer.start(200)  # Her 1000 ms (1 saniye) tetikle
    sys.exit(app.exec_())
