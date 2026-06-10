import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. SYSTEM DESAIN FRONT-END (Dark Mode Optimization & Cognitive Typography)
# ==============================================================================
st.set_page_config(
    page_title="Strategic Briefing IPRLH 2025 | KLH",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS Kustom untuk Memaksa Pemuatan Tema Gelap yang Nyaman di Mata
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700&family=Inter:wght@400;500;600;700&display=swap');

        /* Konfigurasi Global Canvas - Dark Mode Background */
        .stApp {
            background-color: #0f172a; /* Slate Dark */
            color: #f8fafc; /* Light Text */
        }

        /* Tipografi Kognitif Struktural - Kontras Tinggi */
        h1, h2, h3 {
            font-family: 'Merriweather', serif;
            color: #38bdf8; /* Terang: Sky Blue / Cyan lembut untuk elemen penanda */
            letter-spacing: -0.02em;
            margin-bottom: 12px;
        }
        
        p, div, span, label {
            font-family: 'Inter', sans-serif;
        }

        /* Banner Atas Pembuat Kebijakan (Z-Layout Header) - Dark Optimized */
        .hero-banner {
            background-color: #1e293b; /* Kontras dengan background utama */
            padding: 32px;
            border-radius: 6px;
            color: #f8fafc;
            margin-bottom: 28px;
            border-left: 10px solid #f97316; /* Signature Ember Orange (Terang) */
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .hero-banner h1 { 
            color: #ffffff !important; 
            margin: 0; 
            font-size: 28px; 
            font-weight: 700;
        }
        .hero-banner p { 
            color: #38bdf8; 
            font-size: 12px; 
            margin-top: 6px; 
            text-transform: uppercase; 
            letter-spacing: 2px; 
            font-weight: 600;
        }

        /* Kontainer KPI Card Premium - Mode Gelap */
        .kpi-card-box {
            background: #1e293b; /* Card Dark Background */
            padding: 24px;
            border: 1px solid #334155;
            border-bottom: 4px solid #0ea5e9; /* Light Blue Accent */
            border-radius: 4px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .kpi-card-box.gap-highlight {
            border-bottom-color: #f97316; /* Orange Aksen Krisis */
        }
        .kpi-card-value {
            font-size: 34px;
            font-weight: 700;
            color: #f8fafc;
            font-family: 'Merriweather', serif;
            line-height: 1.2;
        }
        .kpi-card-label {
            font-size: 11px;
            color: #94a3b8; /* Muted Light */
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.75px;
            margin-bottom: 4px;
        }
        .kpi-card-sub {
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
        }

        /* Modifikasi Elemen Sidebar agar Selaras */
        [data-testid="stSidebar"] {
            background-color: #0b0f19;
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            font-size: 11px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #38bdf8 !important;
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
    if "github.com" in url_path and "/blob/" in url_path:
        url_raw = url_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    else:
        url_raw = url_path

    try:
        response = requests.get(url_raw, timeout=15)
        response.raise_for_status()
        excel_buffer = io.BytesIO(response.content)
        df = pd.read_excel(excel_buffer, sheet_name=0)
        
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
        st.error(f"Koneksi data terputus. Error: {e}")
        st.stop()

file_path_target = "https://github.com/jvon-creator/dashboard_iprlh/blob/main/Data_IPRLH_2025_Cleaned.xlsx"
df_main = load_validated_data(file_path_target)


# ==============================================================================
# 3. INTERACTIVE SLICER CONTROL (Sidebar Setup)
# ==============================================================================
st.sidebar.markdown("### 🎛️ SLICER DATA UTAMA")

list_pulau = ["-- Nasional (Tampilkan Semua) --"] + sorted(df_main['Pulau'].unique().tolist())
selected_pulau = st.sidebar.selectbox("Filter Wilayah Administrasi Pulau:", list_pulau)

list_cluster = ["-- Tampilkan Semua Klaster --"] + sorted(df_main['Cluster'].unique().tolist())
selected_cluster = st.sidebar.selectbox("Filter Klaster Intervensi Perilaku:", list_cluster)

df_filtered = df_main.copy()
if selected_pulau != "-- Nasional (Tampilkan Semua) --":
    df_filtered = df_filtered[df_filtered['Pulau'] == selected_pulau]
if selected_cluster != "-- Tampilkan Semua Klaster --":
    df_filtered = df_filtered[df_filtered['Cluster'] == selected_cluster]

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

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    val_iprlh = df_filtered['IPRLH'].mean() if not df_filtered.empty else 0
    cat_lbl = "Ramah" if val_iprlh >= 0.60 else ("Cukup Ramah" if val_iprlh >= 0.50 else "Kurang Ramah")
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-card-label">Rerata Capaian IPRLH</div>
            <div class="kpi-card-value">{val_iprlh:.2f}</div>
            <div class="kpi-card-sub">Kategori: <b style="color: #38bdf8;">{cat_lbl}</b></div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    val_k = df_filtered['Knowledge'].mean() if not df_filtered.empty else 0
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-card-label">Literasi (Knowledge)</div>
            <div class="kpi-card-value" style="color: #60a5fa;">{val_k:.2f}</div>
            <div class="kpi-card-sub">Tingkat Pemahaman Teori</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    val_p = df_filtered['Practice'].mean() if not df_filtered.empty else 0
    st.markdown(f"""
        <div class="kpi-card-box">
            <div class="kpi-card-label">Aksi Nyata (Practice)</div>
            <div class="kpi-card-value" style="color: #fbbf24;">{val_p:.2f}</div>
            <div class="kpi-card-sub">🚨 Bottleneck Perilaku Hulu</div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    val_gap = df_filtered['Gap_K_P'].mean() if not df_filtered.empty else 0
    st.markdown(f"""
        <div class="kpi-card-box gap-highlight">
            <div class="kpi-card-label" style="color: #f97316;">Kesenjangan (Gap K-P)</div>
            <div class="kpi-card-value" style="color: #f97316;">{val_gap:.2f}</div>
            <div class="kpi-card-sub">Masyarakat paham tetapi tidak aksi</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ==============================================================================
# 5. GRIDS HALAMAN WORKSPACE INTI (Split Layout 2 Kolom)
# ==============================================================================
col_left, col_right = st.columns([4, 3])

with col_left:
    st.markdown("### 📊 Pemetaan Distribusi Hubungan Perilaku (KAP)")
    tab_scatter, tab_bar = st.tabs(["🎯 Scatter Matriks Teori vs Aksi", "📈 Komparasi Komponen Per Pulau"])
    
    with tab_scatter:
        # Menggunakan template='plotly_dark' untuk otomatisasi teks terang
        fig_scatter = px.scatter(
            df_filtered, 
            x="Knowledge", 
            y="Practice",
            color="Cluster",
            size="IPRLH",
            hover_name="Provinsi",
            text="Provinsi",
            template="plotly_dark",
            color_discrete_map={
                'Cluster 1: Prioritas KIE Dasar': '#f87171',       # Soft Light Red
                'Cluster 2: Tahu tetapi Belum Praktik': '#fbbf24',  # Soft Light Amber
                'Cluster 3: Role Model / Akselerasi': '#34d399'    # Soft Light Emerald
            },
            labels={"Knowledge": "Skor Pengetahuan (Knowledge)", "Practice": "Skor Tindakan Nyata (Practice)"},
            range_x=[0.40, 0.95],
            range_y=[0.35, 0.65]
        )
        
        fig_scatter.add_trace(go.Scatter(
            x=[0.40, 0.70], y=[0.40, 0.70], 
            mode='lines', name='Kondisi Ideal (K=P)', 
            line=dict(color='#475569', dash='dot')
        ))
        
        fig_scatter.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig_scatter.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='#1e293b')))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with tab_bar:
        df_summary_pulau = df_main.groupby('Pulau')[['Knowledge', 'Attitude', 'Practice']].mean().reset_index()
        fig_bar = px.bar(
            df_summary_pulau, 
            x="Pulau", 
            y=["Knowledge", "Attitude", "Practice"],
            barmode="group",
            template="plotly_dark",
            labels={"value": "Nilai Indeks", "variable": "Komponen"},
            color_discrete_sequence=['#38bdf8', '#a78bfa', '#f59e0b']
        )
        fig_bar.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)


with col_right:
    st.markdown("### 📋 Rekomendasi Program Taktis Pemilahan Sampah")
    
    def dapatkan_instruksi_taktis(nama_cluster):
        if nama_cluster == 'Cluster 1: Prioritas KIE Dasar':
            return "⚠️ **KIE LITERASI DASAR:** Kampanye edukasi dasar pemisahan sampah organik/anorganik secara tatap muka langsung ke hulu rumah tangga."
        elif nama_cluster == 'Cluster 2: Tahu tetapi Belum Praktik':
            return "🛠️ **PENGUATAN INFRASTRUKTUR FISIK:** Setop brosur teori! Alihkan anggaran KIE untuk pembangunan TPS3R, Bank Sampah, dan logistik jemput terpilah."
        else:
            return "⭐ **REPLIKASI PROGRAM:** Berikan insentif fiskal daerah, publikasikan success story komunitas hulu, jadikan model rujukan studi banding nasional."

    if not df_filtered.empty:
        st.write(f"Menampilkan Top {min(5, len(df_filtered))} Wilayah dengan Urgensi Kerja Lapangan Tertinggi:")
        
        for idx, row in df_filtered.head(5).iterrows():
            warna_tepi = "#f87171" if row['Cluster'] == "Cluster 1: Prioritas KIE Dasar" else ("#fbbf24" if row['Cluster'] == "Cluster 2: Tahu tetapi Belum Praktik" else "#34d399")
            
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 16px; border-radius: 4px; border-left: 6px solid {warna_tepi}; margin-bottom: 14px; border-top: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 14px; color: #f8fafc;">{row['Provinsi']} ({row['Pulau']})</span>
                    <span style="font-weight: 700; color: #38bdf8; font-size: 14px;">IPRLH: {row['IPRLH']:.2f}</span>
                </div>
                <div style="font-size: 11px; color: #94a3b8; margin-top: 3px;">Nilai Kesenjangan Perilaku (Gap K-P): <b>{row['Gap_K_P']:.2f}</b></div>
                <div style="font-size: 12px; margin-top: 10px; color: #cbd5e0; line-height: 1.5;">{dapatkan_instruksi_taktis(row['Cluster'])}</div>
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

st.markdown("<p style='text-align: center; color: #64748b; font-size: 11px; margin-top: 10px;'>Pusat Data dan Informasi (Pusdatin) KLH | Standar UI Dashboard Laporan LHK Dark v3.5</p>", unsafe_allow_html=True)
