import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==============================================================================
# 1. KONFIGURASI UTAMA & ENGINES FRONT-END STYLE (Executive Theme)
# ==============================================================================
st.set_page_config(
    page_title="Dashboard BI Strategis IPRLH 2025",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS Kustom untuk Mengoptimalkan Pengalaman Visual Tingkat Menteri (KLH)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Reset Tipografi & Canvas Workspace */
        html, body, [data-testid="stSidebar"], .stApp {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
        }
        
        /* Banner Utama Atas Dashboard (Z-Layout Header) */
        .header-banner {
            background: linear-gradient(135deg, #1e3a8a, #0f172a);
            padding: 26px 24px;
            border-radius: 12px;
            color: white;
            margin-bottom: 24px;
            border: 1px solid #1e293b;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .header-banner h1 {
            font-size: 24px;
            font-weight: 700;
            color: #ffffff !important;
            margin: 0;
            letter-spacing: 0.5px;
        }
        .header-banner p {
            font-size: 13px;
            color: #94a3b8;
            margin-top: 6px;
            font-weight: 500;
        }
        
        /* Kustomisasi Visual KPI Block Card */
        div[data-testid="stMetricValue"] {
            font-size: 34px;
            font-weight: 700;
            color: #1e3a8a;
            line-height: 1;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            color: #64748b;
            letter-spacing: 0.75px;
            margin-bottom: 4px;
        }
        
        /* Panel Kontrol Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            font-size: 11px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #94a3b8 !important;
        }
        
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. DATA PIPELINE CONSUMER (ABS PATH EXCEL PARSER)
# ==============================================================================
@st.cache_data
def load_validated_data(file_path):
    # Validasi keberadaan file di path absolut Windows sebelum diproses sistem
    if not os.path.exists(file_path):
        st.error(f"""
            **Berkas Tidak Ditemukan!** Sistem gagal mendeteksi file pada jalur lokal komputer Anda:  
            `{file_path}`  
            
            *Saran Perbaikan:*
            1. Pastikan drive **C:** Anda dapat diakses dan tidak terkunci enkripsi sistem.
            2. Periksa kembali penulisan nama folder `\\Work\\Pelatihan\\Data Analyst\\Project\\`.
            3. Pastikan file hasil normalisasi data bersih `Data_IPRLH_2025_Cleaned.xlsx` sudah dipindahkan ke folder tersebut.
        """)
        st.stop()
        
    try:
        # Membaca data sheet tabular provinsi bersih
        df = pd.read_excel(file_path, sheet_name="Data_Clean_Provinsi")
            
        # Standardisasi nama kolom kementerian untuk keperluan visualisasi grafik internal
        column_mapping = {
            'No': 'No', 'Provinsi': 'Provinsi', 'Pulau_Region': 'Pulau',
            'IPRLH': 'IPRLH', 'Knowledge': 'Knowledge', 'Attitude': 'Attitude',
            'Practice': 'Practice', 'Kelas_IPRLH': 'Kelas_IPRLH',
            'Gap_Knowledge_Practice': 'Gap_K_P', 'Priority_Score': 'Priority_Score',
            'Cluster_KIE': 'Cluster'
        }
        df = df.rename(columns=column_mapping)
        return df
    except Exception as e:
        st.error(f"Sistem gagal mengonsumsi data tabular Excel. Pastikan nama sheet tidak diubah. Error: {e}")
        st.stop()

# Mengunci path absolut Windows menggunakan awalan 'r' (Raw String) untuk mematikan sifat escape character
file_path_target = r"https://github.com/jvon-creator/dashboard_iprlh/blob/main/Data_IPRLH_2025_Cleaned.xlsx"
df_dashboard = load_validated_data(file_path_target)


# ==============================================================================
# 3. BANNER HEADER UTAMA
# ==============================================================================
st.markdown("""
    <div class="header-banner">
        <h1>DASHBOARD MONITORING SEBARAN PERILAKU RAMAH LINGKUNGAN HIDUP (IPRLH) TA 2025</h1>
        <p>Aplikasi Penunjang Kebijakan Publik Pusdatin KLH — Segmentasi Klaster KIE Pemilahan Sampah Nasional</p>
    </div>
""", unsafe_allow_html=True)


# ==============================================================================
# 4. INTERACTIVE SLICER KONTROL SIDEBAR
# ==============================================================================
st.sidebar.markdown("### 🎛️ SLICER KONTROL DASHBOARD")

# Slicer Filter Wilayah / Pulau Besar
list_pulau = ["-- Tampilkan Seluruh Nasional --"] + sorted(df_dashboard['Pulau'].unique().tolist())
selected_pulau = st.sidebar.selectbox("Filter Wilayah / Pulau:", list_pulau)

# Slicer Filter Klaster Komunikasi KIE
list_cluster = ["-- Tampilkan Seluruh Klaster --"] + sorted(df_dashboard['Cluster'].unique().tolist())
selected_cluster = st.sidebar.selectbox("Filter Klaster Model KIE:", list_cluster)

# Memproses penyaringan data secara real-time
df_filtered = df_dashboard.copy()
if selected_pulau != "-- Tampilkan Seluruh Nasional --":
    df_filtered = df_filtered[df_filtered['Pulau'] == selected_pulau]
if selected_cluster != "-- Tampilkan Seluruh Klaster --":
    df_filtered = df_filtered[df_filtered['Cluster'] == selected_cluster]

# Pengurutan otomatis berdasarkan beban urgensi tertinggi (Priority Score Descending)
df_filtered = df_filtered.sort_values(by="Priority_Score", ascending=False)


# ==============================================================================
# 5. RINGKASAN DATA EKSEKUTIF (KPI CARDS GRID BLOCK)
# ==============================================================================
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    avg_iprlh = df_filtered['IPRLH'].mean() if not df_filtered.empty else 0
    cat_lbl = "Ramah" if avg_iprlh >= 0.60 else ("Cukup Ramah" if avg_iprlh >= 0.50 else "Kurang Ramah")
    st.metric(label="Rerata Indeks IPRLH", value=f"{avg_iprlh:.2f}", delta=f"Kategori: {cat_lbl}", delta_color="off")

with kpi_col2:
    avg_k = df_filtered['Knowledge'].mean() if not df_filtered.empty else 0
    st.metric(label="Rerata Pengetahuan (Teori)", value=f"{avg_k:.2f}", delta="Komponen Tertinggi")

with kpi_col3:
    avg_p = df_filtered['Practice'].mean() if not df_filtered.empty else 0
    st.metric(label="Rerata Praktik (Aksi Nyata)", value=f"{avg_p:.2f}", delta="🚨 Bottleneck Kritis", delta_color="inverse")

with kpi_col4:
    avg_gap = df_filtered['Gap_K_P'].mean() if not df_filtered.empty else 0
    st.metric(label="Rerata Kesenjangan Perilaku", value=f"{avg_gap:.2f}", delta="Target KIE Komunikasi", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)


# ==============================================================================
# 6. GRIDS LAYOUT WORKSPACE UTAMA (SPLIT 2 KOLOM OPTIMAL)
# ==============================================================================
col_left_chart, col_right_action = st.columns([4, 3])

# --- PANEL SEBELAH KIRI: GRAFIK INTERAKTIF LIVE RENDERING ---
with col_left_chart:
    st.markdown("### 📊 Pemetaan Distribusi Hubungan KAP")
    
    tab_scatter, tab_bottleneck = st.tabs(["🎯 Scatter Matriks Teori vs Aksi", "📈 Analisis Komponen Per Pulau"])
    
    with tab_scatter:
        # Scatter Plot interaktif pemetaan relasi Teori vs Aksi Nyata
        fig_scatter = px.scatter(
            df_filtered, 
            x="Knowledge", 
            y="Practice",
            color="Cluster",
            size="IPRLH",
            hover_name="Provinsi",
            text="Provinsi",
            color_discrete_map={
                'Cluster 1: Prioritas KIE Dasar': '#ef4444',       # Merah (KIE Dasar)
                'Cluster 2: Tahu tetapi Belum Praktik': '#f59e0b',  # Kuning (Fasilitasi Fisik)
                'Cluster 3: Role Model / Akselerasi': '#10b981'    # Hijau (Aman/Percontohan)
            },
            labels={"Knowledge": "Skor Pengetahuan (Knowledge)", "Practice": "Skor Tindakan Nyata (Practice)"},
            range_x=[0.40, 0.95],
            range_y=[0.35, 0.65]
        )
        
        # Penambahan garis bantu diagonal keselarasan perilaku X=Y
        fig_scatter.add_trace(go.Scatter(
            x=[0.40, 0.70], y=[0.40, 0.70], 
            mode='lines', name='Kondisi Ideal (K=P)', 
            line=dict(color='#94a3b8', dash='dash')
        ))
        
        fig_scatter.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig_scatter.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with tab_bottleneck:
        # Grouped Bar Chart komparasi capaian nilai komponen pembentuk indeks per pulau besar
        df_summary_pulau = df_dashboard.groupby('Pulau')[['Knowledge', 'Attitude', 'Practice']].mean().reset_index()
        fig_bar = px.bar(
            df_summary_pulau, 
            x="Pulau", 
            y=["Knowledge", "Attitude", "Practice"],
            barmode="group",
            labels={"value": "Nilai Indeks", "variable": "Komponen"},
            color_discrete_sequence=['#3b82f6', '#8b5cf6', '#f59e0b']
        )
        fig_bar.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# --- PANEL SEBELAH KANAN: MARIKS REKOMENDASI INTERVENSI OPERASIONAL ---
with col_right_action:
    st.markdown("### 📋 Rekomendasi Program Taktis Pemilahan Sampah")
    
    # Fungsi penentu kalimat instruksi kerja menteri dari klasifikasi data klaster
    def dapatkan_instruksi_taktis(nama_cluster):
        if nama_cluster == 'Cluster 1: Prioritas KIE Dasar':
            return "⚠️ **KIE LITERASI DASAR:** Kampanye tatap muka pengenalan klasifikasi sampah (Organik/Anorganik) langsung ke hulu rumah tangga."
        elif nama_cluster == 'Cluster 2: Tahu tetapi Belum Praktik':
            return "🛠️ **PENGUATAN INFRASTRUKTUR:** Stop penyebaran brosur teori! Alihkan anggaran untuk pembangunan fisik TPS3R, Bank Sampah, dan sistem pengangkutan terpilah."
        else:
            return "⭐ **REPLIKASI PROGRAM:** Berikan insentif fiskal daerah, publikasikan success story, jadikan model rujukan nasional."

    if not df_filtered.empty:
        st.write(f"Urutan Top {min(5, len(df_filtered))} Wilayah Prioritas Urgensi Kerja Lapangan:")
        
        # Loop pencetakan visual card kustom untuk penargetan taktis pimpinan
        for idx, row in df_filtered.head(5).iterrows():
            warna_badge = "#ef4444" if row['Cluster'] == "Cluster 1: Prioritas KIE Dasar" else ("#d97706" if row['Cluster'] == "Cluster 2: Tahu tetapi Belum Praktik" else "#10b981")
            
            st.markdown(f"""
            <div style="background-color: #ffffff; padding: 16px; border-radius: 8px; border-left: 6px solid {warna_badge}; margin-bottom: 14px; border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 14px; color: #1e293b;">{row['Provinsi']} ({row['Pulau']})</span>
                    <span style="font-weight: 700; color: #1e3a8a; font-size: 14px;">IPRLH: {row['IPRLH']:.2f}</span>
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Nilai Kesenjangan Perilaku (Gap K-P): <b>{row['Gap_K_P']:.2f}</b></div>
                <div style="font-size: 12px; margin-top: 10px; color: #334155; line-height: 1.4;">{dapatkan_instruksi_taktis(row['Cluster'])}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada data provinsi yang memenuhi kriteria filter saat ini.")


# ==============================================================================
# 7. EXPANDER LEMBAR DATA AUDIT TABULAR (COMPLIANCE VERIFICATION)
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🔍 Transparansi Audit Tabular Data")
with st.expander("Klik untuk melihat lembar data tabular lengkap 38 Provinsi hasil verifikasi"):
    df_show = df_filtered[['Provinsi', 'Pulau', 'IPRLH', 'Knowledge', 'Attitude', 'Practice', 'Gap_K_P', 'Cluster']].copy()
    df_show.columns = ['Nama Provinsi', 'Pulau/Region', 'Skor IPRLH', 'Knowledge (Teori)', 'Attitude (Sikap)', 'Practice (Aksi)', 'Gap K-P', 'Klaster Segmentasi KIE']
    
    st.dataframe(
        df_show.style.format({
            'Skor IPRLH': '{:.2f}', 'Knowledge (Teori)': '{:.2f}', 
            'Attitude (Sikap)': '{:.2f}', 'Practice (Aksi)': '{:.2f}', 'Gap K-P': '{:.2f}'
        }).background_gradient(subset=['Gap K-P'], cmap='Reds'),
        use_container_width=True
    )
