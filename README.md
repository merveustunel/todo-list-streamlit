<img width="1919" height="900" alt="image" src="https://github.com/user-attachments/assets/38dac195-7d34-446b-9dcd-f7826d953215" />

To-Do List App (Python · Streamlit · SQLite)

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)]()
[![SQLite](https://img.shields.io/badge/SQLite-DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)]()
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)]()

A modern **task management / to-do list web application** built with **Python**, **Streamlit**, and **SQLite**.
It allows users to add, filter, edit, delete and complete tasks while analyzing productivity with charts.


🇬🇧 ENGLISH OVERVIEW


PURPOSE  
This project is a task management (To-Do List) application designed to help users:

- Add tasks with title, description, priority, deadline, and progress  
- Edit, delete, or complete tasks  
- Filter by priority or due date  
- Track productivity with charts and metrics  
- Save tasks persistently using SQLite  

The app runs both **locally** and in **Google Colab**.

--------------------------------------------------------------------------------
🧩 MAIN FEATURES

- Add task  
- List tasks as cards  
- Edit task  
- Delete task  
- Mark as completed  
- Priority filtering  
- Deadline filtering  
- Analytics (charts + metrics)

--------------------------------------------------------------------------------
⚙️ TECH STACK

Backend:
- Python  
- SQLite (persistent storage)

Frontend / UI:
- Streamlit  
- Plotly (charts)  
- Pandas (data processing)

--------------------------------------------------------------------------------
🚀 RUNNING LOCALLY

1. (Optional) Create virtual environment:
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # Linux/macOS

2. Install dependencies:
   pip install streamlit pandas plotly

3. Start the app:
   streamlit run app.py

Open the provided local URL (http://localhost:8501).

--------------------------------------------------------------------------------
☁️ RUNNING IN GOOGLE COLAB

1. Open `to-do-app.ipynb` in Colab  
2. Run installation cell (Streamlit + ngrok)  
3. Run the launch cell  
4. Click the generated ngrok link  
5. Use the app from your browser  

--------------------------------------------------------------------------------
📁 PROJECT STRUCTURE

project/
│
├── app.py               # Main Streamlit app  
├── tasks.db             # SQLite database (auto-created)  
├── to-do-app.ipynb      # Colab notebook version  
└── README.md            # This file  


🇹🇷 TÜRKÇE AÇIKLAMA


🎯 PROJENİN AMACI  
Bu proje, Python ile geliştirilen bir **Görev Yönetim (To-Do List)** uygulamasıdır.  
Kullanıcılar;

- Görev ekleyebilir  
- Görevleri düzenleyebilir  
- Görevleri tamamlayabilir  
- Görevleri silebilir  
- Öncelik ve teslim tarihine göre filtreleyebilir  
- Görev analizlerini grafiklerle görüntüleyebilir  

Streamlit ile modern bir arayüz, SQLite ile kalıcı veri saklama sağlanır.

--------------------------------------------------------------------------------
🖥️ ARAYÜZ YAPISI

Sol Menü (Filtreleme):
- Öncelik filtreleme (Yüksek / Orta / Düşük)  
- Durum filtreleme (Tamamlanan / Bekleyen)  
- Tarih filtreleme (Bugün / 7 Gün / Gecikmiş)

Ana Alan (Görev Yönetimi):
- Yeni görev ekleme formu  
- Görev kartları  
- Düzenle / Sil / Tamamla butonları  

Analiz Alanı:
- Öncelik dağılım grafiği  
- Tamamlanan–bekleyen görev oranları  
- Toplam görev, başarı yüzdesi  

--------------------------------------------------------------------------------
▶️ KULLANIM (KISACA)

1. Gerekli kütüphaneleri yükle:  
   pip install streamlit pandas plotly

2. Uygulamayı çalıştır:  
   streamlit run app.py

3. Tarayıcıda açılan linkten kullanmaya başla.

--------------------------------------------------------------------------------
✔ SONUÇ  
Bu To-Do List uygulaması;  
- Modern bir UI  
- Basit CRUD işlemleri  
- Grafik tabanlı analiz  
- Kalıcı veritabanı desteği  

sunarak ders projeleri ve portföy çalışmaları için ideal bir örnek uygulamadır.


END OF README

