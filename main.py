from datetime import datetime, timedelta
import sys
import pandas as pd
from webbrowser import open
import MySQLdb
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from db_queries import *
from PyQt5.uic import loadUiType
import numpy as np

# from texttable import Texttable

# from GUICopy import Ui_MainWindow as Program

Program, _ = loadUiType('GUICopy.ui')

my_db = MySQLdb.connect(host='localhost', user='root', password='159753852456', db='rc_company')
my_db.set_character_set('utf8')


class MainApp(QMainWindow, Program):
    def __init__(self):
        super(MainApp, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)
        # self.showNormal()
        self.db = my_db
        self.cur = self.db.cursor()
        self.ui_changes()
        self.all_customers_table_changes()
        self.main_buttons()
        self.user_actions()
        self.all_sub_types()
        self.input_restrict()

        self.get_month()
        self.reset_sub()
        self.search_name_completer()

    # *******************************
    #   Buttons
    # *******************************

    def main_buttons(self):
        self.add_new.clicked.connect(self.new_customer)
        self.add_new.setShortcut('ENTER')
        self.new_customer_pb.clicked.connect(lambda: self.change_tab(order=0))
        self.all_customers_pb.clicked.connect(self.change_tab_to_all_customers)
        self.reg_sub_pb.clicked.connect(lambda: self.change_tab(order=2))
        self.edit_customer_pb.clicked.connect(lambda: self.change_tab(order=3))
        self.cancel.clicked.connect(lambda: self.clear_text())
        self.customer_search_pb.clicked.connect(self.search_by_id)
        self.save_customers_data.clicked.connect(self.save_csv)
        self.save_pill.clicked.connect(self.new_pill)
        self.edit_search_pb.clicked.connect(self.search_for_edit)
        self.save_edits_pb.clicked.connect(self.save_edits)

    # *******************************
    #   UI Changes
    # *******************************
    def ui_changes(self):
        self.mainTab.tabBar().setVisible(False)
        self.change_tab(order=0)
        self.all_sub.setChecked(True)
        self.single_customer_data.verticalHeader().show()
        self.today_date.setText(str(datetime.today().date()))

    def change_tab_to_all_customers(self):
        self.change_tab(order=1)
        # self.show_all_customers()
        self.filter_all_customers()
        self.sub_numbers_on_filter()

    def sub_numbers_on_filter(self):
        total = get_customers_total_number()
        total_txt = ' [ ' + str(total) + ' ] ' + 'كل المشتركين'

        active = get_customers_filtered_number(fltr='تم الدفع')
        active_txt = ' [ ' + str(active) + ' ] ' + 'تم تحصيل الاشتراك'

        inactive = get_customers_filtered_number(fltr='لم يتم الدفع')
        inactive_txt = ' [ ' + str(inactive) + ' ] ' + 'لم يتم تحصيل الاشتراك'
        self.all_sub.setText(total_txt)
        self.all_active_sub.setText(active_txt)
        self.all_inactive_sub.setText(inactive_txt)

    def all_customers_table_changes(self):
        self.all_customers.verticalHeader().hide()
        self.all_customers.setSortingEnabled(True)
        # Column size
        self.all_customers.setColumnWidth(0, 60)
        self.all_customers.setColumnWidth(1, 200)
        self.all_customers.setColumnWidth(2, 110)
        self.all_customers.setColumnWidth(3, 250)
        self.all_customers.setColumnWidth(4, 120)
        self.all_customers.setColumnWidth(5, 120)
        self.all_customers.setColumnWidth(6, 120)
        self.all_customers.setColumnWidth(7, 120)
        self.all_customers.setColumnWidth(8, 120)
        self.all_customers.setColumnWidth(9, 150)

        # Why here ?
        # self.id_calc()

    def search_name_completer(self):
        data = get_all_customers_data()
        # Getting only the names
        data = np.array(data)[:, 1]
        # Convert the np.array to list
        names = list(data)
        name_completer = QCompleter(names)
        name_completer.setFilterMode(Qt.MatchContains)
        self.search_name.setCompleter(name_completer)

    # *******************************
    #   User actions
    # *******************************
    def user_actions(self):
        self.new_customer_sub_type.currentTextChanged.connect(self.unit_price)
        self.new_customer_sub_type.currentTextChanged.connect(self.total_price)
        self.new_customer_sub_type.currentTextChanged.connect(self.special_sub)
        self.new_customer_sub_count.textChanged.connect(self.total_price)
        self.filter_changed()
        self.search_name.textChanged.connect(self.filter_customers_by_name)

    def special_sub(self):
        sub_type = self.new_customer_sub_type.currentText()
        if sub_type == 'حاله خاصه':
            self.new_customer_total.setReadOnly(False)
        else:
            self.new_customer_total.setReadOnly(True)

    def change_tab(self, order=0):
        self.mainTab.setCurrentIndex(order)

    def input_restrict(self):
        self.new_customer_sub_count.setValidator(QIntValidator())
        self.edit_c_sub_count.setValidator(QIntValidator())

    def filter_changed(self):
        self.all_sub.toggled.connect(self.filter_all_customers)
        self.all_active_sub.toggled.connect(self.filter_all_customers)
        self.all_inactive_sub.toggled.connect(self.filter_all_customers)

    # *******************************
    #      Clients
    # *******************************
    def id_calc(self):

        rowcount = get_last_id_by_branch(branch='بسيون')
        customer_id = int(rowcount) + 1 if rowcount else 110000
        return customer_id

    def new_customer(self):
        # Getting info from UI
        customer_id = self.id_calc()
        name = self.new_customer_name.text().strip()
        nickname = self.new_customer_nickname.text().strip()
        phone = self.new_customer_phone.text().strip()
        address = self.new_customer_address.text().strip()
        lank_mark = self.new_customer_landmark.text()
        national_id = self.new_customer_id.text()
        sub_type = self.new_customer_sub_type.currentText()
        sub_count = int(self.new_customer_sub_count.text().strip())
        added_time = str(datetime.today().date())
        months = self.new_customer_sub_month.text()
        active = 'تم الدفع'
        total = self.new_customer_total.text()

        if len(name) > 1:
            insert_new_customer(
                [customer_id, name, nickname, phone, address, lank_mark, national_id, sub_type, sub_count, total,
                 added_time, months, active])

            msg_box = QMessageBox()
            msg_box.setWindowTitle("Success")
            msg_box.setText("تم التسجيل بنجاح")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

            self.clear_text()

        else:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Error")
            msg_box.setText("يجب ادخال الاسم")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

    def clear_text(self):
        # Clear Text
        self.new_customer_name.setText('')
        self.new_customer_nickname.setText('')
        self.new_customer_phone.setText('')
        self.new_customer_address.setText('كفر جعفر - مركز بسيون - محافظه الغربيه')
        self.new_customer_landmark.setText('')
        self.new_customer_id.setText('')
        self.new_customer_sub_count.setText('1')

    # def show_all_customers(self):
    #
    #     customers_data = get_all_customers_data()
    #
    #     if customers_data:
    #         self.all_customers.setRowCount(0)
    #         self.all_customers.insertRow(0)
    #         for row, form in enumerate(customers_data):
    #             customer_id = form[0]
    #             full_name = (form[1] + f"({form[2]})") if len(form[2]) > 1 else form[1]
    #             phone = form[3]
    #             address = form[4] + f"({form[5]})" if len(form[5]) > 1 else form[4]
    #             national_id = form[6]
    #             sub_type = form[7] + f"({form[8]})"
    #             date = form[9]
    #             months = form[10]
    #             active = form[11]
    #
    #             # Total calculation
    #             total = 0
    #             s_type = form[7]
    #             s_count = form[8]
    #
    #             data = get_sub_price(sub=s_type)
    #             unit_price = int(data[0]) if data else 0
    #             if s_type == 'منزل' and s_count > 1:
    #                 if s_count == 2:
    #                     total = 25
    #                 elif s_count >= 3:
    #                     total = s_count * 10
    #             else:
    #                 total = s_count * unit_price
    #
    #             self.all_customers.setItem(row, 0, QTableWidgetItem(str(customer_id)))
    #             self.all_customers.setItem(row, 1, QTableWidgetItem(str(full_name)))
    #             self.all_customers.setItem(row, 2, QTableWidgetItem(str(phone)))
    #             self.all_customers.setItem(row, 3, QTableWidgetItem(str(address)))
    #             self.all_customers.setItem(row, 4, QTableWidgetItem(str(national_id)))
    #             self.all_customers.setItem(row, 5, QTableWidgetItem(str(sub_type)))
    #             self.all_customers.setItem(row, 6, QTableWidgetItem(str(total)))
    #             self.all_customers.setItem(row, 7, QTableWidgetItem(str(date)))
    #             self.all_customers.setItem(row, 8, QTableWidgetItem(str(months)))
    #             self.all_customers.setItem(row, 9, QTableWidgetItem(str(active)))
    #
    #             row_pos = self.all_customers.rowCount()
    #             self.all_customers.insertRow(row_pos)

    def filter_all_customers(self):
        customers_data = ''
        if self.all_sub.isChecked():
            customers_data = get_all_customers_data()
        elif self.all_active_sub.isChecked():
            customers_data = get_customers_with_filter(fltr='تم الدفع')
        elif self.all_inactive_sub.isChecked():
            customers_data = get_customers_with_filter(fltr='لم يتم الدفع')

        self.all_customers.setRowCount(0)
        self.all_customers.insertRow(0)
        if customers_data:
            for row, form in enumerate(customers_data):
                customer_id = form[0]
                full_name = (form[1] + f"({form[2]})") if len(form[2]) > 1 else form[1]
                phone = form[3]
                address = form[4] + f"({form[5]})" if len(form[5]) > 1 else form[4]
                national_id = form[6]
                sub_type = form[7] + f"({form[8]})"
                total_paid = form[9]
                date = form[10]
                months = form[11]
                active = form[12]

                self.all_customers.setItem(row, 0, QTableWidgetItem(str(customer_id)))
                self.all_customers.setItem(row, 1, QTableWidgetItem(str(full_name)))
                self.all_customers.setItem(row, 2, QTableWidgetItem(str(phone)))
                self.all_customers.setItem(row, 3, QTableWidgetItem(str(address)))
                self.all_customers.setItem(row, 4, QTableWidgetItem(str(national_id)))
                self.all_customers.setItem(row, 5, QTableWidgetItem(str(sub_type)))
                self.all_customers.setItem(row, 6, QTableWidgetItem(str(total_paid)))
                self.all_customers.setItem(row, 7, QTableWidgetItem(str(date)))
                self.all_customers.setItem(row, 8, QTableWidgetItem(str(months)))
                self.all_customers.setItem(row, 9, QTableWidgetItem(str(active)))

                row_pos = self.all_customers.rowCount()
                self.all_customers.insertRow(row_pos)

    def filter_customers_by_name(self):
        name = self.search_name.text()
        if len(name)>0:
            customers_data = get_customers_data_by_name(name)

            self.all_customers.setRowCount(0)
            self.all_customers.insertRow(0)
            if customers_data:
                for row, form in enumerate(customers_data):
                    customer_id = form[0]
                    full_name = (form[1] + f"({form[2]})") if len(form[2]) > 1 else form[1]
                    phone = form[3]
                    address = form[4] + f"({form[5]})" if len(form[5]) > 1 else form[4]
                    national_id = form[6]
                    sub_type = form[7] + f"({form[8]})"
                    total_paid = form[9]
                    date = form[10]
                    months = form[11]
                    active = form[12]

                    self.all_customers.setItem(row, 0, QTableWidgetItem(str(customer_id)))
                    self.all_customers.setItem(row, 1, QTableWidgetItem(str(full_name)))
                    self.all_customers.setItem(row, 2, QTableWidgetItem(str(phone)))
                    self.all_customers.setItem(row, 3, QTableWidgetItem(str(address)))
                    self.all_customers.setItem(row, 4, QTableWidgetItem(str(national_id)))
                    self.all_customers.setItem(row, 5, QTableWidgetItem(str(sub_type)))
                    self.all_customers.setItem(row, 6, QTableWidgetItem(str(total_paid)))
                    self.all_customers.setItem(row, 7, QTableWidgetItem(str(date)))
                    self.all_customers.setItem(row, 8, QTableWidgetItem(str(months)))
                    self.all_customers.setItem(row, 9, QTableWidgetItem(str(active)))

                    row_pos = self.all_customers.rowCount()
                    self.all_customers.insertRow(row_pos)
        else:
            self.filter_all_customers()

    def all_sub_types(self):
        data = get_all_sub_types()
        if data:
            self.new_customer_sub_type.clear()
            for name in data:
                self.new_customer_sub_type.addItem(name[0])
            self.unit_price()

    def unit_price(self):
        sub_type = self.new_customer_sub_type.currentText().strip()
        data = get_sub_price(sub=sub_type)
        if data:
            self.new_customer_unit_price.setText(str(data))

    def total_price(self):
        sub_type = self.new_customer_sub_type.currentText().strip()
        unit_price = int(self.new_customer_unit_price.text())
        s_count = self.new_customer_sub_count.text().strip()
        sub_count = 0 if s_count == '' else int(s_count)

        total = 0
        if sub_type == 'منزل' and sub_count > 1:
            if sub_count == 2:
                total = 25
            elif sub_count >= 3:
                total = sub_count * 10
        else:
            total = sub_count * unit_price

        self.new_customer_total.setText(str(total))

    def search_by_id(self):
        customer_id = self.customer_id.text()
        data = get_customer_data_by_id(customer_id=customer_id)
        # single_customer_data

        if data:
            customer_id = data[0]
            full_name = data[1] + f"({data[2]})"
            phone = data[3]
            address = data[4] + f"({data[5]})"
            national_id = data[6]
            sub_type = data[7] + f"({data[8]})"
            date = data[9]
            months = data[10]

            self.single_customer_data.setItem(0, 0, QTableWidgetItem(str(customer_id)))
            self.single_customer_data.setItem(1, 0, QTableWidgetItem(str(full_name)))
            self.single_customer_data.setItem(2, 0, QTableWidgetItem(str(phone)))
            self.single_customer_data.setItem(3, 0, QTableWidgetItem(str(address)))
            self.single_customer_data.setItem(4, 0, QTableWidgetItem(str(national_id)))
            self.single_customer_data.setItem(5, 0, QTableWidgetItem(str(sub_type)))
            self.single_customer_data.setItem(6, 0, QTableWidgetItem(str(date)))
            self.single_customer_data.setItem(7, 0, QTableWidgetItem(str(months)))

            s_type = data[7]
            s_count = int(data[8])

            data = get_sub_price(sub=s_type)
            unit_price = int(data)
            total = 0
            if s_type == 'منزل' and s_count > 1:
                if s_count == 2:
                    total = 25
                elif s_count >= 3:
                    total = s_count * 10
            else:
                total = s_count * unit_price
            self.customer_total.setText(str(total))

            # row = 0
            # for item in data:
            #     self.single_customer_data.setItem(row, 1, QTableWidgetItem(str(item)))
            #     row += 1

    def get_month(self):
        day = int(datetime.today().date().day)
        month = int(datetime.today().date().month)
        if day >= 25:
            # Get next month
            if month == 12:
                month = 1
            else:
                month += 1
        month_name = month_dict[month]
        self.new_customer_sub_month.setText(month_name)
        self.sub_month.clear()
        self.sub_month.addItem(month_name)

    def save_csv(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')[0]
        month = month_dict[int(datetime.today().date().month)]
        data = ''
        if self.all_sub.isChecked():
            data = get_all_customers_data()
        elif self.all_active_sub.isChecked():
            data = get_customers_with_filter(fltr='تم الدفع')
        elif self.all_inactive_sub.isChecked():
            data = get_customers_filtered_number(fltr='لم يتم الدفع')
        columns = ['الكود', 'الاسم', 'اسم الشهره', 'رقم التليفون', 'العنوان', 'علامه مميزة', 'الرقم القومي',
                   'وصف المكان', 'العدد', 'تاريخ اخر تحصيل', 'الشهر', 'نشط']

        # Convert to Data frame
        df = pd.DataFrame(list(data), columns=columns)

        # Get The total price for every customer
        all_total = []
        for row, col in enumerate(data):
            s_type = col[7]
            s_count = int(col[8])
            data = get_sub_price(s_type)
            unit_price = int(data[0]) if data else 0
            total = 0
            if s_type == 'منزل' and s_count > 1:
                if s_count == 2:
                    total = 25
                elif s_count >= 3:
                    total = s_count * 10
            else:
                total = s_count * unit_price
            all_total.append(total)
        # add Total to the details Dataframe
        # df['اجمالي المطلوب'] = all_total
        df.insert(9, 'اجمالي المطلوب', all_total)
        # Covert to excel
        writer = pd.ExcelWriter(f'{name}.xlsx')
        df.to_excel(writer, sheet_name=f'{month}', index=None)
        # Auto-adjust columns' width
        for column in df:
            column_width = max(df[column].astype(str).map(len).max(), len(column))
            col_idx = df.columns.get_loc(column)
            writer.sheets[month].set_column(col_idx, col_idx, column_width)
        # Save csv file
        writer.save()

    def new_pill(self):
        customer_id = self.customer_id.text()
        sub_month = self.sub_month.currentText()
        months = get_customer_one_attr(customer_id=customer_id, attr='months')
        months_list = months.split('+')

        if sub_month not in months_list:
            if 3 > len(months_list) != 0 and len(months_list[0]) > 0:
                months += f'+{sub_month}'
            elif len(months_list) == 3:
                months = f'{sub_month}+{months_list[0]}+{months_list[1]}'
            else:
                months = sub_month

        update_customer_one_attr(customer_id=customer_id, attr='months', value=months)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Success")
        msg_box.setText("تم التسجيل بنجاح")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

        # Clear input Data

    def customer_last_month(self):
        customer_id = self.customer_id.text()
        sub_month = self.sub_month.currentText()
        months = get_customer_one_attr(customer_id=customer_id, attr='months')
        months_list = months.split('+')
        last_month = months_list[-1]
        if last_month != sub_month:
            self.sub_month.addItem()

    def reset_sub(self):
        global reset_indicator
        day = int(datetime.today().date().day)

        if day >= 25 and reset_indicator:
            reset_all_customers_sub()
            reset_indicator = False
        if day < 25:
            reset_indicator = True

        self.db.commit()

    def search_for_edit(self):
        customer_id = self.search_edit_id.text()
        data = get_customer_data_by_id(customer_id=customer_id)
        # single_customer_data
        if data:
            name = data[1]
            nickname = data[2]
            phone = data[3]
            address = data[4]
            landmark = data[5]
            national_id = data[6]
            sub_type = data[7]
            sub_count = data[8]

            self.edit_c_name.setText(name)
            self.edit_c_nickname.setText(nickname)
            self.edit_c_phone.setText(phone)
            self.edit_c_address.setText(address)
            self.edit_c_landmark.setText(landmark)
            self.edit_c_nid.setText(national_id)
            self.edit_c_sub_type.addItem(sub_type)
            self.edit_c_sub_count.setText(str(sub_count))

    def save_edits(self):
        customer_id = self.search_edit_id.text()
        name = self.edit_c_name.text().strip()
        nickname = self.edit_c_nickname.text().strip()
        phone = self.edit_c_phone.text().strip()
        address = self.edit_c_address.text().strip()
        lank_mark = self.edit_c_landmark.text()
        national_id = self.edit_c_nid.text()
        sub_type = self.edit_c_sub_type.currentText()
        sub_count = int(self.edit_c_sub_count.text().strip())

        if len(name) > 1:
            update_customer_data(
                [name, nickname, phone, address, lank_mark, national_id, sub_type, sub_count, customer_id])

            # self.statusBar().showMessage(f"*تم التسجيل بنجاح* ")
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Success")
            msg_box.setText("تم تعديل البيانات")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

            self.search_edit_id.clear()
            self.edit_c_sub_type.clear()
            self.edit_c_name.clear()
            self.edit_c_nickname.clear()
            self.edit_c_phone.clear()
            self.edit_c_address.clear()
            self.edit_c_landmark.clear()
            self.edit_c_nid.clear()
            self.edit_c_sub_type.clear()
            self.edit_c_sub_count.clear()
        else:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Error")
            msg_box.setText("يجب ادخال الاسم")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()


if __name__ == '__main__':
    month_dict = {1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'ابريل', 5: 'مايو', 6: 'يونيو', 7: 'يوليه', 8: 'اغسطس',
                  9: 'سبتمبر', 10: 'اكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'}
    reset_indicator = False

    app = QApplication(sys.argv)
    window = MainApp()
    window.setWindowTitle('RC Clients System')
    window.setWindowIcon(QIcon(r'pics\\logo.ico'))
    window.show()
    app.exec_()
