import re
import pdfplumber
import pandas as pd
from pathlib import Path


def parse_price(text):
    """Extract integer price from Rp string."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else None


def parse_luas(text):
    """Extract luas tanah and luas bangunan from 'Lt / Lb : X m2 / Y m2'."""
    if not text:
        return None, None
    m = re.search(r"Lt\s*/\s*Lb\s*:\s*([\d,\.]+)\s*m2\s*/\s*([\d,\.]+)\s*m2", text, re.IGNORECASE)
    if m:
        lt = int(re.sub(r"[^\d]", "", m.group(1)))
        lb = int(re.sub(r"[^\d]", "", m.group(2)))
        return lt, lb
    # tanah only
    m2 = re.search(r"Lt\s*:\s*([\d,\.]+)\s*m2", text, re.IGNORECASE)
    if m2:
        lt = int(re.sub(r"[^\d]", "", m2.group(1)))
        return lt, None
    return None, None


def detect_type(title):
    """Normalize property type from title."""
    title_up = title.upper()
    if "GUDANG" in title_up:
        return "Gudang"
    if "RUKO" in title_up or ("RUMAH" in title_up and "TOKO" in title_up):
        return "Ruko"
    if "TANAH" in title_up:
        return "Tanah"
    if "APARTEMEN" in title_up:
        return "Apartemen"
    return "Rumah Tinggal"


def detect_region(title):
    """Extract region from title like 'RUMAH TINGGAL DI LOMBOK TIMUR'."""
    m = re.search(r"\bDI\s+(.+)$", title, re.IGNORECASE)
    if m:
        return m.group(1).strip().title()
    return "Lainnya"


WILAYAH_ALIAS = {
    "Mataram": "Kota Mataram",
    "Kota Mataram": "Kota Mataram",
}


def normalize_region(region):
    return WILAYAH_ALIAS.get(region, region)


def parse_pdf(pdf_path: str) -> pd.DataFrame:
    """
    Parse the booklet PDF and return a DataFrame with one row per listing.
    Skips cover/separator pages (no price found).
    """
    records = []
    path = Path(pdf_path)

    # Regex patterns
    RE_TITLE = re.compile(
        r"^(RUMAH TINGGAL|RUMAH DAN TOKO|GUDANG|TANAH|RUKO|APARTEMEN|TOKO).*DI\s+.+$",
        re.IGNORECASE,
    )
    RE_PRICE = re.compile(r"^Rp[\d\.,]+$")
    RE_LUAS = re.compile(r"Lt\s*/\s*Lb\s*:", re.IGNORECASE)
    RE_LUAS_T = re.compile(r"Lt\s*:\s*[\d]", re.IGNORECASE)
    RE_LELANG = re.compile(r"Lelang tanggal\s*:\s*(.+)", re.IGNORECASE)
    RE_JARAK = re.compile(r"(\d+)\s+Menit ke\s+(.+)", re.IGNORECASE)
    RE_FASILITAS_HEADER = re.compile(r"^FASILITAS$", re.IGNORECASE)
    RE_HUBUNGI_HEADER = re.compile(r"^HUBUNGI\s*:", re.IGNORECASE)

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            lines = [l.strip() for l in text.splitlines() if l.strip()]

            # Find title (first matching line)
            title_line = None
            for line in lines:
                if RE_TITLE.match(line):
                    title_line = line
                    break
            if not title_line:
                continue

            # Collect prices (Rp lines)
            prices = []
            for line in lines:
                if RE_PRICE.match(line):
                    prices.append(parse_price(line))

            if not prices:
                continue  # skip separator/cover pages

            harga_limit = prices[0] if len(prices) >= 1 else None
            harga_appraisal = prices[1] if len(prices) >= 2 else None

            # Luas
            luas_text = next((l for l in lines if RE_LUAS.search(l) or RE_LUAS_T.search(l)), "")
            lt, lb = parse_luas(luas_text)

            # Tanggal lelang
            tanggal = "On Process"
            for line in lines:
                m = RE_LELANG.search(line)
                if m:
                    val = m.group(1).strip()
                    if val and val.lower() != "on process":
                        tanggal = val
                    break

            # Address: line after luas or after price lines
            address_lines = []
            in_address = False
            for i, line in enumerate(lines):
                if RE_PRICE.match(line):
                    in_address = True
                    continue
                if in_address:
                    if RE_LUAS.search(line) or RE_LUAS_T.search(line):
                        break
                    if RE_FASILITAS_HEADER.match(line):
                        break
                    if "Google Maps" in line:
                        break
                    address_lines.append(line)

            address = " ".join(address_lines).strip()

            # Jarak ke landmark
            jarak = []
            for line in lines:
                m = RE_JARAK.search(line)
                if m:
                    jarak.append(f"{m.group(1)} menit ke {m.group(2).strip()}")

            # Fasilitas
            fasilitas = []
            in_fas = False
            for line in lines:
                if RE_FASILITAS_HEADER.match(line):
                    in_fas = True
                    continue
                if in_fas:
                    if RE_HUBUNGI_HEADER.search(line) or "Google Maps" in line:
                        break
                    fasilitas.append(line)

            prop_type = detect_type(title_line)
            region = normalize_region(detect_region(title_line))

            records.append(
                {
                    "page": page_num + 1,
                    "title": title_line.title(),
                    "type": prop_type,
                    "region": region,
                    "address": address,
                    "harga_limit": harga_limit,
                    "harga_appraisal": harga_appraisal,
                    "luas_tanah": lt,
                    "luas_bangunan": lb,
                    "tanggal_lelang": tanggal,
                    "jarak": " | ".join(jarak),
                    "fasilitas": ", ".join(fasilitas),
                }
            )

    df = pd.DataFrame(records)
    return df
