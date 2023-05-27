## MyPDF

README ini memberikan gambaran tentang kode yang terdapat dalam repositori ini. Kode ini mencakup fungsionalitas untuk pencarian dokumen, analisis teks, dan manipulasi file terkait dokumen PDF dan Word.

### Persyaratan

Sebelum menggunakan aplikasi ini, pastikan kamu memiliki kunci API OpenAI yang valid. Pastikan juga kamu telah menginstal semua dependensi yang diperlukan yang tercantum dalam file `requirements.txt`.

### Konfigurasi

Sebelum menjalankan aplikasi, kamu perlu mengatur kunci API OpenAI kamu sebagai variabel lingkungan dengan nama `OPENAI_API_KEY`.

## Manipulator

`manipulator.py` adalah skrip yang memungkinkan kamu untuk memproses file PDF atau Word, membagi kontennya menjadi file-file teks yang lebih kecil, dan menyimpannya dalam folder `docs`. Berikut adalah cara penggunaan `manipulator.py`:

```bash
python manipulator.py [--pdf <lokasi_file_pdf>] [--word <lokasi_file_word>] [--max-word <batas_kata>] [--clean] [--wrap]
```

Argumen yang dapat digunakan pada `manipulator.py` adalah:

- `--pdf`: Lokasi file PDF yang ingin diproses.
- `--max-word`: Batas kata maksimum per file. Semakin tinggi semakin baik, tetapi semakin boros. (default: 400).
- `--wrap`: Opsi untuk memilih apakah teks akan dibungkus menjadi paragraf dengan lebar 70 karakter (default: not wrapped).

Pastikan kamu telah mengatur kunci API OpenAI sebelum menjalankan `manipulator.py`.

## Main

`main.py` adalah skrip utama yang digunakan untuk menjalankan aplikasi pencarian dokumen. Berikut adalah cara penggunaan `main.py`:

```bash
python main.py [--model {chat,davinci}] [--temperature <temperature>]
```

Argumen yang dapat digunakan pada `main.py` adalah:

- `--model`: Pilihan model yang digunakan untuk generasi teks oleh OpenAI API (default: chat).
- `--temperature`: Suhu yang mengontrol tingkat ketidakteraturan dalam generasi teks (default: 0.0).

Pastikan kamu telah mengatur kunci API OpenAI sebelum menjalankan `main.py`.

Silakan lihat file kode untuk informasi lebih detail tentang implementasi masing-masing fungsionalitas.
