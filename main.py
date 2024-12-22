# Kelas Pemrograman Desktop B
# Tema = Laundry
# Anggota Kelompok :
# 230411100045 - Dani Subianto
# 230411100163 - Hengki Dwi Kurniawan
# 230411100017 - Wiwik Ainun Janah
# 230411100186 - Yasmin Azzahra
# 230411100001 - Intan Aulia Majid

import os
import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QDataWidgetMapper
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from Laundry import Ui_MainWindow
from PyQt6.QtCore import QDate

basedir = os.path.dirname(__file__)

db = QSqlDatabase("QSQLITE")
db.setDatabaseName(os.path.join("Data_Laundry.sqlite"))
db.open()

# main logic
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.ui.dateEdit.setDisplayFormat("dd/MM/yyyy")
        self.ui.dateEdit_2.setDisplayFormat("dd/MM/yyyy")
        
        self.ui.dateEdit.setDate(QDate.currentDate())
        self.ui.dateEdit_2.setDate(QDate.currentDate())

        self.load_data_pelanggan()
        self.load_data_transaksi()
        self.load_paket()

        self.ui.lineEdit_5.textChanged.connect(self.load_data_transaksi)
        self.ui.lineEdit_6.textChanged.connect(self.load_data_transaksi)
        self.ui.lineEdit_7.textChanged.connect(self.load_data_pelanggan)
        self.ui.lineEdit_8.textChanged.connect(self.load_data_pelanggan)

        self.ui.pushButton.clicked.connect(self.total_harga)

        self.ui.pushButton_2.clicked.connect(self.save)

        self.record_transaksi()
        self.record_pelanggan()
        self.record_paket()

        
    def total_harga(self):
        conn = sqlite3.connect("Data_Laundry.sqlite")
        cursor = conn.cursor()

        berat = self.ui.spinBox_5.value()
        if berat <= 0:
            QMessageBox.warning(self, "Peringatan", "Silahkan masukan berat cucian!!")
            return
        paket = self.ui.comboBox_2.currentText()
        if paket == "Pilih Paket":
            QMessageBox.warning(self, "Peringatan", "Silahkan pilih paket!!")
            return
        diskon = (self.ui.lineEdit_12.text())
        if int(diskon) > 100 or int(diskon) < 0:
            QMessageBox.warning(self, "Peringatan", "Diskon tidak boleh melebihi 100 dan kurang dari 0 !!")
        else:
            query = "SELECT HARGA FROM paket WHERE NAMA_PAKET = ?"
            cursor.execute(query,(paket,))
            result = cursor.fetchone()
            if result:
                total_harga = result[0] * berat
                if diskon != "0":
                    total_harga -= (total_harga * int(diskon) / 100)
                self.ui.lineEdit_4.setText(str(int(total_harga)))

        conn.close()
        
    def save(self):
        conn = sqlite3.connect("Data_Laundry.sqlite")
        cursor = conn.cursor()

        nama = self.ui.lineEdit.text()
        telepon = self.ui.lineEdit_2.text()
        alamat = self.ui.lineEdit_3.text()
        jk = ""
        if self.ui.radioButton.isChecked():
            jk += "Laki - Laki"
        elif self.ui.radioButton_2.isChecked():
            jk += "Perempuan"

        if not nama or not telepon or not alamat or not jk:
            QMessageBox.warning(self, "Peringatan", "Semua data harus diisi!")
            return

        query = "INSERT INTO pelanggan (NAMA, TELEPON, ALAMAT, JK) VALUES (?, ?, ?, ?)"

        cursor.execute(query,(nama, telepon, alamat, jk))

        pelanggan = cursor.lastrowid
        baju = self.ui.spinBox.value()
        celana = self.ui.spinBox_2.value()
        berat = self.ui.spinBox_5.value()
        paket = self.ui.comboBox_2.currentData()
        tgl_transaksi = self.ui.dateEdit.date().toPyDate()
        tgl_selesai = self.ui.dateEdit_2.date().toPyDate()
        diskon = self.ui.lineEdit_12.text()
        total_harga = self.ui.lineEdit_4.text()
        status = self.ui.comboBox.currentText()

        query_transaksi = """
        INSERT INTO transaksi (PELANGGAN_ID, TGL_TRANSAKSI, TGL_SELESAI, STATUS, JML_BAJU, JML_CELANA, TOTAL_HARGA, PAKET_ID, BERAT, DISKON)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query_transaksi, (pelanggan, tgl_transaksi, tgl_selesai, status, baju, celana, total_harga, paket, berat, diskon))

        conn.commit()
        conn.close()

        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()
        self.ui.lineEdit_3.clear()

        self.ui.spinBox.setValue(0)
        self.ui.spinBox_2.setValue(0)
        self.ui.spinBox_5.setValue(0)
        self.ui.comboBox_2.setCurrentIndex(0)
        self.ui.dateEdit.setDate(QDate.currentDate())
        self.ui.dateEdit_2.setDate(QDate.currentDate())
        self.ui.lineEdit_12.setText("0")
        self.ui.lineEdit_4.clear()
        
        self.load_data_pelanggan()
        self.load_data_transaksi()

        self.reload_record_transaksi()
        self.reload_record_pelanggan()

    def load_paket(self):
        conn = sqlite3.connect('Data_Laundry.sqlite')
        cursor = conn.cursor()

        query = "SELECT ID_PAKET, NAMA_PAKET FROM paket"
        cursor.execute(query)
        results = cursor.fetchall()


        self.ui.comboBox_2.clear()
        self.ui.comboBox_2.addItem("Pilih Paket", None)
        for row in results:
            self.ui.comboBox_2.addItem(row[1], row[0])

        conn.close()

    def load_data_pelanggan(self):
        conn = sqlite3.connect('Data_Laundry.sqlite')  
        cursor = conn.cursor()
        
        customer_name = self.ui.lineEdit_7.text().strip()
        customer_address = self.ui.lineEdit_8.text().strip()

        query = "SELECT ID_PELANGGAN, NAMA, TELEPON, JK, ALAMAT FROM pelanggan"
        params = []
        if customer_name:
            query += " WHERE NAMA LIKE ?"
            params.append(f"%{customer_name}%")
        if customer_address:
            query += " AND ALAMAT LIKE ?" if customer_name else " WHERE ALAMAT LIKE ?"
            params.append(f"%{customer_address}%")

        cursor.execute(query, params)
        results = cursor.fetchall()

        self.ui.tableWidget.setRowCount(len(results))
        self.ui.tableWidget.setColumnCount(5)  
        
        
        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                self.ui.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        conn.close()
        
    def load_data_transaksi(self):
        conn = sqlite3.connect('Data_Laundry.sqlite')
        cursor = conn.cursor()

        customer_name = self.ui.lineEdit_5.text().strip()
        status = self.ui.lineEdit_6.text().strip()

        query = """
            SELECT 
                t.ID_TRANSAKSI, 
                p.NAMA AS nama_pelanggan, 
                t.TGL_TRANSAKSI, 
                t.TGL_SELESAI,
                t.JML_BAJU, 
                t.BERAT, 
                t.JML_CELANA, 
                pa.NAMA_PAKET AS nama_paket,
                t.TOTAL_HARGA,
                t.STATUS,
                t.DISKON
            FROM transaksi AS t
            JOIN pelanggan AS p ON t.PELANGGAN_ID = p.ID_PELANGGAN
            JOIN paket AS pa ON t.PAKET_ID = pa.ID_PAKET
        """

        params = []
        if customer_name:
            query += " WHERE p.NAMA LIKE ?"
            params.append(f"%{customer_name}%")
        if status:
            query += " AND t.STATUS LIKE ?" if customer_name else " WHERE t.STATUS LIKE ?"
            params.append(f"%{status}%")

        cursor.execute(query, params)
        results = cursor.fetchall()

        self.ui.tableWidget_2.setRowCount(len(results))
        self.ui.tableWidget_2.setColumnCount(11)

        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                self.ui.tableWidget_2.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        conn.close()


    def record_transaksi(self):
        self.model_transaksi = QSqlTableModel(db=db)
        self.model_transaksi.setTable("transaksi")
        self.model_transaksi.select()

        self.mapper_transaksi = QDataWidgetMapper()
        self.mapper_transaksi.setModel(self.model_transaksi)

        self.mapper_transaksi.addMapping(self.ui.lineEdit_9, 0)
        self.mapper_transaksi.addMapping(self.ui.lineEdit_10, 1)
        self.mapper_transaksi.addMapping(self.ui.dateEdit_3, 2)
        self.mapper_transaksi.addMapping(self.ui.dateEdit_4, 3)
        self.mapper_transaksi.addMapping(self.ui.spinBox_3, 4)
        self.mapper_transaksi.addMapping(self.ui.spinBox_4, 5)
        self.mapper_transaksi.addMapping(self.ui.spinBox_6, 6)
        self.mapper_transaksi.addMapping(self.ui.lineEdit_22, 7)
        self.mapper_transaksi.addMapping(self.ui.lineEdit_20, 8)
        self.mapper_transaksi.addMapping(self.ui.lineEdit_21, 9)
        self.mapper_transaksi.addMapping(self.ui.lineEdit_11, 10)

        self.mapper_transaksi.toFirst()

        self.ui.pushButton_3.clicked.connect(self.mapper_transaksi.toPrevious)
        self.ui.pushButton_4.clicked.connect(self.mapper_transaksi.toNext)
        self.ui.pushButton_5.clicked.connect(self.save_changes_transaksi)

    def save_changes_transaksi(self):
        conn = sqlite3.connect("Data_Laundry.sqlite")
        cursor = conn.cursor()

        transaksiID = self.ui.lineEdit_9.text()
        pelanggan = self.ui.lineEdit_10.text()
        tgl_transaksi = self.ui.dateEdit_3.date().toPyDate()
        tgl_selesai = self.ui.dateEdit_4.date().toPyDate()
        berat = self.ui.spinBox_3.value()
        baju = self.ui.spinBox_4.value()
        celana = self.ui.spinBox_6.value()
        paket = self.ui.lineEdit_22.text()
        total_harga = self.ui.lineEdit_20.text()
        status = self.ui.lineEdit_21.text()
        diskon = self.ui.lineEdit_11.text()

        query_transaksi = """
        UPDATE transaksi SET PELANGGAN_ID = ?, TGL_TRANSAKSI = ?, TGL_SELESAI = ?, BERAT = ?, JML_BAJU = ?, JML_CELANA = ?, PAKET_ID = ?, TOTAL_HARGA = ?, STATUS = ?, DISKON = ?
        WHERE ID_TRANSAKSI = ?
        """
        cursor.execute(query_transaksi, (pelanggan, tgl_transaksi, tgl_selesai, berat, baju, celana, paket, total_harga, status, diskon, transaksiID))

        conn.commit()
        conn.close()

        self.load_data_transaksi()


    def record_pelanggan(self):
        self.model_pelanggan = QSqlTableModel(db=db)
        self.model_pelanggan.setTable("pelanggan")
        self.model_pelanggan.select()

        self.mapper_pelanggan = QDataWidgetMapper()
        self.mapper_pelanggan.setModel(self.model_pelanggan)

        self.mapper_pelanggan.addMapping(self.ui.lineEdit_13, 0)
        self.mapper_pelanggan.addMapping(self.ui.lineEdit_14, 1)
        self.mapper_pelanggan.addMapping(self.ui.lineEdit_15, 2)
        self.mapper_pelanggan.addMapping(self.ui.lineEdit_16, 4)
        self.mapper_pelanggan.addMapping(self.ui.textEdit, 3)

        self.mapper_pelanggan.toFirst()

        self.load_data_pelanggan

        self.ui.pushButton_6.clicked.connect(self.mapper_pelanggan.toPrevious)
        self.ui.pushButton_7.clicked.connect(self.mapper_pelanggan.toNext)
        self.ui.pushButton_8.clicked.connect(self.save_changes_pelanggan)

    def save_changes_pelanggan(self):
        conn = sqlite3.connect("Data_Laundry.sqlite")
        cursor = conn.cursor()

        pelangganID = self.ui.lineEdit_13.text()
        nama = self.ui.lineEdit_14.text()
        telepon = self.ui.lineEdit_15.text()
        jk = self.ui.lineEdit_16.text()
        alamat = self.ui.textEdit.toPlainText()

        query = "UPDATE pelanggan SET NAMA = ?, TELEPON = ?, ALAMAT = ?, JK = ? WHERE ID_PELANGGAN = ?"

        cursor.execute(query, (nama, telepon, alamat, jk, pelangganID))

        conn.commit()
        conn.close()

        self.load_data_pelanggan()


    def record_paket(self):
        self.model_paket = QSqlTableModel(db=db)
        self.model_paket.setTable("paket")
        self.model_paket.select()

        self.mapper_paket = QDataWidgetMapper()
        self.mapper_paket.setModel(self.model_paket)

        self.mapper_paket.addMapping(self.ui.lineEdit_17, 0)
        self.mapper_paket.addMapping(self.ui.lineEdit_18, 1)
        self.mapper_paket.addMapping(self.ui.lineEdit_19, 2)
        self.mapper_paket.addMapping(self.ui.textEdit_2, 3)

        self.mapper_paket.toFirst()

        self.ui.pushButton_9.clicked.connect(self.mapper_paket.toPrevious)
        self.ui.pushButton_10.clicked.connect(self.mapper_paket.toNext)
        self.ui.pushButton_11.clicked.connect(self.save_changes_paket)


    def save_changes_paket(self):
        conn = sqlite3.connect("Data_Laundry.sqlite")
        cursor = conn.cursor()

        paketID = self.ui.lineEdit_17.text()
        nama_paket = self.ui.lineEdit_18.text()
        harga = self.ui.lineEdit_19.text()
        deskripsi = self.ui.textEdit_2.toPlainText()

        query_paket = "UPDATE paket SET NAMA_PAKET = ?, HARGA = ?, DESKRIPSI = ? WHERE ID_PAKET = ?"

        cursor.execute(query_paket, (nama_paket, harga, deskripsi, paketID))

        conn.commit()
        conn.close()

    def reload_record_transaksi(self):
        self.model_transaksi.select()
        self.mapper_transaksi.toFirst()

    def reload_record_pelanggan(self):
        self.model_pelanggan.select()
        self.mapper_pelanggan.toFirst()


# main running
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
