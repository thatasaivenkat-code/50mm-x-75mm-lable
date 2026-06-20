import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, inch
from reportlab.graphics.barcode import code128 as reportlab_code128
from reportlab.lib.utils import simpleSplit
import barcode
from barcode.writer import ImageWriter
from datetime import datetime
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import pandas as pd
import pdfplumber
import re
import zipfile
import base64
import tempfile

# ===============================================
# PAGE CONFIG & SETUP
# ===============================================
st.set_page_config(page_title="🚀 వాయి వేగ Multi-Tool Pro Max", layout="wide", page_icon="🚛")

LOGO_FOLDER = "logos"
if not os.path.exists(LOGO_FOLDER):
    os.makedirs(LOGO_FOLDER)

NOW_TS = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

# ===============================================
# PREMIUM CSS
# ===============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="stApp"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #f8fafc !important;
}

[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}

.main-title {
    font-size: 3rem !important;
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    text-align: center;
    margin-bottom: 5px;
    letter-spacing: -0.5px;
}
.subtitle {
    font-size: 1.08rem !important;
    color: #475569;
    text-align: center;
    font-weight: 500;
    margin-bottom: 35px;
}
.tool-section {
    background: #ffffff;
    padding: 26px;
    border-radius: 16px;
    margin-bottom: 25px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    border: 1px solid #e2e8f0;
}
.section-title {
    font-size: 1.8rem !important;
    color: #0f172a;
    font-weight: 700;
    margin-bottom: 20px;
    border-left: 5px solid #3b82f6;
    padding-left: 12px;
}
.feature-card {
    background: #ffffff;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    transition: all 0.25s ease;
    display: flex;
    align-items: center;
    min-height: 110px;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    border-color: #3b82f6;
}
.feature-icon {
    font-size: 2.2rem;
    background: #eff6ff;
    padding: 12px;
    border-radius: 12px;
    margin-right: 18px;
}
.card-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 4px;
}
.card-desc {
    color: #64748b;
    font-size: 0.92rem;
    line-height: 1.4;
}
.metric-card {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    text-align: center;
    border-radius: 14px;
    padding: 1rem;
    box-shadow: 0 8px 18px rgba(37, 99, 235, .18);
}
.group-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    text-align: center;
    margin-bottom: 1rem;
}
.skip-box {
    background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
    color: white;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
}
.success-box {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
}
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.2s;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 14px rgba(37, 99, 235, 0.3) !important;
}
div[data-baseweb="select"] *, .stTextArea textarea, .stTextInput input {
    color: #0f172a !important;
    background-color: #f8fafc !important;
    border-radius: 8px !important;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600 !important;
    color: #475569 !important;
}
.stTabs [aria-selected="true"] {
    color: #2563eb !important;
    border-bottom-color: #2563eb !important;
}
.small-note {
    color: #64748b;
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

# ===============================================
# LABEL GENERATION FUNCTION
# ===============================================
def generate_vayu_vega_label(data, uploaded_logo_bytes, show_fixed_logo, selected_folder_logo_path, options, label_size_option, ctrl=None, canvas_obj=None):
    is_bulk = canvas_obj is not None

    if ctrl is None:
        ctrl = {
            "title_x": 0.0, "title_y": 0.0, "title_size": 9.0,
            "bc_x": 0.0, "bc_y": 0.0, "bc_width": 1.10, "bc_height": 0.45,
            "logo_x": 0.0, "logo_y": 0.0, "logo_w": 0.40, "logo_h": 0.42,
            "to_x": 0.0, "to_y": 0.0, "to_w": 1.82,
            "from_x": 0.0, "from_y": 0.0, "from_w": 1.50,
            "foot_x": 0.0, "foot_y": 0.0, "foot_size": 6.5
        }

    if label_size_option == "50mm x 75mm":
        width = (50 / 25.4) * inch
        height = (75 / 25.4) * inch
        is_small_size = True
    else:
        width, height = 4 * inch, 6 * inch
        is_small_size = False

    if not is_bulk:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))
    else:
        c = canvas_obj

    def draw_wrapped_text(canvas_obj, text, x, y, max_width, font_name, font_size, bold=False, align="left", line_spacing=1.2):
        f_name = f"{font_name}-Bold" if bold else font_name
        canvas_obj.setFont(f_name, font_size)
        lines = simpleSplit(str(text), f_name, font_size, max_width)
        for line in lines:
            if align == "right":
                canvas_obj.drawRightString(x + max_width, y, line)
            else:
                canvas_obj.drawString(x, y, line)
            y -= (font_size * line_spacing)
        return y

    c.setLineWidth(1.2)
    c.rect(0.04 * inch, 0.04 * inch, width - (0.08 * inch), height - (0.08 * inch))
    c.setLineWidth(1)

    if is_small_size:
        title_x_pos = (width / 2) + (ctrl["title_x"] * inch)
        title_y_pos = height - (0.22 * inch) + (ctrl["title_y"] * inch)
        c.setFont("Helvetica-Bold", ctrl["title_size"])
        c.drawCentredString(title_x_pos, title_y_pos, "VAYU VEGA EXPRESS")
        c.line(0.06 * inch, height - (0.28 * inch), width - (0.06 * inch), height - (0.28 * inch))

        awb = str(data.get('awb', 'N/A'))
        bc_x_pos = 0.12 * inch + (ctrl["bc_x"] * inch)
        bc_y_pos = height - (0.78 * inch) + (ctrl["bc_y"] * inch)

        try:
            awb_barcode = reportlab_code128.Code128(awb, barHeight=ctrl["bc_height"] * inch, barWidth=ctrl["bc_width"])
            awb_barcode.quiet = 0
            awb_barcode.drawOn(c, bc_x_pos, bc_y_pos)
        except:
            pass

        final_right_logo_bytes = uploaded_logo_bytes
        final_right_logo_path = selected_folder_logo_path if not uploaded_logo_bytes else None

        if final_right_logo_bytes or final_right_logo_path:
            try:
                img = Image.open(io.BytesIO(final_right_logo_bytes)) if final_right_logo_bytes else Image.open(final_right_logo_path)
                img_w, img_h = img.size
                max_w = ctrl["logo_w"] * inch
                max_h = ctrl["logo_h"] * inch
                aspect = img_w / img_h
                final_w, final_h = (max_w, max_w/aspect) if aspect > (max_w/max_h) else (max_h*aspect, max_h)
                logo_x_pos = width - (0.06 * inch) - final_w + (ctrl["logo_x"] * inch)
                logo_y_pos = height - (1.8 * inch) + (ctrl["logo_y"] * inch)

                if final_right_logo_bytes:
                    c.drawInlineImage(img, logo_x_pos, logo_y_pos, width=final_w, height=final_h)
                else:
                    c.drawImage(final_right_logo_path, logo_x_pos, logo_y_pos, width=final_w, height=final_h, mask='auto', preserveAspectRatio=True)
            except:
                pass

        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(width / 2, height - (0.92 * inch), f"AWB: {awb}")
        c.line(0.06 * inch, height - (0.98 * inch), width - (0.06 * inch), height - (0.98 * inch))

        ship_y = height - (1.10 * inch) + (ctrl["to_y"] * inch)
        ship_x = 0.08 * inch + (ctrl["to_x"] * inch)
        ship_w = (ctrl["to_w"] * inch)

        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(ship_x, ship_y, "SHIP TO:")

        ref = str(data.get('ref', 'REF'))
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(width - (0.08 * inch), ship_y, f"REF: {ref}")

        ship_y = draw_wrapped_text(c, f"NAME: {data.get('to_name','')}".upper(), ship_x, ship_y - 11, ship_w, "Helvetica", 9, bold=True)
        to_phone = data.get('to_phone','') if options['show_mobile'] else "0000000000"
        ship_y = draw_wrapped_text(c, f"PH: {to_phone}", ship_x, ship_y, ship_w, "Helvetica", 9, bold=True)

        raw_address = str(data.get('to_address',''))
        addr_len = len(raw_address)
        if addr_len > 120:
            to_addr_font_size = 5.5
            addr_spacing = 1.05
        elif addr_len > 75:
            to_addr_font_size = 6.5
            addr_spacing = 1.1
        else:
            to_addr_font_size = 8
            addr_spacing = 1.25

        ship_y = draw_wrapped_text(c, raw_address, ship_x, ship_y - 2, ship_w, "Helvetica", to_addr_font_size, bold=False, line_spacing=addr_spacing)

        bottom_area_y = 1.05 * inch
        if options['show_from']:
            from_x = width - (1.6 * inch) + (ctrl["from_x"] * inch)
            from_w = ctrl["from_w"] * inch
            from_y = (bottom_area_y - 45) + (ctrl["from_y"] * inch)
            from_phone = data.get('from_phone','') if options['show_mobile'] else "0000000000"

            from_y = draw_wrapped_text(c, f"FROM: {data.get('from_name','')}".upper(), from_x, from_y, from_w, "Helvetica", 6.5, bold=True, align="right")
            from_y = draw_wrapped_text(c, f"PH: {from_phone}", from_x, from_y, from_w, "Helvetica", 6, bold=True, align="right")
            draw_wrapped_text(c, data.get('from_address',''), from_x, from_y, from_w, "Helvetica", 5, bold=False, line_spacing=1.1, align="right")

        foot_y_pos = 0.10 * inch + (ctrl["foot_y"] * inch)
        foot_x_pos = 0.08 * inch + (ctrl["foot_x"] * inch)
        c.setFont("Helvetica-Bold", ctrl["foot_size"])
        c.drawString(foot_x_pos, foot_y_pos, "THANK YOU - VAYU VEGA")
        c.drawRightString(width - (0.08 * inch) + (ctrl["foot_x"] * inch), foot_y_pos, f"DT: {data.get('label_date','')}")

    else:
        line_y = height - (0.85 * inch)
        if show_fixed_logo:
            fixed_path = "logo.png"
            if os.path.exists(fixed_path):
                c.drawImage(fixed_path, -0.5 * inch, height - (1 * inch), width=1.7 * inch, height=1 * inch, mask='auto', preserveAspectRatio=True)

        final_right_logo_bytes = uploaded_logo_bytes
        final_right_logo_path = selected_folder_logo_path if not uploaded_logo_bytes else None

        if final_right_logo_bytes or final_right_logo_path:
            try:
                img = Image.open(io.BytesIO(final_right_logo_bytes)) if final_right_logo_bytes else Image.open(final_right_logo_path)
                img_w, img_h = img.size
                max_w, max_h = 1.3 * inch, 0.6 * inch
                aspect = img_w / img_h
                final_w, final_h = (max_w, max_w/aspect) if aspect > (max_w/max_h) else (max_h*aspect, max_h)
                if final_right_logo_bytes:
                    c.drawInlineImage(img, width - (0.15 * inch) - final_w, height - (0.78 * inch), width=final_w, height=final_h)
                else:
                    c.drawImage(final_right_logo_path, width - (0.15 * inch) - final_w, height - (0.78 * inch), width=final_w, height=final_h, mask='auto', preserveAspectRatio=True)
            except:
                pass

        c.line(0.12 * inch, line_y, width - (0.12 * inch), line_y)

        awb = str(data.get('awb', 'N/A'))
        awb_barcode = reportlab_code128.Code128(awb, barHeight=0.6 * inch, barWidth=1.8)
        awb_barcode.drawOn(c, 0.4 * inch, 4.4 * inch)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width/2, 4.25 * inch, f"AWB: {awb}")

        ship_x = 0.15 * inch
        max_ship_w = 1.9 * inch
        ship_y = 3.9 * inch
        to_phone = data.get('to_phone','') if options['show_mobile'] else "0000000000"

        ship_y = draw_wrapped_text(c, "SHIP TO:", ship_x, ship_y, max_ship_w, "Helvetica", 9, bold=True)
        ship_y = draw_wrapped_text(c, f"NAME: {data.get('to_name','')}", ship_x + 0.05 * inch, ship_y, max_ship_w, "Helvetica", 8, bold=True)
        ship_y = draw_wrapped_text(c, f"PH: {to_phone}", ship_x + 0.05 * inch, ship_y, max_ship_w, "Helvetica", 8, bold=True)
        draw_wrapped_text(c, data.get('to_address',''), ship_x + 0.05 * inch, ship_y, max_ship_w, "Helvetica", 6)

        pincode_x = 2.7 * inch
        c.setFont("Helvetica-Bold", 11)
        c.drawString(pincode_x + 0.10 * inch, 2.68 * inch, f"PIN: {data.get('to_pincode','')}")
        c.rect(pincode_x, 2.60 * inch, 1.1 * inch, 0.25 * inch)

        from_x_start = 2.2 * inch
        max_from_w = width - from_x_start - (0.15 * inch)
        curr_y_from = 3.9 * inch

        if options['show_from']:
            from_phone = data.get('from_phone','') if options['show_mobile'] else "0000000000"
            curr_y_from = draw_wrapped_text(c, "FROM:", from_x_start, curr_y_from, max_from_w, "Helvetica", 9, bold=True, align="right")
            curr_y_from = draw_wrapped_text(c, f"NAME: {data.get('from_name','')}", from_x_start, curr_y_from, max_from_w, "Helvetica", 8, bold=True, align="right")
            curr_y_from = draw_wrapped_text(c, f"PH: {from_phone}", from_x_start, curr_y_from, max_from_w, "Helvetica", 8, bold=True, align="right")
            draw_wrapped_text(c, data.get('from_address',''), from_x_start, curr_y_from, max_from_w, "Helvetica", 6, align="right")

        c.line(0.15 * inch, 2.5 * inch, 3.85 * inch, 2.5 * inch)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, 2.35 * inch, f"PRODUCT: {data.get('product_name','')}")
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width/2, 2.1 * inch, f"VALUE: {data.get('product_value','')}")
        c.line(0.15 * inch, 2.0 * inch, 3.85 * inch, 2.0 * inch)

        c.rect(0.2 * inch, 1.4 * inch, 3.6 * inch, 0.4 * inch)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0.3 * inch, 1.55 * inch, f"WT: {data.get('weight','')} KG")
        if options['show_amount']:
            c.drawRightString(3.7 * inch, 1.55 * inch, f"TOTAL: Rs.{data.get('total_amount','')}")

        ref = str(data.get('ref', 'REF'))
        ref_bar = reportlab_code128.Code128(ref, barHeight=0.4 * inch, barWidth=1.0)
        ref_bar.drawOn(c, -0.1 * inch, 0.75 * inch)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(0.2 * inch, 0.62 * inch, f"{ref}")

        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(3.8 * inch, 1.1 * inch, f"MODE: {data.get('mode', 'Surface').upper()}")
        c.drawRightString(3.8 * inch, 0.9 * inch, f"RISK: {data.get('risk', 'Carrier').upper()}")

        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(3.8 * inch, 0.4 * inch, f"DATE: {data.get('label_date','')}")
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, 0.15 * inch, "THANK YOU FOR CHOOSING VAYU VEGA")

    if not is_bulk:
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
    else:
        c.showPage()

# ===============================================
# HELPERS
# ===============================================
def show_pdf_preview(pdf_buffer, height=520):
    base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0&scrollbar=0" width="100%" height="{height}px" style="border: 1px solid #cbd5e1; border-radius: 12px;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def extract_full_ref(text):
    patterns = [
        r'\bRef\.?\s*No[:\s-]*([A-Z]?\d+\+\d+)\b',
        r'\b([A-Z]\d+\+\d+)\b',
        r'\b(\d+\+\d+)\b',
        r'\b(19-\d{10})\b',
        r'\b(\d{2}-\d+)\b',
        r'\b([A-Z]\d{8,13})\b',
        r'\b(\d{12,14})\b',
        r'\bNo\s*[:\-]?\s*(\d+)\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, text or "", re.IGNORECASE)
        if match:
            return match.group(1) if match.lastindex else match.group(0)
    return None

def normalize_ref(ref_text):
    if not ref_text:
        return None
    return re.sub(r'[\s\.\-:]+', '', str(ref_text)).lower().strip()

def is_awb_only(ref_text):
    if not ref_text:
        return False
    return bool(re.fullmatch(r'[A-Z]\d{8,13}', str(ref_text).strip(), re.IGNORECASE))

def get_group_id(ref_text):
    if not ref_text:
        return None
    ref_text = str(ref_text).strip()
    match = re.search(r'[A-Z]?(\d+)\+\d+', ref_text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'(\d{2})-\d+', ref_text)
    if match:
        return match.group(1)
    return None

def validate_ref(ref_text):
    if not ref_text:
        return False
    valid_patterns = [
        r'^[A-Z]?\d+\+\d+$',
        r'^\d{2}-\d+$',
        r'^\d+$'
    ]
    return any(re.match(p, str(ref_text).strip(), re.IGNORECASE) for p in valid_patterns)

def build_pdf_from_pages(pages):
    writer = PdfWriter()
    for page in pages:
        writer.add_page(page)
    bio = io.BytesIO()
    writer.write(bio)
    bio.seek(0)
    return bio.getvalue()

def sort_group_key(item):
    gid = item[0]
    return int(gid) if str(gid).isdigit() else str(gid)

def process_pdf_reference_files(uploaded_files, skip_awb_only=True):
    grouped_pages = {}
    no_ref_pages = []
    skipped_pages = []
    extracted_log = []

    global_seen_refs = set()
    total_pages_processed = 0

    for file in uploaded_files:
        file_bytes = file.read()
        reader_stream = io.BytesIO(file_bytes)
        text_stream = io.BytesIO(file_bytes)

        reader = PdfReader(reader_stream)
        file_seen_refs = set()

        with pdfplumber.open(text_stream) as pdf:
            for page_index, page in enumerate(pdf.pages):
                total_pages_processed += 1
                page_label = f"{file.name} (Page {page_index + 1})"
                text = page.extract_text() or ""
                ref = extract_full_ref(text)

                if ref:
                    if skip_awb_only and is_awb_only(ref):
                        skipped_pages.append(f"{page_label} -> {ref} [AWB ONLY SKIPPED]")
                        extracted_log.append(f"{page_label} -> AWB ONLY SKIPPED: {ref}")
                        continue

                    norm_ref = normalize_ref(ref)

                    if norm_ref in file_seen_refs:
                        skipped_pages.append(f"{page_label} -> {ref} [PDF DUPLICATE]")
                        extracted_log.append(f"{page_label} -> SKIPPED PDF DUPLICATE: {ref}")
                        continue

                    if norm_ref in global_seen_refs:
                        skipped_pages.append(f"{page_label} -> {ref} [GLOBAL DUPLICATE]")
                        extracted_log.append(f"{page_label} -> SKIPPED GLOBAL DUPLICATE: {ref}")
                        continue

                    file_seen_refs.add(norm_ref)
                    global_seen_refs.add(norm_ref)

                    gid = get_group_id(ref)
                    if gid and validate_ref(ref):
                        grouped_pages.setdefault(gid, []).append(reader.pages[page_index])
                        extracted_log.append(f"{page_label} -> REF: {ref} -> GROUP: {gid}")
                    else:
                        no_ref_pages.append(reader.pages[page_index])
                        extracted_log.append(f"{page_label} -> INVALID REF FORMAT: {ref}")
                else:
                    no_ref_pages.append(reader.pages[page_index])
                    extracted_log.append(f"{page_label} -> NO REF FOUND")

    return {
        "grouped_pages": grouped_pages,
        "no_ref_pages": no_ref_pages,
        "skipped_pages": skipped_pages,
        "extracted_log": extracted_log,
        "total_pages_processed": total_pages_processed,
        "total_files": len(uploaded_files)
    }

def build_zip_of_groups(grouped_pages):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for gid, pages in sorted(grouped_pages.items(), key=sort_group_key):
            pdf_bytes = build_pdf_from_pages(pages)
            zipf.writestr(f"Group_{gid}.pdf", pdf_bytes)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# ===============================================
# SIDEBAR NAVIGATION
# ===============================================
with st.sidebar:
    st.markdown('<div style="text-align:center; padding:10px 0 20px 0;"><h2 style="color:#3b82f6; font-weight:800; margin:0; font-size:1.6rem;">⚡ VAYU VEGA</h2><p style="color:#94a3b8; font-size:0.8rem; margin:0;">Enterprise Hub v4.0</p></div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-size:0.75rem; font-weight:700; text-transform:uppercase; margin-bottom:8px; padding-left:5px;">Main Modules</p>', unsafe_allow_html=True)

    choice = st.radio(
        "Navigation Options",
        ["🏠 Dashboard", "🕹️ Advanced Controls", "📦 Barcode Pro", "📊 PDF→Excel", "📂 PDF Ref Extractor"],
        index=0,
        label_visibility="collapsed"
    )

# ===============================================
# DASHBOARD
# ===============================================
if choice == "🏠 Dashboard":
    st.markdown('<h1 class="main-title">వాయి వేగ Multi-Tool Pro Max</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Unified Logistics, Labeling, Barcode, PDF Parsing & Reference Extraction Automation Hub</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🕹️</span>
            <div>
                <div class="card-title">Advanced Label Controls</div>
                <div class="card-desc">Dynamic joystick tuning with single and bulk PDF label generation for 50x75 and 4x6 formats.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📦</span>
            <div>
                <div class="card-title">Barcode Generator Pro</div>
                <div class="card-desc">A4 barcode sheet generation using Code128 layout with brand title header support.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div>
                <div class="card-title">PDF to Excel Converter</div>
                <div class="card-desc">Delhivery and DTDC waybill parsing with normalized Excel export pipeline.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📂</span>
            <div>
                <div class="card-title">PDF Reference Extractor</div>
                <div class="card-desc">Group pages using refs like E25+1 or D19+1, skip duplicates, and export grouped PDFs.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #eff6ff; padding: 20px; border-radius: 12px; border: 1px solid #bfdbfe; text-align: center; max-width: 800px; margin: 40px auto 0 auto;">
        <h4 style="color:#1e40af; margin-top:0; font-weight:700;">System Ready</h4>
        <p style="color:#1e3a8a; margin-bottom:0; font-size:0.95rem;">బ్రో, project-1 modules + PDF ref extractor anni kalipi full enterprise version ready అయింది. Sidebar nundi module select chesi direct use cheyyachu.</p>
    </div>
    """, unsafe_allow_html=True)

# ===============================================
# ADVANCED CONTROLS
# ===============================================
elif choice == "🕹️ Advanced Controls":
    st.markdown('<h2 class="section-title">🕹️ Advanced Label Controls & Layout Tuning</h2>', unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.header("📐 Layout Configuration")
    label_size = st.sidebar.selectbox("📐 Label Sheet Dimensions", ["50mm x 75mm", "4x6 Inch"])
    show_logo = st.sidebar.checkbox("Show Branding Logo (logo.png)", value=True)
    uploaded_logo = st.sidebar.file_uploader("Upload External Logo", type=['png', 'jpg', 'jpeg'], key="logo_uploader")

    st.sidebar.markdown("---")
    st.sidebar.header("👁️ Visibility Controls")
    opt_amount = st.sidebar.toggle("Show Total Value/Amount", value=True)
    opt_mobile = st.sidebar.toggle("Show Client Contact Numbers", value=True)
    opt_from = st.sidebar.toggle("Show Sender Info (FROM)", value=True)

    display_options = {
        'show_amount': opt_amount,
        'show_mobile': opt_mobile,
        'show_from': opt_from
    }

    logo_files = [f for f in os.listdir(LOGO_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))] if os.path.exists(LOGO_FOLDER) else []
    selected_logo_name = st.sidebar.selectbox("Select Regional Hub Logo", ["None"] + logo_files)
    folder_logo_path = os.path.join(LOGO_FOLDER, selected_logo_name) if selected_logo_name != "None" else None

    ctrl = {
        "title_x": 0.0, "title_y": 0.0, "title_size": 9.0,
        "bc_x": 0.0, "bc_y": 0.0, "bc_width": 1.10, "bc_height": 0.45,
        "logo_x": 0.0, "logo_y": 0.0, "logo_w": 0.40, "logo_h": 0.42,
        "to_x": 0.0, "to_y": 0.0, "to_w": 1.82,
        "from_x": 0.0, "from_y": 0.0, "from_w": 1.50,
        "foot_x": 0.0, "foot_y": 0.0, "foot_size": 6.5
    }

    if label_size == "50mm x 75mm":
        st.sidebar.markdown("---")
        st.sidebar.header("🕹️ Super Joysticks Calibration")
        lock_dashboard = st.sidebar.toggle("🔒 Freeze Configuration", value=False)

        if not lock_dashboard:
            with st.sidebar.expander("📝 1. Header Coordinates"):
                ctrl["title_x"] = st.slider("Title Offset X", -0.5, 0.5, 0.0, step=0.01)
                ctrl["title_y"] = st.slider("Title Offset Y", -0.3, 0.3, 0.0, step=0.01)
                ctrl["title_size"] = st.slider("Title Typography Size", 6.0, 14.0, 9.0, step=0.5)
            with st.sidebar.expander("📊 2. Barcode Dimensions"):
                ctrl["bc_x"] = st.slider("Barcode Position X", -0.5, 0.5, 0.0, step=0.01)
                ctrl["bc_y"] = st.slider("Barcode Position Y", -0.5, 0.5, 0.0, step=0.01)
                ctrl["bc_width"] = st.slider("Module Line Width", 0.7, 1.8, 1.10, step=0.05)
                ctrl["bc_height"] = st.slider("Barcode Stripe Height", 0.2, 0.8, 0.45, step=0.05)
            with st.sidebar.expander("🖼️ 3. Logo Scaling Matrix"):
                ctrl["logo_x"] = st.slider("Logo Position X", -0.5, 0.5, 0.0, step=0.01)
                ctrl["logo_y"] = st.slider("Logo Position Y", -0.5, 0.5, 0.0, step=0.01)
                ctrl["logo_w"] = st.slider("Max Scale Width", 0.2, 1.0, 0.40, step=0.02)
                ctrl["logo_h"] = st.slider("Max Scale Height", 0.2, 1.0, 0.42, step=0.02)
            with st.sidebar.expander("📍 4. Consignee Text Envelope"):
                ctrl["to_x"] = st.slider("To Zone X", -0.4, 0.4, 0.0, step=0.01)
                ctrl["to_y"] = st.slider("To Zone Y", -0.5, 0.5, 0.0, step=0.01)
                ctrl["to_w"] = st.slider("Text Wrap Boundary Width", 1.0, 2.5, 1.82, step=0.02)
            if opt_from:
                with st.sidebar.expander("🏢 5. Sender Text Envelope"):
                    ctrl["from_x"] = st.slider("From Zone X", -0.5, 0.5, 0.0, step=0.01)
                    ctrl["from_y"] = st.slider("From Zone Y", -0.5, 0.5, 0.0, step=0.01)
                    ctrl["from_w"] = st.slider("Sender Box Limit Width", 0.8, 2.2, 1.50, step=0.02)
            with st.sidebar.expander("🎉 6. Footer Layout"):
                ctrl["foot_x"] = st.slider("Footer Alignment X", -0.3, 0.3, 0.0, step=0.01)
                ctrl["foot_y"] = st.slider("Footer Alignment Y", -0.2, 0.4, 0.0, step=0.01)
                ctrl["foot_size"] = st.slider("Footer Font Weight Size", 4.0, 10.0, 6.5, step=0.5)
        else:
            st.sidebar.success("🔒 Calibration Matrix Locked.")

    tab1, tab2 = st.tabs(["📄 Single Manual Dispatch", "📂 Bulk Batch Manifest"])

    with tab1:
        st.markdown('<div class="tool-section">', unsafe_allow_html=True)
        c_form, c_view = st.columns([3, 2])

        with c_form:
            with st.form("single_form"):
                c1, c2 = st.columns(2)
                with c1:
                    awb_no = st.text_input("Waybill Tracking ID (AWB)", "VV-100200")
                    p_name = st.text_input("Declared Product Type", "General")
                    p_val = st.text_input("Assigned Commercial Value", "1000")
                    l_date = st.text_input("Label Date Stamp", datetime.now().strftime("%d-%m-%Y"))
                    wt = st.text_input("Physical Weight (KG)", "0.5")
                    t_amt = st.text_input("Invoice Total Amount", "1100")
                    ref_no = st.text_input("Customer Ref Number", "REF-01")
                    mode_opt = st.selectbox("Logistics Channel Mode", ["Surface", "Express"])
                    risk_opt = st.selectbox("Consignment Risk Cover", ["Carrier", "No Risk"])
                with c2:
                    t_name = st.text_input("Consignee (To Name)", "CHINNA RAO")
                    t_phone = st.text_input("Consignee Contact Mobile", "9876543210")
                    t_pin = st.text_input("Destination Pincode", "500001")
                    t_addr = st.text_area("Full Complete Destination Address", "D.No: 4-56/A, Main Road, Near Ramalayam Temple, Gudivada, Andhra Pradesh")
                    f_name = st.text_input("Shipper (From Name)", "Vayu Vega Hub")
                    f_phone = st.text_input("Shipper Contact Mobile", "8888888888")
                    f_addr = st.text_area("Full Origin Address Coordinates", "Hub Main Center, Vijayawada")
                st.form_submit_button("🔥 Refresh Design Grid View")

        l_data = {
            'awb': awb_no, 'product_name': p_name, 'product_value': p_val, 'label_date': l_date,
            'ref': ref_no, 'weight': wt, 'total_amount': t_amt, 'to_name': t_name,
            'to_phone': t_phone, 'to_pincode': t_pin, 'to_address': t_addr,
            'from_name': f_name, 'from_phone': f_phone, 'from_address': f_addr,
            'mode': mode_opt, 'risk': risk_opt
        }

        current_pdf = generate_vayu_vega_label(
            l_data,
            uploaded_logo.getvalue() if uploaded_logo else None,
            show_logo,
            folder_logo_path,
            display_options,
            label_size,
            ctrl=ctrl
        )

        with c_view:
            st.markdown("<h4 style='color:#0f172a; font-weight:700; margin-top:0;'>🖥️ Blueprint Rendering</h4>", unsafe_allow_html=True)
            show_pdf_preview(current_pdf, height=500)
            st.download_button("📥 Export Current PDF File", current_pdf, f"{awb_no}_{ref_no}.pdf", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="tool-section">', unsafe_allow_html=True)
        st.info("💡 CSV లేదా Excel ఫైల్‌ను అప్‌లోడ్ చేయండి. పైన సెట్ చేసిన జాయ్‌స్టిక్ సెట్టింగ్స్ అన్ని లేబుల్స్‌కి అప్లై అవుతాయి.")

        sample_data = {
            'Consignment (CN) No.': ['VV1001', 'VV1002'],
            'Customer Reference Number': ['REF01', 'REF02'],
            "Receiver's Name": ['Rahul Kumar', 'Suresh Kumar'],
            "Receiver's Address Line 1": ['H.No 1-2, Ameerpet', 'Plot 45, Benz Circle'],
            "Receiver's Address Line 2": ['Hyderabad, Telangana', 'Vijayawada, AP'],
            "Receiver's Pincode": ['500001', '520001'],
            "Receiver's Phone Number": ['9876543210', '9999999999'],
            'weight (kg)': ['0.5', '1.2'],
            'Description': ['General Items', 'Electronics'],
            'Declared Value': ['1000', '5000'],
            'VAS Amount': ['1100', '5200'],
            "Sender's Name": ['Vayu Vega Hub', 'Vayu Vega Hub'],
            "Sender's Address Line 1": ['Hub Main Road', 'Hub Main Road'],
            "Sender's Phone number": ['8888888888', '8888888888'],
            'Service Type': ['Surface', 'Express']
        }
        sample_df = pd.DataFrame(sample_data)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            csv_data = sample_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Master Template CSV", data=csv_data, file_name="vayu_vega_master_sample.csv", mime="text/csv", use_container_width=True)
        with col_s2:
            output_xlsx = io.BytesIO()
            with pd.ExcelWriter(output_xlsx, engine='openpyxl') as writer:
                sample_df.to_excel(writer, index=False)
            st.download_button("📥 Download Master Template Excel", data=output_xlsx.getvalue(), file_name="vayu_vega_master_sample.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        st.markdown("---")
        uploaded_file = st.file_uploader("Upload Batch Operations Matrix File", type=['csv', 'xlsx'], key="bulk_upload")

        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.write("### Target Mapping Rows Data Validation Grid")
            if "Select" not in df.columns:
                df.insert(0, "Select", True)

            edited_df = st.data_editor(df, hide_index=True, use_container_width=True)
            selected_rows = edited_df[edited_df["Select"] == True]

            if st.button(f"🚀 Compile System Engine for {len(selected_rows)} Manifest Items", use_container_width=True):
                if len(selected_rows) == 0:
                    st.error("Please ensure you mark rows checked inside the system layout grid!")
                else:
                    logo_bytes = uploaded_logo.getvalue() if uploaded_logo else None
                    zip_buffer = io.BytesIO()
                    bulk_pdf_buffer = io.BytesIO()

                    b_width, b_height = ((50 / 25.4) * inch, (75 / 25.4) * inch) if label_size == "50mm x 75mm" else (4 * inch, 6 * inch)
                    bulk_c = canvas.Canvas(bulk_pdf_buffer, pagesize=(b_width, b_height))

                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for idx, row in selected_rows.iterrows():
                            raw_dict = row.to_dict()

                            to_addr_1 = str(raw_dict.get("Receiver's Address Line 1", '')).strip()
                            to_addr_2 = str(raw_dict.get("Receiver's Address Line 2", '')).strip()
                            to_city = str(raw_dict.get("Receiver's City", '')).strip()
                            to_state = str(raw_dict.get("Receiver's State", '')).strip()
                            assembled_to_addr = ", ".join([p for p in [to_addr_1, to_addr_2, to_city, to_state] if p and p.lower() != 'nan'])

                            from_addr_1 = str(raw_dict.get("Sender's Address Line 1", '')).strip()
                            from_addr_2 = str(raw_dict.get("Sender's Address Line 2", '')).strip()
                            from_city = str(raw_dict.get("Sender's City", '')).strip()
                            from_state = str(raw_dict.get("Sender's State", '')).strip()
                            assembled_from_addr = ", ".join([p for p in [from_addr_1, from_addr_2, from_city, from_state] if p and p.lower() != 'nan'])

                            l_dict = {
                                'awb': raw_dict.get('Consignment (CN) No.', raw_dict.get('Waybill', raw_dict.get('awb', f'VV-BULK-{idx}'))),
                                'ref': raw_dict.get('Customer Reference Number', raw_dict.get('Reference No', raw_dict.get('ref', 'REF'))),
                                'to_name': raw_dict.get("Receiver's Name", raw_dict.get('Consignee Name', raw_dict.get('to_name', ''))),
                                'to_address': assembled_to_addr if assembled_to_addr else raw_dict.get('Address', raw_dict.get('to_address', '')),
                                'to_pincode': raw_dict.get("Receiver's Pincode", raw_dict.get('Pincode', raw_dict.get('to_pincode', ''))),
                                'to_phone': raw_dict.get("Receiver's Phone Number", raw_dict.get('Mobile', raw_dict.get('Phone', raw_dict.get('to_phone', '')))),
                                'weight': raw_dict.get('weight (kg)', raw_dict.get('Weight', raw_dict.get('weight', '0.0'))),
                                'product_name': raw_dict.get('Description', raw_dict.get('Product to be Shipped', raw_dict.get('product_name', 'General'))),
                                'product_value': raw_dict.get('Declared Value', raw_dict.get('Package Amount', raw_dict.get('product_value', '0'))),
                                'total_amount': raw_dict.get('VAS Amount', raw_dict.get('Cod Amount', raw_dict.get('Package Amount', raw_dict.get('total_amount', '0')))),
                                'from_name': raw_dict.get("Sender's Name", raw_dict.get('Seller Name', raw_dict.get('from_name', 'Vayu Vega Hub'))),
                                'from_address': assembled_from_addr if assembled_from_addr else raw_dict.get('Seller Address', raw_dict.get('from_address', '')),
                                'from_phone': raw_dict.get("Sender's Phone number", raw_dict.get('from_phone', '8888888888')),
                                'mode': raw_dict.get('Service Type', raw_dict.get('Shipping Mode', raw_dict.get('mode', 'Surface'))),
                                'risk': raw_dict.get('risk', 'Carrier'),
                                'label_date': raw_dict.get('label_date', datetime.now().strftime("%d-%m-%Y"))
                            }

                            single_pdf = generate_vayu_vega_label(l_dict, logo_bytes, show_logo, folder_logo_path, display_options, label_size, ctrl=ctrl)
                            f_name = f"{l_dict.get('awb')}_{l_dict.get('ref')}.pdf"
                            zip_file.writestr(f_name, single_pdf.getvalue())

                            generate_vayu_vega_label(l_dict, logo_bytes, show_logo, folder_logo_path, display_options, label_size, ctrl=ctrl, canvas_obj=bulk_c)

                    bulk_c.save()
                    bulk_pdf_buffer.seek(0)

                    st.success(f"🎯 Packed {len(selected_rows)} Sequential Digital Labels Securely!")
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.download_button("📥 Download Independent Files (ZIP)", zip_buffer.getvalue(), "Selected_Labels.zip", use_container_width=True)
                    with col_d2:
                        st.download_button("📥 Download Combined Continuous Grid (PDF)", bulk_pdf_buffer.getvalue(), "Selected_Labels_Combined.pdf", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# BARCODE PRO
# ===============================================
elif choice == "📦 Barcode Pro":
    st.markdown('<h2 class="section-title">📦 Barcode Pro Layout Engine</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)

    colb1, colb2 = st.columns([2, 1])
    with colb1:
        numbers_input = st.text_area("📝 Input Barcode Sequential IDs (Line Separated):", height=200, placeholder="PA1234567890\nPA1234567891")
    with colb2:
        company_name = st.text_input("🏢 Brand Header Top Text Label:", value="VAYU VEGA LOGISTICS")

    if st.button("🖨️ Compile A4 Standard Print Grid Sheet", use_container_width=True):
        if numbers_input.strip() and company_name.strip():
            tracking_list = [n.strip() for n in numbers_input.split('\n') if n.strip()]
            try:
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=A4)
                width, height = A4
                label_width, label_height = 3 * inch, 1.5 * inch
                margin_x, margin_y = 0.5 * inch, 0.5 * inch
                curr_x, curr_y = margin_x, height - margin_y - label_height

                for num in tracking_list:
                    code_class = barcode.get_barcode_class('code128')
                    my_barcode = code_class(num, writer=ImageWriter())
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        img_path = my_barcode.save(tmp.name.replace(".png", ""), options={"write_text": True, "font_size": 8, "text_distance": 3})

                    c.setFont("Helvetica-Bold", 10)
                    c.drawCentredString(curr_x + (label_width/2), curr_y + label_height - 15, company_name.upper())
                    c.drawImage(img_path, curr_x + 10, curr_y + 10, width=label_width-20, height=label_height-40)

                    curr_x += label_width + 0.2 * inch
                    if curr_x + label_width > width:
                        curr_x = margin_x
                        curr_y -= label_height + 0.3 * inch
                    if curr_y < margin_y:
                        c.showPage()
                        curr_y = height - margin_y - label_height
                        curr_x = margin_x

                    if os.path.exists(img_path):
                        os.remove(img_path)

                c.save()
                st.success(f"✅ Generated {len(tracking_list)} sequential barcodes successfully!")
                st.download_button("📥 Save A4 Composite Print Sheet PDF", pdf_buffer.getvalue(), f"{company_name.replace(' ', '_')}_A4_Labels.pdf", use_container_width=True)
            except Exception as e:
                st.error(f"❌ Core Exception Failure: {str(e)}")
        else:
            st.warning("⚠️ High alert fields data cannot be null!")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# PDF TO EXCEL
# ===============================================
elif choice == "📊 PDF→Excel":
    st.markdown('<h2 class="section-title">📊 Waybill Carrier Extraction Database Engine</h2>', unsafe_allow_html=True)
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)

    st.subheader("1️⃣ Deep Extraction Parsing Filter Matrix")
    col_del, col_dtdc = st.columns(2)

    with col_del:
        use_delhivery = st.checkbox("🚚 Enable Delhivery System Layout Recognition", value=True)
        del_client = st.text_input("Delhivery Assigned Client/Account Key ID:", key="del_c", placeholder="e.g., 1234")
        del_weight = st.text_input("Fallback Unit Weight Configuration (Delhivery):", key="del_w", placeholder="e.g., 0.5")

    with col_dtdc:
        use_dtdc = st.checkbox("📦 Enable DTDC System Layout Recognition", value=True)
        dtdc_client = st.text_input("DTDC Assigned Client/Account Key ID:", key="dtdc_c", placeholder="e.g., 5678")
        dtdc_weight = st.text_input("Fallback Unit Weight Configuration (DTDC):", key="dtdc_w", placeholder="e.g., 1.0")

    st.divider()
    st.subheader("2️⃣ Ingestion System Manifest PDF Binary Pool")
    pdf_files = st.file_uploader("📄 Drop Digital PDF Files Directly", type=['pdf'], accept_multiple_files=True, key="pdf_excel_uploader")

    if pdf_files and st.button("🔄 Execute Extraction Pipeline Matrix", use_container_width=True):
        all_extracted_data = []

        with st.spinner("Parsing target binary stream channels..."):
            for pdf_file in pdf_files:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if not text:
                            continue

                        final_date, awb, dest_name, dest_pin = "", "", "", ""
                        row_client, row_weight = "", ""

                        if use_delhivery and ("AWB#" in text or "Delhivery" in text):
                            row_client = del_client
                            row_weight = del_weight
                            d_match = re.search(r"(\d{2}-[a-zA-Z]{3}-\d{4})", text)
                            if d_match:
                                try:
                                    d_obj = datetime.strptime(d_match.group(1), '%d-%b-%Y')
                                    final_date = d_obj.strftime('%d-%m-%Y')
                                except:
                                    pass
                            awb_m = re.search(r"AWB#\s*(\d+)", text)
                            awb = awb_m.group(1) if awb_m else ""
                            n_match = re.search(r"Ship to\s*-\s*([^\n]+)", text)
                            dest_name = n_match.group(1).strip() if n_match else ""
                            p_match = re.search(r"PIN\s*[:\-\s]*(\d{6})", text)
                            dest_pin = p_match.group(1) if p_match else ""

                        elif use_dtdc and ("Ship Date" in text or "DTDC" in text or "TO:" in text):
                            row_client = dtdc_client
                            row_weight = dtdc_weight
                            date_match = re.search(r"Ship Date\s*:\s*(\d{2}-\d{2}-\d{4})", text)
                            final_date = date_match.group(1) if date_match else ""
                            awb_m = re.search(r"([A-Z][0-9]{10})", text)
                            awb = awb_m.group(1) if awb_m else ""
                            n_match = re.search(r"TO:\s*\n?([^\n,]+)", text)
                            dest_name = n_match.group(1).strip() if n_match else ""
                            p_match = re.search(r"Pin[:\-\s]*(\d{6})|PIN[:\-\s]*(\d{6})|(\d{6})", text)
                            if p_match:
                                dest_pin = next((g for g in p_match.groups() if g and len(g) == 6), "")
                            if not row_client:
                                f_match = re.search(r"FROM:\s*\n?([a-zA-Z]+)(\d+)", text)
                                row_client = f_match.group(2) if f_match else ""

                        if awb or dest_name:
                            all_extracted_data.append({
                                "Reference No (A)": "",
                                "Client/Phone (B)": row_client,
                                "Date (C)": final_date,
                                "AWB/Tracking (D)": awb,
                                "Customer Name (E)": dest_name,
                                "Pincode (F)": dest_pin,
                                " (G)": "",
                                "Weight (H)": row_weight
                            })

        if all_extracted_data:
            df = pd.DataFrame(all_extracted_data).fillna("")
            st.success(f"✅ Successfully compiled {len(all_extracted_data)} normalized ledger data streams!")
            st.dataframe(df, use_container_width=True, height=350)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')

            st.download_button(
                "📥 Save Formatted Master Spreadsheet Report",
                data=output.getvalue(),
                file_name="Vaayi_Vega_Extracted_Report.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
        else:
            st.warning("⚠️ No compliant data fields recognized in the current file set structure.")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================================
# PDF REF EXTRACTOR
# ===============================================
elif choice == "📂 PDF Ref Extractor":
    st.markdown('<h2 class="section-title">📂 PDF Reference Extractor Master</h2>', unsafe_allow_html=True)

    st.markdown("""
    <div class="tool-section">
        <p style="margin:0;color:#475569;">
            Supported logic: <b>E25+1 → Group 25</b>, <b>D19+1 → Group 19</b>, duplicate pages skipped, invalid/no-ref pages separated.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_opt1, col_opt2 = st.columns([1, 2])
    with col_opt1:
        skip_awb_only = st.toggle("Skip AWB-only refs", value=True)
    with col_opt2:
        st.markdown('<p class="small-note">Example AWB-only: D1012817623. Enabled ayithe skip report lo ki pothundi.</p>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader("📁 Upload PDF files", type=["pdf"], accept_multiple_files=True, key="pdf_ref_uploader")

    if uploaded_files:
        result = process_pdf_reference_files(uploaded_files, skip_awb_only=skip_awb_only)

        grouped_pages = result["grouped_pages"]
        no_ref_pages = result["no_ref_pages"]
        skipped_pages = result["skipped_pages"]
        extracted_log = result["extracted_log"]
        total_pages_processed = result["total_pages_processed"]
        total_files = result["total_files"]

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div>📂 Groups</div><h2>{len(grouped_pages)}</h2></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div>📄 Files</div><h2>{total_files}</h2></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div>📑 Pages</div><h2>{total_pages_processed}</h2></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div>⏭️ Skipped</div><h2>{len(skipped_pages)}</h2></div>', unsafe_allow_html=True)

        st.divider()

        if grouped_pages:
            st.subheader("📂 Group Downloads")
            cols = st.columns(3)
            for i, (gid, pages) in enumerate(sorted(grouped_pages.items(), key=sort_group_key)):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="group-box">
                        <h4 style="margin:0;color:#1d4ed8;">Group {gid}</h4>
                        <p style="margin:8px 0 0 0;color:#64748b;">{len(pages)} page(s)</p>
                    </div>
                    """, unsafe_allow_html=True)

                    group_pdf = build_pdf_from_pages(pages)
                    st.download_button(
                        label=f"📥 Download Group-{gid}",
                        data=group_pdf,
                        file_name=f"Group_{gid}_{NOW_TS}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"group_{gid}"
                    )

        st.divider()
        c1, c2, c3 = st.columns(3)

        with c1:
            if no_ref_pages:
                no_ref_pdf = build_pdf_from_pages(no_ref_pages)
                st.info(f"No Reference Pages: {len(no_ref_pages)}")
                st.download_button(
                    "📂 Download No-Ref PDF",
                    data=no_ref_pdf,
                    file_name=f"NoRef_{NOW_TS}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.success("No no-ref pages found")

        with c2:
            if skipped_pages:
                st.markdown(f"""
                <div class="skip-box">
                    <h4 style="margin-top:0;">⚠️ Skipped Items</h4>
                    <p style="margin-bottom:0;">{len(skipped_pages)} page(s) skipped</p>
                </div>
                """, unsafe_allow_html=True)

                skip_txt = "SKIPPED PAGES REPORT\n\n" + "\n".join(skipped_pages)
                st.download_button(
                    label="📥 Download Skip Report",
                    data=skip_txt,
                    file_name=f"Skipped_{NOW_TS}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.success("No skipped pages")

        with c3:
            if extracted_log:
                log_txt = "EXTRACTION LOG\n\n" + "\n".join(extracted_log)
                st.markdown(f"""
                <div class="success-box">
                    <h4 style="margin-top:0;">📋 Extraction Log</h4>
                    <p style="margin-bottom:0;">{len(extracted_log)} log entries ready</p>
                </div>
                """, unsafe_allow_html=True)

                st.download_button(
                    label="📥 Download Full Log",
                    data=log_txt,
                    file_name=f"ExtractionLog_{NOW_TS}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        if grouped_pages:
            st.divider()
            all_group_pages = []
            for gid, pages in sorted(grouped_pages.items(), key=sort_group_key):
                all_group_pages.extend(pages)

            all_groups_pdf = build_pdf_from_pages(all_group_pages)
            zip_groups = build_zip_of_groups(grouped_pages)
            total_group_pages = sum(len(v) for v in grouped_pages.values())

            st.markdown(f"""
            <div class="success-box">
                <h4 style="margin-top:0;">✅ Processing Complete</h4>
                <p style="margin-bottom:0;">{len(grouped_pages)} groups / {total_group_pages} grouped page(s)</p>
            </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns(2)
            with b1:
                st.download_button(
                    label="📦 Download All Groups Combined",
                    data=all_groups_pdf,
                    file_name=f"AllGroups_{NOW_TS}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with b2:
                st.download_button(
                    label="🗜️ Download All Groups ZIP",
                    data=zip_groups,
                    file_name=f"AllGroups_{NOW_TS}.zip",
                    mime="application/zip",
                    use_container_width=True
                )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background:#1e293b;padding:12px;border-radius:12px;">
        <h4 style="margin-top:0;color:#93c5fd;">🎯 Logic</h4>
        <pre style="font-size:0.82rem;background:#0f172a;padding:10px;border-radius:10px;color:#e2e8f0;white-space:pre-wrap;">
Delhivery: E25+1  -> Group 25
DTDC:     D19+1  -> Group 19
Generic:  25+1   -> Group 25
AWB only: D1012817623 -> Skip (optional)
No match  -> NoRef PDF
Duplicate -> Skip Report
        </pre>
    </div>
    """, unsafe_allow_html=True)

# ===============================================
# FOOTER
# ===============================================
st.markdown("""
<div style="text-align:center; padding:30px 0; color:#64748b; font-size:0.85rem; font-weight:500;">
    Vayu Vega Logistics Master Automation Engine Suite • Powered by Streamlit Pro Engine © 2026
</div>
""", unsafe_allow_html=True)
