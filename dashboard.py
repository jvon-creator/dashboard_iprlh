import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. STUDIO DESIGN SYSTEM (Custom CSS & Typography)
# ==============================================================================
st.set_page_config(
    page_title="Strategic IPRLH 2025 | KLH",
    page_icon="🌳",
    layout="wide"
)

# Injeksi Desain Khusus: Midnight Forest Green (#004d40) & Rich Parchment (#fdfdfb)
# Signature Risk: Ember Orange (#d84315) untuk penanda Gap Kritis
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700&family=Inter:wght@400;600&display=swap');

        /* Global Canvas */
        .stApp {
            background-color: #fdfdfb;
            color: #1a202c;
        }

        /* Typography */
        h1, h2, h3 {
            font-family: 'Merriweather', serif;
            color: #004d40;
            letter-spacing: -0.02em;
        }
        
        p, div, span {
            font-family: 'Inter', sans-serif;
        }

        /* The Hero Thesis: Banner Otoritatif */
        .hero-banner {
            background-color: #004d40;
            padding: 40px;
            border-radius: 4px;
            color: #f1f8e9;
            margin-bottom: 30px;
            border-left: 10px solid #d84315; /* Signature Element */
        }
        .hero-banner h1 { color: #ffffff; margin: 0; font-size: 32px; }
        .hero-banner p { opacity: 0.85; font-size: 14px; margin-top: 10px; text-transform: uppercase; letter-spacing: 2px; }

        /* Custom KPI Card: Styled like high-end report briefs */
        .kpi-box {
            background: #ffffff;
            padding: 24px;
            border: 1px solid #e2e8f0;
            border-bottom: 4px solid #004d40;
            border-radius: 2px;
        }
        .kpi-value {
            font-size: 36px;
            font-weight: 700;
            color: #004d40;
            font-family: 'Merriweather', serif;
        }
        .kpi-label {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 1px;
        }

        /* Sidebar Kustom */
        [data-testid="stSidebar"] {
            background-color: #00251a;
        }
        [data-testid="stSidebar"] * {
            color: #f1f8e9 !important;
        }

        /* Actionable Badge */
        .badge-red { background-color: #ffebee; color: #c62828; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 11px; }
        .badge-amber { background-color: #fff8e1; color: #ff8f00; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 11px; }
        .badge-green { background-color: #e8f5e9; color: #2e7d32; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 11px; }

    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA PIPELINE (GitHub Excel Parser)
# ==============================================================================
@st.cache_data
def load_validated_data(url_path):
    # Konversi URL GitHub biasa ke URL Raw biner
    if "github.com" in url_path and "/blob/" in url_path:
        url_raw = url_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    else:
        url_raw = url_path

    try:
        response = requests.get(url_raw, timeout=20)
        response.raise_for_status()
        excel_buffer = io.BytesIO(response.content)
        
        # Membaca data yang sudah dirapikan (Sheet: Data_Clean_Provinsi)
        df = pd.read_excel(excel_buffer, sheet_name=0)
        
        # Sinkronisasi penamaan kolom internal
        mapping = {
            'Pulau_Region': 'Pulau', 'Kelas_IPRLH': 'Status',
            'Gap_Knowledge_Practice': 'Gap_KP', 'Priority_Score': 'P_Score',
            'Cluster_KIE': 'Cluster'
        }
        df = df.rename(columns=mapping)
        return df
    except Exception as e:
        st.error(f"Kegagalan Akses Database Pusat: {e}")
        st.stop()

# Load data
file_path_target = "https://github.com/jvon-creator/dashboard_iprlh/blob/main/Data_IPRLH_2025_Cleaned.xlsx"
df_main = load_validated_data(file_path_target)

# ==============================================================================
# 3. INTERACTIVE SLICER (Sidebar Control)
# ==============================================================================
with st.sidebar:
    st.markdown("### STRATEGIC FILTERS")
    list_pulau = ["NASIONAL"] + sorted(df_main['Pulau'].unique().tolist())
    selected_pulau = st.selectbox("Wilayah Administrasi", list_pulau)
    
    list_cluster = ["SEMUA SEGMEN"] + sorted(df_main['Cluster'].unique().tolist())
    selected_cluster = st.selectbox("Klaster Intervensi KIE", list_cluster)

# Logic Filter
df_filtered = df_main.copy()
if selected_pulau != "NASIONAL":
    df_filtered = df_filtered[df_filtered['Pulau'] == selected_pulau]
if selected_cluster != "SEMUA SEGMEN":
    df_filtered = df_filtered[df_filtered['Cluster'] == selected_cluster]

# Sort by urgency
df_filtered = df_filtered.sort_values(by="P_Score", ascending=False)

# ==============================================================================
# 4. DASHBOARD RENDERING
# ==============================================================================

# Hero Header
st.markdown(f"""
    <div class="hero-banner">
        <p>Strategic Briefing | Menteri Lingkungan Hidup</p>
        <h1>Evaluasi Indeks Perilaku Ramah Lingkungan 2025</h1>
    </div>
""", unsafe_allow_html=True)

# Executive KPI Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">IPRLH Rerata</div><div class="kpi-value">{df_filtered["IPRLH"].mean():.2f}</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Literasi (Knowledge)</div><div class="kpi-value">{df_filtered["Knowledge"].mean():.2f}</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Implementasi (Practice)</div><div class="kpi-value">{df_filtered["Practice"].mean():.2f}</div></div>', unsafe_allow_html=True)
with kpi4:
    # Highlight Gap using signature Ember Orange
    gap_val = df_filtered["Gap_KP"].mean()
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Gap Teori-Aksi</div><div class="kpi-value" style="color:#d84315;">{gap_val:.2f}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Grid: Scatter Matrix & Strategy Cards
col_vis, col_strat = st.columns([1.8, 1.2])

with col_vis:
    st.markdown("### Analysis: Knowledge vs Practice Matrix")
    
    # Custom Styled Scatter Plot
    fig = px.scatter(
        df_filtered, 
        x="Knowledge", y="Practice",
        size="IPRLH", color="Cluster",
        hover_name="Provinsi", text="Provinsi",
        color_discrete_map={
            'Cluster 1: Prioritas KIE Dasar': '#d84315', 
            'Cluster 2: Tahu tetapi Belum Praktik': '#ffb300',
            'Cluster 3: Role Model / Akselerasi': '#00695c'
        },
        range_x=[0.4, 0.95], range_y=[0.35, 0.65]
    )
    
    # Add Diagonal Balance Line
    fig.add_trace(go.Scatter(
        x=[0.4, 0.7], y=[0.4, 0.7], mode='lines',
        name='Garis Keselarasan', line=dict(color='#cbd5e0', dash='dot')
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_strat:
    st.markdown("### Top Priority Recommendations")
    
    # Custom Strategy briefing cards using direct HTML for bespoke feel
    def get_brief(cluster):
        if "Cluster 1" in cluster: return "🚨 <b>KIE LITERASI DASAR:</b> Fokus pada pengenalan dasar jenis sampah hulu."
        if "Cluster 2" in cluster: return "🛠️ <b>INTERVENSI SARANA:</b> Setop sosialisasi teori. Fokus infrastruktur TPS3R."
        return "⭐ <b>REPLIKASI MODEL:</b> Jadikan percontohan benchmarking nasional."

    if not df_filtered.empty:
        for _, row in df_filtered.head(4).iterrows():
            border_color = "#d84315" if "Cluster 1" in row['Cluster'] else ("#ffb300" if "Cluster 2" in row['Cluster'] else "#00695c")
            st.markdown(f"""
                <div style="background: white; padding: 15px; border-left: 5px solid {border_color}; border-top: 1px solid #eee; border-right: 1px solid #eee; border-bottom: 1px solid #eee; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 700; color: #2d3748;">{row['Provinsi']}</span>
                        <span style="font-size: 11px; font-weight: 700; color: #004d40;">IPRLH: {row['IPRLH']:.2f}</span>
                    </div>
                    <div style="font-size: 12px; color: #4a5568; margin-top: 8px;">{get_brief(row['Cluster'])}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sila sesuaikan filter untuk melihat rekomendasi.")

# Footer Audit Table
st.markdown("---")
with st.expander("🔍 DATA AUDIT: VERIFIED PROVINCIAL MATRIX"):
    df_audit = df_filtered[['Provinsi', 'Pulau', 'IPRLH', 'Gap_KP', 'Cluster']].copy()
    st.dataframe(
        df_audit.style.background_gradient(subset=['Gap_KP'], cmap='YlOrRd'),
        use_container_width=True
    )

st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 10px;'>Pusat Data dan Informasi (Pusdatin) KLH | Standar Laporan Strategis Menteri v3.0</p>", unsafe_allow_html=True)
