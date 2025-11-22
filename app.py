import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import os

# ============================================================
# DATABASE AYARLARI
# ============================================================

# Not: Colab/Drive yolu kontrolü yerinde bırakılmıştır.
DB_PATH = "/content/drive/MyDrive/Colab Notebooks/to-do-list/tasks.db" if os.path.exists("/content/drive/MyDrive/Colab Notebooks/to-do-list") else "tasks.db"

@st.cache_resource
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        deadline TEXT,
        priority TEXT,
        progress INTEGER DEFAULT 0,
        is_completed INTEGER DEFAULT 0,
        created_at TEXT,
        completed_at TEXT,
        notified INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    return conn

conn = get_conn()

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

# Orijinal fonksiyonlar: add_task, fetch_tasks, update_task, delete_task, mark_complete, human_timedelta

def add_task(title, description, deadline, priority, progress):
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO tasks (title,description,deadline,priority,progress,created_at) VALUES (?,?,?,?,?,?)",
        (title, description, deadline, priority, progress, now),
    )
    conn.commit()

def fetch_tasks(where=None, params=()):
    q = "SELECT * FROM tasks"
    if where:
        q += " WHERE " + where
    # Tamamlananlar en sona, son tarih olmayanlar en başa (tamamlanmamışlar içinde)
    q += " ORDER BY is_completed, (CASE WHEN deadline IS NULL THEN 0 ELSE 1 END), deadline, priority DESC" 
    cur = conn.execute(q, params)
    return [dict(r) for r in cur.fetchall()]

def update_task(task_id, **fields):
    if not fields:
        return
    assignments = ", ".join([f"{k}=?" for k in fields.keys()])
    params = list(fields.values()) + [task_id]
    conn.execute(f"UPDATE tasks SET {assignments} WHERE id=?", params)
    conn.commit()

def delete_task(task_id):
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

def mark_complete(task_id, completed=True):
    if completed:
        now = datetime.utcnow().isoformat()
        conn.execute("UPDATE tasks SET is_completed=1, progress=100, completed_at=? WHERE id=?", (now, task_id))
    else:
        conn.execute("UPDATE tasks SET is_completed=0, progress=0, completed_at=NULL WHERE id=?", (task_id,))
    conn.commit()

def human_timedelta(td):
    days = td.days
    secs = td.seconds
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    parts = []
    if days: parts.append(f"{days} gün")
    if hours: parts.append(f"{hours} saat")
    if minutes: parts.append(f"{minutes} dk")
    if not parts: return "0 dk"
    return " ".join(parts)

def get_priority_color(priority):
    """Öncelik seviyesine göre renk/ikon döndürür."""
    if priority == "High":
        return "🔴 Yüksek"
    elif priority == "Medium":
        return "🟠 Orta"
    else:
        return "🟢 Düşük"

def format_date(date_str):
    """ISO tarih dizesini okunabilir hale getirir."""
    if not date_str:
        return "Belirtilmedi"
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d %b %Y")
    except:
        return date_str

# ============================================================
# UYGULAMA ARAYÜZÜ
# ============================================================

st.set_page_config(page_title="Streamlit To-Do", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 Streamlit Görev Yönetimi")

# Mobil uyum ve genel tasarım CSS
st.markdown("""
<style>

/* ========================================================== */
/* GENEL TASARIM (LIGHT + DARK UYUMLU) */
/* ========================================================== */

:root {
    --gradient-bg-light: linear-gradient(135deg, #74ABE2 0%, #5563DE 100%);
    --gradient-bg-dark: linear-gradient(135deg, #2E2E48 0%, #1A1A2E 100%);
    --card-bg-light: rgba(255, 255, 255, 0.6);
    --card-bg-dark: rgba(30, 30, 40, 0.6);
    --text-light: #1c1c1c;
    --text-dark: #f1f1f1;
}

/* BODY VE ARKA PLAN */
html, body {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: auto !important;
    background: var(--gradient-bg-light) !important;
    background-attachment: fixed !important;
    transition: background 0.4s ease;
}

/* Streamlit Dark Mode için otomatik değişim */
@media (prefers-color-scheme: dark) {
    html, body {
        background: var(--gradient-bg-dark) !important;
    }
}

/* Ana konteyner */
[data-testid="stAppViewContainer"] {
    overflow-y: visible !important;
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Blok konteyner */
.block-container {
    backdrop-filter: blur(18px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
    background-color: var(--card-bg-light) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 2.5rem !important;
    max-width: 1100px !important;
    margin: 2rem auto !important;
    transition: all 0.3s ease;
}

@media (prefers-color-scheme: dark) {
    .block-container {
        background-color: var(--card-bg-dark) !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
}

/* ========================================================== */
/* BAŞLIKLAR VE METİNLER */
/* ========================================================== */

h1 {
    font-size: 2.4rem !important;
    text-align: center !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1.5rem !important;
    color: var(--text-light) !important;
    transition: color 0.4s ease;
}
@media (prefers-color-scheme: dark) {
    h1 { color: var(--text-dark) !important; }
}

h2, h3, h4, p, label, div, span {
    color: var(--text-light) !important;
}
@media (prefers-color-scheme: dark) {
    h2, h3, h4, p, label, div, span { color: var(--text-dark) !important; }
}

/* ========================================================== */
/* GÖREV KARTLARI */
/* ========================================================== */

.task-card {
    border: 1px solid rgba(255,255,255,0.25);
    border-left: 6px solid var(--priority-color, #00BFFF);
    padding: 16px 20px;
    margin-bottom: 18px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    background-color: rgba(255,255,255,0.35);
}
@media (prefers-color-scheme: dark) {
    .task-card {
        background-color: rgba(40,40,60,0.6);
        box-shadow: 0 4px 10px rgba(0,0,0,0.25);
    }
}

.task-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 14px rgba(0,0,0,0.2);
}
.task-card.high { border-left-color: #FF5C93; }
.task-card.medium { border-left-color: #FFD166; }
.task-card.low { border-left-color: #06D6A0; }
.task-card.completed { border-left-color: #4ECDC4; opacity: 0.85; }

/* ========================================================== */
/* GRAFİKLER (ORTALAMA + FULLSCREEN BUTONU GİZLEME) */
/* ========================================================== */

div[data-testid="stPlotlyChart"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    background: transparent !important;
    padding: 1rem 0 !important;
    overflow: hidden !important;
}

/* Fullscreen ikonu gizle */
div[title="View fullscreen"] {
    display: none !important;
}

/* Plotly figure container hizası */
.js-plotly-plot .plotly {
    margin: 0 auto !important;
}

/* ========================================================== */
/* BUTONLAR */
/* ========================================================== */

button[kind="primary"] {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    transition: all 0.25s ease;
}
button[kind="primary"]:hover {
    transform: scale(1.03);
    box-shadow: 0 4px 14px rgba(0,0,0,0.3);
}

button[kind="secondary"] {
    background: rgba(255,255,255,0.2) !important;
    color: inherit !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}
button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.3) !important;
}

/* ========================================================== */
/* RESPONSIVE */
/* ========================================================== */

@media (max-width: 768px) {
    .block-container {
        padding: 1rem !important;
    }
    h1 { font-size: 1.8rem !important; }
    .task-card { padding: 14px !important; }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SİDEBAR
# ============================================================

st.sidebar.header("⚙️ Ayarlar ve Filtreler")
show_completed = st.sidebar.checkbox("Tamamlanan Görevleri Göster", value=True)
priority_filter = st.sidebar.multiselect("Öncelik Seviyesi", ["Low","Medium","High"], default=["Low","Medium","High"])
due_filter = st.sidebar.radio("Vade Durumu", ["Hepsi","Gecikenler","Bugün","7 Gün İçinde"], index=0)

# ============================================================
# GÖREV EKLEME FORMU
# ============================================================

st.subheader("➕ Yeni Görev Ekle")
with st.expander("Yeni Görev Formunu Aç"): # Formu varsayılan olarak kapalı hale getirerek ana görünümü temizledik
    with st.form("add_task_form", clear_on_submit=True):
        st.write("**Temel Bilgiler**")
        title = st.text_input("Görev Başlığı *", placeholder="Örn: Raporu bitir, Müşteriye mail at...")
        description = st.text_area("Açıklama", placeholder="Birden fazla satır ekleyebilirsin...", height=100)

        st.write("**Detaylar**")
        col1, col2, col3 = st.columns(3)
        with col1:
            priority = st.selectbox("Öncelik", ["Low","Medium","High"], index=2) # Varsayılan: High
        with col2:
            set_deadline = st.checkbox("Son tarih belirle", value=True) # Varsayılan: İşaretli
            # Takvim bileşenini her zaman render etme çözümü korunmuştur.
            deadline_input = st.date_input("Son tarih", value=date.today() + timedelta(days=1))
            deadline = deadline_input if set_deadline else None
        with col3:
            progress = st.slider("Tamamlanma (%)", 0, 100, 0, key="add_progress")

        st.markdown("---")
        submitted = st.form_submit_button("✅ Görevi Kaydet")
        
        if submitted:
            if not title.strip():
                st.error("Başlık boş olamaz.")
            else:
                try:
                    add_task(title.strip(), description.strip(), deadline.isoformat() if deadline else None, priority, progress)
                    st.success("Görev başarıyla eklendi! 🎉")
                    st.rerun()
                except Exception as e:
                    st.error(f"Veritabanı hatası: {e}")
                    
st.markdown("---")

# ============================================================
# GÖREVLERİN LİSTESİ
# ============================================================

tasks = fetch_tasks()
df = pd.DataFrame(tasks)
df_filtered = df.copy()

if df_filtered.empty:
    st.info("Henüz görev eklenmemiş. Lütfen yukarıdaki formu kullanarak bir görev ekleyin. ⬆️")
else:
    # Filtreleme mantığı
    if not show_completed:
        df_filtered = df_filtered[df_filtered["is_completed"] == 0]
        
    df_filtered = df_filtered[df_filtered["priority"].isin(priority_filter)]
    
    today = date.today()
    # Tarihleri kontrol edilebilir hale getir
    df_filtered["deadline_date"] = pd.to_datetime(df_filtered["deadline"], errors="coerce").dt.date
    deadlines = df_filtered["deadline_date"]

    if due_filter == "Gecikenler":
        df_filtered = df_filtered[(deadlines < today) & (df_filtered["is_completed"] == 0)]
    elif due_filter == "Bugün":
        df_filtered = df_filtered[deadlines == today]
    elif due_filter == "7 Gün İçinde":
        df_filtered = df_filtered[(deadlines >= today) & (deadlines <= (today + timedelta(days=7)))]
    # 'Hepsi' filtresi için ek bir koşul gerekmez
    
    
    st.subheader(f"📋 Görev Listesi ({len(df_filtered)} Görev)")
    
    if df_filtered.empty:
        st.info("Seçili filtrelere uygun görev bulunamadı.")
    else:
        # Görünümü iyileştirmek için görevler 2 sütunda listeleniyor
        task_cols = st.columns(2)
        
        for i, row in df_filtered.iterrows():
            tid = int(row["id"])
            col_index = i % 2
            
            # Kartın stilini belirle
            priority_class = row['priority'].lower()
            completed_class = " completed" if row["is_completed"] else ""
            card_class = f"task-card {priority_class}{completed_class}"

            # Görevi kart içerisinde göster
            with task_cols[col_index]:
                with st.container():
                    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                    
                    st.markdown(f"<div class='task-title'>{row['title']}</div>", unsafe_allow_html=True)
                    
                    desc = (row.get("description") or "").replace("\n", "  \n")
                    if desc:
                        st.markdown(f"<div class='task-description'>{desc}</div>", unsafe_allow_html=True)
                        
                    # Detaylar
                    st.markdown(f"<div class='task-info'>**Öncelik:** {get_priority_color(row['priority'])}</div>", unsafe_allow_html=True)
                    
                    deadline_display = format_date(row.get("deadline"))
                    st.markdown(f"<div class='task-info'>**Son Tarih:** {deadline_display}</div>", unsafe_allow_html=True)

                    # İlerleme Çubuğu ve Yüzde
                    progress_val = int(row.get("progress") or 0)
                    progress_col, percent_col = st.columns([4,1])
                    with progress_col:
                        st.progress(progress_val)
                    with percent_col:
                        st.markdown(f"<p style='font-size: 0.9em; margin-top: -10px; text-align: right;'>{progress_val}%</p>", unsafe_allow_html=True)
                    
                    # Aksiyon Butonları (Tek bir satırda toplandı)
                    btn_cols = st.columns(3)
                    
                    # Tamamlama/Geri Al Butonu
                    with btn_cols[0]:
                        if row["is_completed"]:
                            if st.button("↩️ Geri Al", key=f"undo_{tid}", use_container_width=True):
                                mark_complete(tid, completed=False)
                                st.rerun()
                        else:
                            if st.button("✔️ Tamamla", key=f"done_{tid}", type="primary", use_container_width=True):
                                mark_complete(tid, completed=True)
                                st.success("Görev tamamlandı! 🎉")
                                st.rerun()
                    
                    # Düzenle Butonu
                    with btn_cols[1]:
                        if st.button("✏️ Düzenle", key=f"edit_{tid}", use_container_width=True):
                            st.session_state["edit_id"] = tid
                            st.rerun()
                            
                    # Sil Butonu
                    with btn_cols[2]:
                        if st.button("🗑️ Sil", key=f"del_{tid}", type="secondary", use_container_width=True):
                            delete_task(tid)
                            st.warning("Görev silindi. 🗑️")
                            st.rerun()
                            
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True) # Sütunları temizle


# ============================================================
# GÖREV DÜZENLEME FORMU (Modal benzeri bir görünüm için expander)
# ============================================================

if "edit_id" in st.session_state:
    eid = st.session_state["edit_id"]
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (eid,)).fetchone()
    
    if row:
        st.markdown("---")
        st.subheader("✍️ Görevi Düzenle")
        
        # Streamlit'te modal olmadığı için bir expander içinde düzenleme formu daha iyi bir kullanıcı deneyimi sunar.
        with st.form(f"edit_form_{eid}"):
            st.info(f"Düzenlenen Görev ID: **{eid}** - Başlık: **{row['title']}**")
            
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                new_title = st.text_input("Başlık", value=row["title"])
                new_desc = st.text_area("Açıklama", value=row["description"] or "", height=100)
            
            with col_edit2:
                # Son tarih varsayılan değerleri
                default_dead = date.fromisoformat(row["deadline"]) if row["deadline"] else date.today()
                set_deadline = st.checkbox("Son tarih belirle", value=bool(row["deadline"]))
                new_dead = st.date_input("Son tarih", value=default_dead)
                
                # Öncelik varsayılan değeri
                priorities = ["Low","Medium","High"]
                default_priority_index = priorities.index(row["priority"] or "Low")
                new_priority = st.selectbox("Öncelik", priorities, index=default_priority_index)
                
                # İlerleme varsayılan değeri
                new_prog = st.slider("Tamamlanma (%)", 0, 100, int(row["progress"] or 0))

            st.markdown("---")
            col_btns = st.columns(3)
            with col_btns[0]:
                save = st.form_submit_button("💾 Kaydet ve Kapat", type="primary", use_container_width=True)
            with col_btns[1]:
                cancel = st.form_submit_button("❌ İptal", use_container_width=True)
            
            if save:
                if not new_title.strip():
                    st.error("Başlık boş olamaz.")
                else:
                    try:
                        update_task(
                            eid,
                            title=new_title.strip(),
                            description=new_desc.strip(),
                            deadline=new_dead.isoformat() if set_deadline else None,
                            priority=new_priority,
                            progress=int(new_prog),
                            is_completed=1 if int(new_prog) == 100 else 0, # İlerleme %100 ise tamamlandı olarak işaretle
                            completed_at=datetime.utcnow().isoformat() if int(new_prog) == 100 else None
                        )
                        st.success("Görev başarıyla güncellendi! ✅")
                    except Exception as e:
                        st.error(f"Güncelleme hatası: {e}")
                    del st.session_state["edit_id"]
                    st.rerun()
            
            if cancel:
                del st.session_state["edit_id"]
                st.rerun()
            
        st.markdown("---")

# ============================================================
# ANALİZ BÖLÜMÜ
# ============================================================

st.markdown("---")
st.subheader("📈 Görev Analizi")

if not df.empty:
    
    # Metrikler
    total = len(df)
    completed = len(df[df["is_completed"] == 1])
    
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("Toplam Görev", total, delta="Tüm zamanlar")
    with metric_cols[1]:
        st.metric("Tamamlanan", completed, delta=f"{(completed/total*100):.1f}%" if total else "0.0%")
    with metric_cols[2]:
        st.metric("Beklemede", total - completed)
    
    # Ortalama Tamamlanma Süresi
    durations = []
    for t in tasks:
        if t.get("completed_at") and t.get("created_at"):
            try:
                a = datetime.fromisoformat(t["created_at"])
                b = datetime.fromisoformat(t["completed_at"])
                durations.append(b - a)
            except:
                pass
    
    with metric_cols[3]:
        if durations:
            avg = sum((d.total_seconds() for d in durations)) / len(durations)
            avg_td = timedelta(seconds=avg)
            st.metric("Ortalama Tamamlanma Süresi", human_timedelta(avg_td))
        else:
            st.metric("Ortalama Tamamlanma Süresi", "N/A", delta="Tamamlanan görev yok")


    st.markdown("---")
    
    chart_cols = st.columns(2)
    
    # 1. Grafik: Öncelik Dağılımı
    with chart_cols[0]:
        fig_priority = px.pie(
            df, 
            names="priority", 
            title="Öncelik Dağılımı",
            color_discrete_map={'High':'red', 'Medium':'orange', 'Low':'green'}
        )
        st.plotly_chart(fig_priority, use_container_width=True)

    # 2. Grafik: Durum Dağılımı
    with chart_cols[1]:
        status_df = df.copy()
        status_df["Durum"] = status_df["is_completed"].apply(lambda x: "Tamamlandı" if x == 1 else "Beklemede")
        fig_status = px.pie(
            status_df, 
            names="Durum", 
            title="Tamamlanma Durumu",
            color_discrete_map={'Tamamlandı':'#00b300', 'Beklemede':'#4682b4'}
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
    st.markdown("---")