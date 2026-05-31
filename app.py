"""
Katalog Lelang Properti — Streamlit App
"""

import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

# ── path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from utils.parser import parse_pdf
from utils.renderer import image_to_bytes, render_pages

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lelang Properti NTB & NTT",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Dark background */
.stApp {
    background: #0d0f14;
    color: #e8e9ed;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #13161f !important;
    border-right: 1px solid #1e2130;
}
[data-testid="stSidebar"] * {
    color: #c8cad4 !important;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1a1d28 0%, #13161f 100%);
    border: 1px solid #2a2d3e;
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
}
.metric-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #f0a500;
    line-height: 1;
}
.metric-sub {
    font-size: 11px;
    color: #4b5563;
    margin-top: 4px;
}

/* Property card */
.prop-card {
    background: #13161f;
    border: 1px solid #1e2130;
    border-radius: 16px;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
    height: 100%;
}
.prop-card:hover {
    border-color: #f0a500;
    transform: translateY(-2px);
}
.card-body {
    padding: 14px 16px 16px;
}
.card-title {
    font-size: 13px;
    font-weight: 700;
    color: #e8e9ed;
    margin-bottom: 4px;
    line-height: 1.3;
}
.card-address {
    font-size: 11px;
    color: #6b7280;
    margin-bottom: 10px;
    line-height: 1.4;
}
.card-price {
    font-family: 'Space Mono', monospace;
    font-size: 16px;
    font-weight: 700;
    color: #f0a500;
    margin-bottom: 2px;
}
.card-appraisal {
    font-size: 10px;
    color: #4b5563;
    margin-bottom: 10px;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-right: 4px;
    margin-bottom: 4px;
}
.badge-rumah    { background: #1d3a2f; color: #34d399; }
.badge-tanah    { background: #2d2a14; color: #fbbf24; }
.badge-ruko     { background: #1e2a3a; color: #60a5fa; }
.badge-gudang   { background: #2a1e30; color: #c084fc; }
.badge-other    { background: #1e1e1e; color: #9ca3af; }
.badge-onprocess { background: #1e1e2a; color: #818cf8; }
.badge-scheduled { background: #1a2e1a; color: #4ade80; }

.card-meta {
    font-size: 11px;
    color: #6b7280;
    border-top: 1px solid #1e2130;
    padding-top: 10px;
    margin-top: 8px;
    display: flex;
    gap: 12px;
}
.meta-item { display: flex; align-items: center; gap: 4px; }

/* Section header */
.section-header {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4b5563;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2130;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #13161f 0%, #1a1d28 50%, #13161f 100%);
    border: 1px solid #1e2130;
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(240,165,0,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 32px;
    font-weight: 800;
    color: #e8e9ed;
    margin-bottom: 6px;
    line-height: 1.1;
}
.hero-title span { color: #f0a500; }
.hero-sub {
    font-size: 14px;
    color: #6b7280;
}

/* Search */
.stTextInput input {
    background: #13161f !important;
    border: 1px solid #2a2d3e !important;
    border-radius: 10px !important;
    color: #e8e9ed !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stTextInput input:focus {
    border-color: #f0a500 !important;
    box-shadow: 0 0 0 2px rgba(240,165,0,0.15) !important;
}

/* Plotly chart bg */
.js-plotly-plot .plotly { background: transparent !important; }

/* Expander */
.streamlit-expanderHeader {
    background: #13161f !important;
    border: 1px solid #2a2d3e !important;
    border-radius: 10px !important;
    color: #e8e9ed !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2a2d3e; border-radius: 3px; }

/* Hide streamlit branding */
#MainMenu, footer { visibility: hidden; }

/* Sort/filter select */
.stSelectbox select, .stMultiSelect { background: #13161f !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── helpers ───────────────────────────────────────────────────────────────────
def fmt_rp(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    v = int(val)
    if v >= 1_000_000_000:
        return f"Rp {v/1_000_000_000:.2f} M".rstrip("0").rstrip(".")
    if v >= 1_000_000:
        return f"Rp {v/1_000_000:.0f} Jt"
    return f"Rp {v:,}"


def badge_type(t):
    cls = {
        "Rumah Tinggal": "rumah",
        "Tanah": "tanah",
        "Ruko": "ruko",
        "Gudang": "gudang",
    }.get(t, "other")
    return f'<span class="badge badge-{cls}">{t}</span>'


def badge_lelang(tanggal):
    if tanggal == "On Process":
        return '<span class="badge badge-onprocess">⏳ On Process</span>'
    return f'<span class="badge badge-scheduled">📅 {tanggal}</span>'


PDF_DEFAULT = ROOT / "Booklet.pdf"

# ── load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(pdf_path: str):
    return parse_pdf(pdf_path)


@st.cache_data(show_spinner=False)
def load_images(pdf_path: str):
    return render_pages(pdf_path, dpi=96)


def load_with_progress(pdf_path: str):
    """Load PDF data and images with animated progress UI."""
    import time

    cache_file = ROOT / "cache" / f"{Path(pdf_path).stem}_images.pkl"
    data_cached = st.session_state.get(f"data_loaded_{pdf_path}", False)
    img_cached  = cache_file.exists()

    # If data already cached just return silently
    if data_cached:
        return load_data(pdf_path), load_images(pdf_path) if img_cached else {}

    # ── loading screen ────────────────────────────────────────────────────────
    placeholder = st.empty()

    with placeholder.container():
        st.markdown(
            """
            <div style='text-align:center;padding:60px 20px 20px'>
                <div style='font-size:48px;margin-bottom:16px'>📄</div>
                <div style='font-size:22px;font-weight:800;color:#e8e9ed;margin-bottom:8px'>
                    Memproses Booklet PDF
                </div>
                <div style='font-size:13px;color:#6b7280;margin-bottom:32px'>
                    Ini hanya dilakukan sekali — hasil akan di-cache otomatis
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Step 1: Parse PDF only ────────────────────────────────────────────
        st.markdown(
            "<div style='text-align:center;font-size:13px;color:#f0a500;font-weight:600;"
            "margin-bottom:8px'>📋 Membaca & parsing data properti...</div>",
            unsafe_allow_html=True,
        )
        bar1 = st.progress(0, text="Membuka PDF...")

        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

        for i in range(0, 60, 3):
            time.sleep(0.03)
            bar1.progress(i, text=f"Scanning halaman... ({int(i/100*total_pages)}/{total_pages})")

        df_result = load_data(pdf_path)
        st.session_state[f"data_loaded_{pdf_path}"] = True

        bar1.progress(100, text=f"✅ {len(df_result)} properti ditemukan!")
        time.sleep(0.5)

    placeholder.empty()
    return df_result, {}


# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center;padding:16px 0 24px'>
            <div style='font-size:36px'>🏠</div>
            <div style='font-size:16px;font-weight:800;color:#e8e9ed;margin-top:4px'>Lelang Properti</div>
            <div style='font-size:11px;color:#4b5563;letter-spacing:1px'>NTB & NTT</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    pdf_path = str(PDF_DEFAULT)

    st.markdown("---")
    st.markdown('<div class="section-header">Filter</div>', unsafe_allow_html=True)

    df_all, images = load_with_progress(pdf_path)

    # Wilayah
    all_regions = sorted(df_all["region"].dropna().unique())
    sel_regions = st.multiselect("📍 Wilayah", all_regions, placeholder="Semua wilayah")

    # Tipe
    all_types = sorted(df_all["type"].dropna().unique())
    sel_types = st.multiselect("🏷️ Tipe Properti", all_types, placeholder="Semua tipe")

    # Harga
    min_h = int(df_all["harga_limit"].dropna().min())
    max_h = int(df_all["harga_limit"].dropna().max())
    harga_range = st.slider(
        "💰 Harga Limit (Juta Rp)",
        min_value=int(min_h / 1e6),
        max_value=int(max_h / 1e6) + 1,
        value=(int(min_h / 1e6), int(max_h / 1e6) + 1),
    )

    # Luas tanah
    lt_vals = df_all["luas_tanah"].dropna()
    if not lt_vals.empty:
        lt_range = st.slider(
            "📐 Luas Tanah (m²)",
            int(lt_vals.min()),
            int(lt_vals.max()),
            (int(lt_vals.min()), int(lt_vals.max())),
        )
    else:
        lt_range = (0, 99999)

    # Tanggal lelang
    show_scheduled = st.checkbox("📅 Tampilkan yang sudah ada jadwal lelang", value=False)

    st.markdown("---")
    st.markdown('<div class="section-header">Tampilan</div>', unsafe_allow_html=True)

    sort_opt = st.selectbox(
        "Urutkan",
        ["Harga Terendah", "Harga Tertinggi", "Luas Terbesar", "Wilayah A–Z"],
    )
    cards_per_row = st.selectbox("Kartu per baris", [2, 3, 4], index=1)
    show_images = st.checkbox("Tampilkan preview halaman PDF", value=False)

# ── apply filters ─────────────────────────────────────────────────────────────
df = df_all.copy()

if sel_regions:
    df = df[df["region"].isin(sel_regions)]
if sel_types:
    df = df[df["type"].isin(sel_types)]

df = df[
    (df["harga_limit"] >= harga_range[0] * 1e6)
    & (df["harga_limit"] <= harga_range[1] * 1e6)
]
df = df[
    df["luas_tanah"].isna()
    | ((df["luas_tanah"] >= lt_range[0]) & (df["luas_tanah"] <= lt_range[1]))
]
if show_scheduled:
    df = df[df["tanggal_lelang"] != "On Process"]

# sort
if sort_opt == "Harga Terendah":
    df = df.sort_values("harga_limit")
elif sort_opt == "Harga Tertinggi":
    df = df.sort_values("harga_limit", ascending=False)
elif sort_opt == "Luas Terbesar":
    df = df.sort_values("luas_tanah", ascending=False)
else:
    df = df.sort_values("region")

# ── hero + search ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
    <div class="hero-title">Katalog <span>Lelang Properti</span></div>
    <div class="hero-sub">NTB · NTT — Data dari Booklet Lelang KPKNL</div>
</div>
""",
    unsafe_allow_html=True,
)

search_query = st.text_input("🔍 Cari alamat, kawasan, atau fasilitas...", placeholder="contoh: Senggigi, Mandalika, garasi...")
if search_query:
    q = search_query.lower()
    df = df[
        df["address"].str.lower().str.contains(q, na=False)
        | df["title"].str.lower().str.contains(q, na=False)
        | df["fasilitas"].str.lower().str.contains(q, na=False)
        | df["jarak"].str.lower().str.contains(q, na=False)
        | df["region"].str.lower().str.contains(q, na=False)
    ]

# ── metric row ────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">Total Listing</div>
        <div class="metric-value">{len(df)}</div>
        <div class="metric-sub">dari {len(df_all)} total</div>
        </div>""",
        unsafe_allow_html=True,
    )

with m2:
    avg_h = df["harga_limit"].mean()
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">Rata-rata Harga</div>
        <div class="metric-value" style="font-size:20px">{fmt_rp(avg_h)}</div>
        <div class="metric-sub">harga limit</div>
        </div>""",
        unsafe_allow_html=True,
    )

with m3:
    min_h_val = df["harga_limit"].min()
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">Harga Termurah</div>
        <div class="metric-value" style="font-size:20px">{fmt_rp(min_h_val)}</div>
        <div class="metric-sub">harga limit</div>
        </div>""",
        unsafe_allow_html=True,
    )

with m4:
    scheduled = (df["tanggal_lelang"] != "On Process").sum()
    st.markdown(
        f"""<div class="metric-card">
        <div class="metric-label">Ada Jadwal Lelang</div>
        <div class="metric-value">{scheduled}</div>
        <div class="metric-sub">sudah terjadwal</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── charts ────────────────────────────────────────────────────────────────────
with st.expander("📊 Statistik & Grafik", expanded=False):
    c1, c2 = st.columns(2)

    with c1:
        region_counts = df["region"].value_counts().reset_index()
        region_counts.columns = ["Wilayah", "Jumlah"]
        fig1 = px.bar(
            region_counts,
            x="Jumlah",
            y="Wilayah",
            orientation="h",
            color="Jumlah",
            color_continuous_scale=["#1e2130", "#f0a500"],
            title="Sebaran per Wilayah",
        )
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af", size=11),
            title_font=dict(color="#e8e9ed", size=13),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(gridcolor="#1e2130"),
            xaxis=dict(gridcolor="#1e2130"),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        type_counts = df["type"].value_counts().reset_index()
        type_counts.columns = ["Tipe", "Jumlah"]
        COLORS = ["#f0a500", "#34d399", "#60a5fa", "#c084fc", "#f87171"]
        fig2 = px.pie(
            type_counts,
            names="Tipe",
            values="Jumlah",
            title="Komposisi Tipe Properti",
            color_discrete_sequence=COLORS,
            hole=0.5,
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af", size=11),
            title_font=dict(color="#e8e9ed", size=13),
            legend=dict(font=dict(color="#9ca3af")),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Price histogram
    fig3 = px.histogram(
        df.dropna(subset=["harga_limit"]),
        x=df.dropna(subset=["harga_limit"])["harga_limit"] / 1e6,
        nbins=30,
        title="Distribusi Harga Limit (Juta Rp)",
        color_discrete_sequence=["#f0a500"],
    )
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af", size=11),
        title_font=dict(color="#e8e9ed", size=13),
        xaxis=dict(title="Harga (Juta Rp)", gridcolor="#1e2130"),
        yaxis=dict(title="Jumlah", gridcolor="#1e2130"),
        margin=dict(l=0, r=0, t=40, b=0),
        bargap=0.05,
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── card grid ─────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="section-header">Menampilkan {len(df)} Properti</div>',
    unsafe_allow_html=True,
)

if df.empty:
    st.markdown(
        """
        <div style='text-align:center;padding:60px 20px;color:#4b5563'>
            <div style='font-size:48px'>🏚️</div>
            <div style='font-size:16px;margin-top:12px'>Tidak ada properti yang cocok dengan filter ini</div>
        </div>
    """,
        unsafe_allow_html=True,
    )
else:
    rows = [df.iloc[i : i + cards_per_row] for i in range(0, len(df), cards_per_row)]

    for row_df in rows:
        cols = st.columns(cards_per_row)
        for col, (_, row) in zip(cols, row_df.iterrows()):
            with col:
                # Image preview
                if show_images and images:
                    page_img = images.get(row["page"])
                    if page_img:
                        # crop bottom third (contacts) for cleaner look
                        w, h = page_img.size
                        cropped = page_img.crop((0, 0, w, int(h * 0.72)))
                        img_bytes = image_to_bytes(cropped, quality=70)
                        st.image(img_bytes, use_container_width=True)

                # Card body
                luas_info = ""
                if row["luas_tanah"]:
                    luas_info = f"🏔️ {int(row['luas_tanah'])} m²"
                    if row["luas_bangunan"] and not pd.isna(row["luas_bangunan"]):
                        luas_info += f" / 🏗️ {int(row['luas_bangunan'])} m²"

                st.markdown(
                    f"""
                    <div class="prop-card">
                        <div class="card-body">
                            <div class="card-title">{row['title']}</div>
                            <div class="card-address">📍 {row['address'] or row['region']}</div>
                            <div class="card-price">{fmt_rp(row['harga_limit'])}</div>
                            <div class="card-appraisal">Appraisal: {fmt_rp(row['harga_appraisal'])}</div>
                            <div>
                                {badge_type(row['type'])}
                                {badge_lelang(row['tanggal_lelang'])}
                            </div>
                            <div class="card-meta">
                                {f'<div class="meta-item">{luas_info}</div>' if luas_info else ''}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Detail expander
                with st.expander("Lihat detail"):
                    if row["jarak"]:
                        st.markdown("**🗺️ Jarak ke Landmark**")
                        for j in row["jarak"].split(" | "):
                            st.markdown(f"- {j}")
                    if row["fasilitas"]:
                        st.markdown("**✅ Fasilitas**")
                        for f in row["fasilitas"].split(", "):
                            st.markdown(f"- {f}")
                    st.markdown(f"**📖 Halaman PDF:** {row['page']}")
                    if show_images and images:
                        full_img = images.get(row["page"])
                        if full_img:
                            st.image(image_to_bytes(full_img, quality=85), use_container_width=True)

# ── footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style='text-align:center;padding:40px 0 20px;color:#2a2d3e;font-size:11px;letter-spacing:1px'>
    KATALOG LELANG PROPERTI · NTB & NTT · DATA DARI BOOKLET PDF
</div>
""",
    unsafe_allow_html=True,
)