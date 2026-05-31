import io
import os
import pickle
from pathlib import Path
from PIL import Image

CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def _cache_path(pdf_path: str) -> Path:
    pdf_name = Path(pdf_path).stem
    return CACHE_DIR / f"{pdf_name}_images.pkl"


def render_pages(pdf_path: str, dpi: int = 72) -> dict[int, Image.Image]:
    """
    Render all PDF pages to PIL Images.
    Uses a pickle cache so repeated runs are instant.
    Returns dict: {page_number (1-based): PIL.Image}
    """
    cache_file = _cache_path(pdf_path)

    if cache_file.exists():
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    try:
        from pdf2image import convert_from_path
        images_list = convert_from_path(pdf_path, dpi=dpi)
        images = {i + 1: img for i, img in enumerate(images_list)}
    except Exception:
        images = {}

    with open(cache_file, "wb") as f:
        pickle.dump(images, f)

    return images


def image_to_bytes(img: Image.Image, format: str = "JPEG", quality: int = 75) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format=format, quality=quality)
    return buf.getvalue()
