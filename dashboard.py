import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. SYSTEM DESAIN FRON-END (Custom CSS, Tipografi Kognitif & Teori Warna)
# ==============================================================================
st.set_page_config(
    page_title="Strategic Briefing IPRLH 2025 | KLH",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi Struktur CSS Kustom (Menghindari Tampilan Template Default Standar)
# Palette Utama: Midnight Forest Green (#004d40) & Rich Parchment (#fdfdfb)
# Aksen Risiko Estetika: Ember Orange (#d84315) sebagai penanda tingkat Gap kritis
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700&family=Inter:wght@400;500;600;700&display=swap');

        /* Konfigurasi Global Canvas */
        .stApp {
            background-color: #fdfdfb;
            color: #0f172a;
        }

        /* Tipografi Kognitif Struktural */
        h1, h2, h3 {
            font-family: 'Merriweather', serif;
            color: #004d40;
            letter-spacing: -0.02em;
            margin-bottom: 12px;
        }
        
        p, div, span, label {
            font-family: 'Inter', sans-serif;
        }

        /* Banner Atas Pembuat Kebijakan (Z-Layout Header) */
        .hero-banner {
            background-color: #004d40;
            padding: 32px;
            border-radius: 6px;
            color: #f1f8e9;
            margin-bottom: 28px;
            border-left: 10px solid #d84315; /* Signature Element */
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .hero-banner h1 { 
            color: #ffffff !important; 
            margin: 0; 
            font-size: 28px; 
            font-weight: 700;
        }
        .hero-banner p { 
            color: #a7f3d0; 
            font-size: 12px; 
            margin-top: 6px; 
            text-transform: uppercase; 
            letter-spacing: 2px; 
            font-weight: 600;
        }

        /* Kontainer KPI Card Premium */
        .kpi-card-box {
            background: #ffffff;
            padding: 24px;
            border: 1px solid #e2e8f0;
            border-bottom: 4px solid #004d40;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        .kpi-card-box.gap-highlight {
            border-bottom-color: #d84315;
        }
        .kpi-card-value {
            font-size: 34px;
            font-weight: 700;
            color: #004d40;
            font-family: 'Merriweather', serif;
            line-height: 1.2;
        }
        .kpi-card-label {
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.75px;
            margin-bottom: 4px;
        }
        .kpi-card-sub {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 4px;
        }

        /* Modifikasi Elemen Sidebar */
        [data-testid="stSidebar"] {
            background-color: #00251a;
        }
        [data-testid="stSidebar"] * {
            color: #f1f8e9 !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            font-size: 11px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #a7f3d0 !important;
        }

        /* Reset padding default streamlit */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. DATA PIPELINE ENGINE (Remote GitHub Excel Content Streamer)
# ==============================================================================
@st.cache_data
def load_validated_data(url_path):
    # Transformasi otomatis URL web interface GitHub menjadi URL Raw data biner
    if "github.com" in url_path and "/blob/" in url_path:
        url_raw = url_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    else:
        url_raw = url_path

    try:
        # Mengunduh data Excel biner lewat HTTP Stream
        response = requests.get(url_raw, timeout=15)
        response.raise_for_status()
        excel_buffer = io.BytesIO(response.content)
        
        # Mengonsumsi langsung data dari sheet bersih pertama hasil pembersihan
        df = pd.read_excel(excel_buffer, sheet_name=0)
        
        # Sinkronisasi pemetaan kolom internal dashboard
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
        st.error(f"Koneksi ke basis data GitHub terputus atau format sheet salah. Error: {e}")
        st.stop()

# Sumber data repositori daring (Sesuai dengan path target Anda)
file_path_target = "https://github.com/jvon-creator/dashboard_iprlh/blob/main/Data_IPRLH_2025_Cleaned.xlsx"
df_main = load_validated_data(file_path_target)


# ==============================================================================
# 3. INTERACTIVE SLICER CONTROL (Sidebar Setup)
# ==============================================================================
st.sidebar.markdown("### 🎛️ SLICER DATA UTAMA")

# Slicer Dropdown Filter Wilayah / Pulau Besar Indonesia
list_pulau = ["-- Nasional (Tampilkan Semua) --"] + sorted(df_main['Pulau'].unique().tolist())
selected_pulau = st.sidebar.selectbox("Filter Wilayah Administrasi Pulau:", list_pulau)

# Slicer Dropdown Filter Klaster Strategis Komunikasi KIE
list_cluster = ["-- Tampilkan Semua Klaster --"] + sorted(df_main['Cluster'].unique().tolist())
selected_cluster = st.sidebar.selectbox("Filter Klaster Intervensi Perilaku:", list_cluster)

# Logika Penyaringan Data Sinkron
df_filtered = df_main.copy()
if selected_pulau != "-- Nasional (Tampilkan Semua) --":
    df_filtered = df_filtered[df_filtered['Pulau'] == selected_pulau]
if selected_cluster != "-- Tampilkan Semua Klaster --":
    df_filtered = df_filtered[df_filtered['Cluster'] == selected_cluster]

# Pengurutan otomatis: Wilayah paling kritis diletakkan paling atas (Priority Score Descending)
df_filtered = df_filtered.sort_values(by="Priority_Score", ascending=False)


# ==============================================================================
# 4. IMPLEMENTASI HEADER & METRIK UTAMA (KPI CARDS GRID BLOCK)
# ==============================================================================
st.markdown("""
    <div class="hero-banner">
        <p>Strategic Executive Briefing — Pusat Data dan Informasi (Pusdatin)</p>
        <h1>Evaluasi Segmentasi Provinsi Berdasarkan Indeks Perilaku Ramah Lingkungan Hidup (IPRLH) 2025</h1>
    </div>
""", unsafe_allow_html=True)

# Susunan KPI Blok Berjejer Horizontal (Menerapkan Teori Grid)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    val_iprlh = df_filtered['IPRLH'].mean() if not df_filtered.empty else 0
    cat_lbl = "Ramah" if val_iprlh >= 0.60 else ("Cukup Ramah" if val_iprlh >= 0.50 else "Kurang Ramah")
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-card-label">Rerata Capaian IPRLH</div>
            <div class="kpi-card-value">{val_iprlh:.2f}</div>
            <div class="kpi-card-sub">Kategori: <b>{cat_lbl}</b></div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    val_k = df_filtered['Knowledge'].mean() if not df_filtered.empty else 0
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-card-label">Literasi (Knowledge)</div>
            <div class="kpi-card-value">{val_k:.2f}</div>
            <div class="kpi-card-sub">Tingkat Pemahaman Teori</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    val_p = df_filtered['Practice'].mean() if not df_filtered.empty else 0
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-card-label">Aksi Nyata (Practice)</div>
            <div class="kpi-card-value" style="color: #b45309;">{val_p:.2f}</div>
            <div class="kpi-card-sub">🚨 Bottleneck Perilaku Hulu</div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    # Menggunakan Ember Orange untuk Highlight Gap Perilaku Kritis Nasional
    val_gap = df_filtered['Gap_K_P'].mean() if not df_filtered.empty else 0
    st.markdown(f"""
        <div class="kpi-card-box gap-highlight">
            <div class="kpi-card-label" style="color: #d84315;">Kesenjangan (Gap K-P)</div>
            <div class="kpi-card-value" style="color: #d84315;">{val_gap:.2f}</div>
            <div class="kpi-card-sub">Masyarakat paham tapi tidak aksi</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ==============================================================================
# 5. GRIDS HALAMAN WORKSPACE INTI (Split Layout 2 Kolom)
# ==============================================================================
col_left, col_right = st.columns([4, 3])

# --- PANEL SEBELAH KIRI: VISUALISASI UTAMA INTERAKTIF (PLOTLY LIVE PLOTTING) ---
with col_left:
    st.markdown("### 📊 Pemetaan Distribusi Hubungan Perilaku (KAP)")
    
    tab_scatter, tab_bar = st.tabs(["🎯 Scatter Matriks Teori vs Aksi", "📈 Komparasi Komponen Per Pulau"])
    
    with tab_scatter:
        # Scatter Plot interaktif pemetaan relasi Knowledge vs Practice dengan warna kontras tinggi
        fig_scatter = px.scatter(
            df_filtered, 
            x="Knowledge", 
            y="Practice",
            color="Cluster",
            size="IPRLH",
            hover_name="Provinsi",
            text="Provinsi",
            color_discrete_map={
                'Cluster 1: Prioritas KIE Dasar': '#d84315',       # Merah Bata/Oranye Gelap (Kritis)
                'Cluster 2: Tahu tetapi Belum Praktik': '#ffb300',  # Kuning Amber (Warning)
                'Cluster 3: Role Model / Akselerasi': '#00695c'    # Deep Emerald (Aman/Role Model)
            },
            labels={"Knowledge": "Skor Pengetahuan (Knowledge)", "Practice": "Skor Tindakan Nyata (Practice)"},
            range_x=[0.40, 0.95],
            range_y=[0.35, 0.65]
        )
        
        # Tambahkan Garis Diagonal Keselarasan Perilaku Ideal (X = Y)
        fig_scatter.add_trace(go.Scatter(
            x=[0.40, 0.70], y=[0.40, 0.70], 
            mode='lines', name='Kondisi Ideal (K=P)', 
            line=dict(color='#cbd5e0', dash='dot')
        ))
        
        fig_scatter.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig_scatter.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with tab_bar:
        # Grouped Bar Chart komparasi capaian nilai komponen makro per pulau besar
        df_summary_pulau = df_main.groupby('Pulau')[['Knowledge', 'Attitude', 'Practice']].mean().reset_index()
        fig_bar = px.bar(
            df_summary_pulau, 
            x="Pulau", 
            y=["Knowledge", "Attitude", "Practice"],
            barmode="group",
            labels={"value": "Nilai Indeks", "variable": "Komponen"},
            color_discrete_sequence=['#0284c7', '#8b5cf6', '#ffb300'] # Teori Warna Harmonious
        )
        fig_bar.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# --- PANEL SEBELAH KANAN: MATRIKS OPERASIONAL REKOMENDASI INTERVENSI KIE MENTERI ---
with col_right:
    st.markdown("### 📋 Rekomendasi Program Taktis Pemilahan Sampah")
    
    # Fungsi penentu kalimat instruksi kerja menteri dari klasifikasi data klaster riil
    def dapatkan_instruksi_taktis(nama_cluster):
        if nama_cluster == 'Cluster 1: Prioritas KIE Dasar':
            return "⚠️ **KIE LITERASI DASAR:** Kampanye edukasi dasar pemisahan sampah organik/anorganik secara tatap muka langsung ke hulu rumah tangga."
        elif nama_cluster == 'Cluster 2: Tahu tetapi Belum Praktik':
            return "🛠️ **PENGUATAN INFRASTRUKTUR FISIK:** Setop brosur teori! Alihkan anggaran KIE untuk pembangunan TPS3R, Bank Sampah, dan logistik jemput terpilah."
        else:
            return "⭐ **REPLIKASI PROGRAM:** Berikan insentif fiskal daerah, publikasikan success story komunitas hulu, jadikan model rujukan studi banding nasional."

    if not df_filtered.empty:
        st.write(f"Menampilkan Top {min(5, len(df_filtered))} Wilayah dengan Urgensi Kerja Lapangan Tertinggi:")
        
        # Looping visual card kustom untuk instruksi taktis kebijakan
        for idx, row in df_filtered.head(5).iterrows():
            warna_tepi = "#d84315" if row['Cluster'] == "Cluster 1: Prioritas KIE Dasar" else ("#ffb300" if row['Cluster'] == "Cluster 2: Tahu tetapi Belum Praktik" else "#00695c")
            
            st.markdown(f"""
            <div style="background-color: #ffffff; padding: 16px; border-radius: 4px; border-left: 6px solid {warna_tepi}; margin-bottom: 14px; border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 14px; color: #1e293b;">{row['Provinsi']} ({row['Pulau']})</span>
                    <span style="font-weight: 700; color: #004d40; font-size: 14px;">IPRLH: {row['IPRLH']:.2f}</span>
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 3px;">Nilai Kesenjangan Perilaku (Gap K-P): <b>{row['Gap_K_P']:.2f}</b></div>
                <div style="font-size: 12px; margin-top: 10px; color: #334155; line-height: 1.5;">{dapatkan_instruksi_taktis(row['Cluster'])}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada data provinsi yang memenuhi kriteria kombinasi filter.")


# ==============================================================================
# 6. BAGIAN BAWAH: TRANSPARANSI TABULAR (AUDIT COMPLIANCE VERIFICATION)
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
with st.expander("🔍 DATA AUDIT: VERIFIED PROVINCIAL TABULAR MATRIX"):
    df_show = df_filtered[['Provinsi', 'Pulau', 'IPRLH', 'Knowledge', 'Attitude', 'Practice', 'Gap_K_P', 'Cluster']].copy()
    df_show.columns = ['Nama Provinsi', 'Pulau/Region', 'Skor IPRLH', 'Knowledge (Teori)', 'Attitude (Sikap)', 'Practice (Aksi)', 'Gap K-P', 'Klaster Segmentasi KIE']
    
    st.dataframe(
        df_show.style.format({
            'Skor IPRLH': '{:.2f}', 'Knowledge (Teori)': '{:.2f}', 
            'Attitude (Sikap)': '{:.2f}', 'Practice (Aksi)': '{:.2f}', 'Gap K-P': '{:.2f}'
        }),
        use_container_width=True
    )

st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top: 10px;'>Pusat Data dan Informasi (Pusdatin) KLH | Standar UI Dashboard Laporan LHK v3.2</p>", unsafe_allow_html=True)
