import re
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QTextEdit, QVBoxLayout, QWidget
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import cv2
import easyocr
from PIL import Image

class OCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Desktop App - Deteksi Kop Surat")
        self.setGeometry(100, 100, 500, 700)
        self.initUI()

    def initUI(self):
        # Layout Utama
        layout = QVBoxLayout()

        # Label untuk menampilkan gambar
        self.image_label = QLabel("Upload an image to extract text")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.image_label)

        # Tombol untuk memilih gambar
        self.upload_button = QPushButton("Select Image")
        self.upload_button.clicked.connect(self.select_image)
        layout.addWidget(self.upload_button)

        # Area teks untuk menampilkan hasil OCR
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Tombol untuk menjalankan OCR
        self.ocr_button = QPushButton("Run OCR")
        self.ocr_button.clicked.connect(self.run_ocr)
        layout.addWidget(self.ocr_button)

        # Tombol untuk deteksi kop surat
        self.header_button = QPushButton("Detect Header (Kop Surat)")
        self.header_button.clicked.connect(self.detect_header)
        layout.addWidget(self.header_button)

        # Label untuk menampilkan akurasi
        self.accuracy_label = QLabel("Accuracy: N/A")
        layout.addWidget(self.accuracy_label)

        # Widget utama
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_image(self):
        # Dialog untuk memilih file gambar
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)", options=options
        )
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))

    def run_ocr(self):
        if hasattr(self, 'image_path'):
            # Inisialisasi EasyOCR Reader
            reader = easyocr.Reader(['en', 'id'])  # Tambahkan bahasa sesuai kebutuhan
            result = reader.readtext(self.image_path)

            # Format hasil OCR
            extracted_text = "\n".join([text[1] for text in result])

            # Ambil akurasi dari hasil OCR
            accuracy = sum([text[2] for text in result]) / len(result) if result else 0

            # Tampilkan hasil OCR dan akurasi
            self.text_area.setText(extracted_text)
            self.accuracy_label.setText(f"Accuracy: {accuracy * 100:.2f}%")
        else:
            self.text_area.setText("Please select an image first!")

    def detect_header(self):
        if hasattr(self, 'image_path'):
            # Load gambar dan crop bagian atas (kop surat)
            img = cv2.imread(self.image_path)
            height, width = img.shape[:2]
            header_area = img[0:int(height * 0.5), 0:width]  # Ambil 50% area atas

            # Simpan area kop surat sementara
            header_path = "header_temp.jpg"
            cv2.imwrite(header_path, header_area)

            # OCR pada area kop surat
            reader = easyocr.Reader(['en', 'id'])
            result = reader.readtext(header_path)

            # Format hasil OCR
            header_text = "\n".join([text[1] for text in result])

            # Ambil akurasi dari hasil OCR
            accuracy = sum([text[2] for text in result]) / len(result) if result else 0

            # Tampilkan hasil header dan akurasi
            self.text_area.setText(f"Detected Header:\n{header_text}")
            self.accuracy_label.setText(f"Header Detection Accuracy: {accuracy * 100:.2f}%")

            # Tambahkan regex untuk identifikasi pola tertentu
            nama_perusahaan = re.search(r"(PT\.?\s\w+)", header_text)
            nomor_arsip = re.search(r"(\d{4}/[A-Z0-9]+/[A-Z]+/\d{4})", header_text)

            # Tampilkan hasil terstruktur
            self.text_area.append("\n--- Extracted Information ---")
            if nama_perusahaan:
                self.text_area.append(f"Nama Perusahaan: {nama_perusahaan.group(1)}")
            if nomor_arsip:
                self.text_area.append(f"Nomor Arsip: {nomor_arsip.group(1)}")
        else:
            self.text_area.setText("Please select an image first!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec_())
