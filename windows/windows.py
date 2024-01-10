import db
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QAbstractItemView, QVBoxLayout, QHeaderView, \
    QFileDialog
from PyQt5 import uic
from PIL import Image
from PIL.ImageQt import ImageQt, QPixmap, QImage
import hashlib
from datetime import datetime, timedelta, date
from random import randint
import os


class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.authWindow = Authorization()
        self.authWindow.show()

    def exit(self):
        self.authWindow.show()
        self.close()


class Reservation(QMainWindow):

    def __init__(self, id):
        super().__init__()
        self.info = db.getRestaurantInfo(id)
        self.initUI()
        self.initActivity()

    def initUI(self):
        uic.loadUi('ui/reservation.ui', self)

        image = Image.open(self.info['image'])
        image = image.convert("RGBA")
        qim = ImageQt(image)

        self.pixmap = QPixmap(QImage(qim))
        self.imageLabel.setPixmap(
            self.pixmap)

        layout = QVBoxLayout(self)
        layout.addWidget(self.imageLabel)

        hours = int(datetime.now().strftime("%H"))
        hours = hours if hours % 2 != 0 else hours + 1
        days = 0 if hours <= 22 else 1
        hours = 9 if days != 0 else hours
        year = int('20' + datetime.now().strftime('%y'))
        month = int(datetime.now().strftime('%m'))
        day = int(datetime.now().strftime('%d'))

        for i in range(days, 3):
            n = 0
            if i == 0:
                time = datetime.now()
            else:
                time = datetime(year, month, day, 9)
            while 9 <= hours <= 21:
                delta = timedelta(hours=n, days=i)
                self.timeBox.addItem((time + delta).strftime('%d.%m.%y  %H:00'))
                n += 2
                hours += 2
            hours = 9
        self.resAmount()

        self.nameLabel.setText(self.info['name'])
        self.infoPlain.setPlainText(self.info['description'])
        self.infoPlain.setReadOnly(True)

    def initActivity(self):
        self.backButton.clicked.connect(self.backPage)
        self.timeBox.currentIndexChanged.connect(self.resAmount)
        self.resButton.clicked.connect(self.reservation)
        self.reviewsButton.clicked.connect(self.reviews)

    def backPage(self):
        self.userWindow = UserMain(username=username)
        self.userWindow.show()
        self.close()

    def reviews(self):
        self.reviewsWindow = Reviews(self.info['name'])
        self.reviewsWindow.show()
        self.close()

    def reservation(self):
        if amountRes == 'нет':
            QMessageBox.critical(self, 'Ошибка', 'Свободных мест нет. Выберите другое время.')
        else:
            userInfo = db.getUserInfo(username)
            db.addReservation(dateRes, hourRes, self.info['id'], userInfo['id'])
            QMessageBox.information(self, 'Регистрация прошла успешно!', "Вы забронировали столик на выбранное время.")
            self.resAmount()

    def resAmount(self):
        global hourRes, dateRes, amountRes
        hourRes = self.timeBox.currentText()[10:]
        dateRes = self.timeBox.currentText()[:8]
        id = self.info['id']
        amountRes = db.getTablesAmount(hourRes, dateRes, id)
        if amountRes == 0:
            amountRes = 'нет'
        self.amountLabel.setText('Количество свободных столиков: ' + amountRes)


class Reviews(QMainWindow):
    def __init__(self, name):
        super().__init__()
        self.initUI()
        self.initActivity()
        self.name = name
        self.restaurantId = db.getRestaurantInfoByName(name)['id']
        self.reviews = db.getReviewsInfo(self.restaurantId)

        self.label.setText(self.name)

        self.listWidget.setSpacing(6)

        for data in self.reviews:
            login = data['user_login']
            text = data['text']
            stars = str(data['stars'])
            self.listWidget.addItem(f"Пользователь {login}\n{text}\nОценка: {stars}")

    def initUI(self):
        uic.loadUi('ui/reviews.ui', self)

    def initActivity(self):
        self.backButton.clicked.connect(self.back)
        self.addReviewButton.clicked.connect(self.addReview)

    def back(self):
        self.resWindow = Reservation(self.restaurantId)
        self.resWindow.show()
        self.close()

    def addReview(self):
        text = self.lineEdit.text()
        stars = self.spinBox.value()
        login = username
        if text == '':
            QMessageBox.critical(self, 'Ошибка', 'Введите комментарий.')
        else:
            db.addReview(login, text, stars, self.restaurantId)
            QMessageBox.information(self, 'Успешно', "Ваш комментарий был добавлен.")
            self.revWindow = Reviews(self.name)
            self.revWindow.show()
            self.close()


class ReservationInfo(QMainWindow):
    def __init__(self, text, resId):
        super().__init__()
        self.initUI()
        self.initActivity()
        self.text = text
        self.resId = resId

        self.infoText.setText(self.text)

        self.infoLabel.setText('Информация о брони №' + str(self.resId))

    def initUI(self):
        uic.loadUi('ui/reservationInfo.ui', self)

    def initActivity(self):
        self.backButton.clicked.connect(self.backPage)
        self.deleteButton.clicked.connect(self.deleteReservation)

    def backPage(self):
        self.userWindow = UserMain(username)
        self.userWindow.show()
        self.close()

    def deleteReservation(self):
        db.deleteReservation(self.resId)
        QMessageBox.information(self, 'Успешно', 'Бронь удалена.')
        self.backPage()


class Authorization(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initActivity()

    def initUI(self):
        uic.loadUi('ui/auth.ui', self)

    def initActivity(self):
        self.loginButton.clicked.connect(self.signIn)
        self.registrationButton.clicked.connect(self.register)

    def register(self):
        self.regWindow = Registration()
        self.regWindow.show()
        self.close()

    def userWindow(self):
        self.userWindow = UserMain(username)
        self.userWindow.show()
        self.close()

    def adminWindow(self):
        self.adminWindow = UserAdmin(username)
        self.adminWindow.show()
        self.close()

    def signIn(self):
        global username
        username = self.loginInput.text()
        password = hashlib.sha256(self.passwordInput.text().encode('utf8')).hexdigest()
        userInfo = db.getUserInfo(username)

        if not userInfo:
            QMessageBox.critical(self, 'Ошибка', 'Введен неверный логин')
            return

        if password == userInfo['password'] and userInfo['is_admin'] == 0:
            self.userWindow()
        elif password == userInfo['password'] and userInfo['is_admin'] == 1:
            self.adminWindow()
        else:
            QMessageBox.critical(self, 'Ошибка', 'Введен неверный пароль')
            return


class Registration(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initActivity()

    def initUI(self):
        uic.loadUi('ui/registration.ui', self)

    def initActivity(self):
        self.loginButton.clicked.connect(self.signIn)
        self.authButton.clicked.connect(self.login)

    def login(self):
        self.authWindow = Authorization()
        self.authWindow.show()
        self.close()

    def signIn(self):
        login = self.loginInput.text()
        password = self.passwordInput.text()
        password2 = self.passwordInput2.text()

        if password != password2 or password == '' or login == '':
            QMessageBox.critical(self, 'Ошибка', 'Введены некорректные данные')
            return

        userInfo = db.getUserInfo(login)
        if userInfo:
            QMessageBox.critical(self, 'Ошибка', 'Пользователь с таким логином уже есть')
            return
        db.addUser(login, hashlib.sha256(password.encode("utf8")).hexdigest())
        QMessageBox.information(self, 'Успешно', 'Вы успешно зарегистрировались')
        self.login()


class UserAdmin(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.initUI()
        self.initActivity()
        self.reservationsInfo = db.getAdminReservationsInfo()
        self.username = username
        self.usernameLabel.setText(self.username)

        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['ID брони', 'ID Пользователя', 'ID Ресторана', 'Дата', 'Время'])
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 130)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 108)
        self.tableWidget.setColumnWidth(4, 100)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.checkReservations()

        self.loadInfo()

    def initUI(self):
        uic.loadUi('ui/main_admin.ui', self)

    def initActivity(self):
        self.logoutButton.clicked.connect(self.logout)
        self.searchButton.clicked.connect(self.search)
        self.addButton.clicked.connect(self.addRestaurant)
        self.deleteButton.clicked.connect(self.deleteRestaurant)

    def checkReservations(self):
        for item1 in self.reservationsInfo:
            item = item1['date']
            data1 = '20' + item.split('.')[2]
            data2 = item.split('.')[1] if int(item.split('.')[1]) >= 10 else item.split('.')[1][1]
            data3 = item.split('.')[0] if int(item.split('.')[0]) >= 10 else item.split('.')[0][1]
            if date(int(data1), int(data2), int(data3)) < date.today():
                db.deleteReservation(item1['id'])

    def logout(self):
        self.authWindow = Authorization()
        self.authWindow.show()
        self.close()

    def search(self):
        text = self.lineEdit.text()
        self.loadInfo(text)

    def loadInfo(self, query=""):
        self.clearTable()
        info = db.searchInfo(query)
        for i, row in enumerate(info):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(row[elem])))

    def clearTable(self):
        while self.tableWidget.rowCount():
            self.tableWidget.removeRow(0)

    def addRestaurant(self):
        self.addResWindow = RestaurantAdd(self.username)
        self.addResWindow.show()
        self.close()

    def deleteRestaurant(self):
        self.delResWindow = RestaurantDelete()
        self.delResWindow.show()
        self.close()


class RestaurantAdd(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.initUI()
        self.initActivity()
        self.restaurantInfo = db.getAdminRestaurantInfo()
        self.names = []
        self.descriptions = []
        self.addresses = []
        self.username = username

        self.hiddenLabel.setHidden(True)

        for item in self.restaurantInfo:
            self.names.append(item['name'])
            self.descriptions.append(item['description'])
            self.addresses.append(item['address'])

    def initUI(self):
        uic.loadUi('ui/add_restaurant.ui', self)

    def initActivity(self):
        self.selectImageButton.clicked.connect(self.selectImage)
        self.addRestaurantButton.clicked.connect(self.add)
        self.pushButton.clicked.connect(self.back)

    def selectImage(self):
        try:
            input_file_path = QFileDialog.getOpenFileName(None, 'Выбрать изображение', '',
                                                        "Image files (*.png, *.jpeg, *.jpg)")
            self.hiddenLabel.setText(input_file_path[0])
            self.selectImageButton.setText(input_file_path[0].split("/")[-1])
        except Exception as e:
            print(e)

    def back(self):
        self.user_admin = UserAdmin(self.username)
        self.user_admin.show()
        self.close()

    def generateRandomId(self):
        generated_id = randint(1000000, 9999999)
        if os.path.exists(f"images/{generated_id}.png"):
            return self.generateRandomId()
        return generated_id

    def add(self):
        name = self.selectNameLine.text()
        description = self.selectDescriptionLine.text()
        address = self.selectAddressLine.text()
        tables_amount = self.selectTablesSpin.value()
        image = self.hiddenLabel.text()

        if name not in self.names and name != '' and description not in self.descriptions and description != '' and \
                address not in self.addresses and address != '':
            output_file_path = f"images/{self.generateRandomId()}.png"
            data = open(image, "rb").read()
            with open(output_file_path, "wb") as f:
                f.write(data)
            db.addRestaurant(name, description, address, tables_amount, output_file_path)
            QMessageBox.information(self, 'Успешно', "Ресторан добавлен")
            self.back()



class RestaurantDelete(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initActivity()

    def initUI(self):
        uic.loadUi('ui/restaurant_delete.ui', self)

    def initActivity(self):
        self.backButton.clicked.connect(self.back)
        self.deleteButton.clicked.connect(self.delete)

    def back(self):
        self.adminWindow = UserAdmin(username)
        self.adminWindow.show()
        self.close()

    def delete(self):
        restaurantId = self.lineEdit.text()
        try:
            db.getRestaurantInfo(restaurantId)
            db.deleteRestaurant(restaurantId)
            QMessageBox.information(self, 'Успешно', 'Ресторан удален из базы данных.')
        except Exception:
            QMessageBox.critical(self, 'Ошибка', 'Ресторана с таким ID не существует')
        self.lineEdit.setText('')


class UserMain(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.initUI()
        self.initActivity()
        self.reservations = []
        self.userInfo = db.getUserInfo(username)
        self.clientReservations = db.getReservationsInfo(self.userInfo['id'])

        self.label.setText(username)

        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название', 'Адрес', 'Оценка'])
        self.tableWidget.setColumnWidth(0, 0)
        self.tableWidget.setColumnWidth(1, 230)
        self.tableWidget.setColumnWidth(2, 309)
        self.tableWidget.setColumnWidth(3, 100)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.cellClicked.connect(self.tablewidgetClicked)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.setFixedSize(700, 600)  ###везде фиксануть размер и мб одинаково переименовать кнопки

        self.reservationsList.setSpacing(5)

        self.load_restaurants()

        self.currentReservations()

    def initUI(self):
        uic.loadUi('ui/main_user.ui', self)

    def initActivity(self):
        self.logoutButton.clicked.connect(self.logout)
        self.reservationsList.itemClicked.connect(self.clickHandler)
        self.searchButton.clicked.connect(self.search)

    def currentReservations(self):
        for appointment in self.clientReservations:
            appId = appointment['id']
            appHour = appointment['hour']
            appDate = appointment['date']
            appName = db.getRestaurantInfo(appointment['restaurant_id'])['name']
            data1 = '20' + appDate.split('.')[2]
            data2 = appDate.split('.')[1] if int(appDate.split('.')[1]) >= 10 else appDate.split('.')[1][1]
            data3 = appDate.split('.')[0] if int(appDate.split('.')[0]) >= 10 else appDate.split('.')[0][1]
            print(int(data1), int(data2), int(data3))
            if date(int(data1), int(data2), int(data3)) < date.today():
                db.deleteReservation(appId)
                continue
            self.reservations.append([appName, appHour, appDate, appId])
        self.reservations = sorted(self.reservations, key=lambda x: x[2])
        for item in self.reservations:
            self.reservationsList.addItem(f'Заведение "{item[0]}" {item[2]} в {item[1]} \nНомер брони: {item[3]}')
        self.reservations.clear()

    def clickHandler(self, data):
        address = db.getRestaurantInfoByName(data.text().split('"')[1])['address']
        text = data.text().split('\n')[0] + '\nАдрес: ' + address
        id = data.text().split('брони: ')[1]
        self.infoWindow = ReservationInfo(text, id)
        self.infoWindow.show()
        self.close()

    def search(self):
        text = self.lineEdit.text()
        self.load_restaurants(text)

    def tablewidgetClicked(self, row):
        id = self.tableWidget.item(row, 0).text()
        self.reservation(id)

    def reviews(self, name):
        self.revWindow = Reviews(name)
        self.revWindow.show()
        self.close()

    def reservation(self, id):
        self.resWindow = Reservation(id)
        self.resWindow.show()
        self.close()

    def clear_table(self):
        while self.tableWidget.rowCount():
            self.tableWidget.removeRow(0)

    def load_restaurants(self, query=""):
        self.clear_table()
        rests = db.searchRestaurant(query)
        for i, row in enumerate(rests):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 3:
                    stars = int(round(row[elem]))
                    if stars == 0:
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem('нет'))
                    else:
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem(stars * "★" + (5 - stars) * "☆"))
                else:
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(row[elem])))

    def logout(self):
        self.authWindow = Authorization()
        self.authWindow.show()
        self.close()
