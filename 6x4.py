import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from reportlab.graphics.barcode import code128
from reportlab.lib.utils import simpleSplit
from datetime import datetime
from PIL import Image
import io
import os
import pandas as pd
import zipfile
import base64

# --- 1. LOGO FOLDER SETUP ---
LOGO_FOLDER = "logos"
if not os.path.exists(LOGO_FOLDER):
    os.makedirs(LOGO_FOLDER)

# --- 2. PDF GENERATION FUNCTION WITH ADVANCED CONTROLS ---
def generate_vayu_vega_label(data, uploaded_logo_bytes, show_fixed_logo, selected_folder_logo_path, options, label_size_option, ctrl=None, canvas_obj=None):
    is_bulk = canvas_obj is not None
    
    # Global Default Controls Setup if not provided
    if ctrl is None:
        ctrl = {
            "title_x": 0.0, "title_y": 0.0, "title_size": 9.0,
            "bc_x": 0.0, "bc_y": 0.0, "bc_width": 1.10, "bc_height": 0.45,
            "logo_x": 0.0, "logo_y": 0.0, "logo_w": 0.40, "logo_h": 0.42,
            "to_x": 0.0, "to_y": 0.0, "to_w": 1.82,
            "from_x": 0.0, "from_y": 0.0, "from_w": 1.50,
            "foot_x": 0.0, "foot_y": 0.0, "foot_size": 6.5
        }

    # 50mm Width x 75mm Height
    if label_size_option == "50mm x 75mm":
        width = (50 / 25.4) * inch   # ~1.96 in
        height = (75 / 25.4) * inch  # ~2.95 in
        is_small_size = True
    else:  # 4x6 Inch Standard
        width, height = 4 * inch, 6 * inch
        is_small_size = False

    if not is_bulk:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))
    else:
        c = canvas_obj

    # Helper function to wrap text
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

    # Outer Boundary Box
    c.setLineWidth(1.2)
    c.rect(0.04 * inch, 0.04 * inch, width - (0.08 * inch), height - (0.08 * inch))
    c.setLineWidth(1)

    if is_small_size:
        # =========================================================================
        # 50mm x 75mm ULTRA JOYSTICK DYNAMIC LAYOUT
        # =========================================================================
        
        # 1. Header Title Control
        title_x_pos = (width / 2) + (ctrl["title_x"] * inch)
        title_y_pos = height - (0.22 * inch) + (ctrl["title_y"] * inch)
        c.setFont("Helvetica-Bold", ctrl["title_size"])
        c.drawCentredString(title_x_pos, title_y_pos, "VAYU VEGA EXPRESS")
        c.line(0.06 * inch, height - (0.28 * inch), width - (0.06 * inch), height - (0.28 * inch))
        
        # 2. Barcode Control
        awb = str(data.get('awb', 'N/A'))
        bc_x_pos = 0.12 * inch + (ctrl["bc_x"] * inch)
        bc_y_pos = height - (0.78 * inch) + (ctrl["bc_y"] * inch)
        
        try:
            awb_barcode = code128.Code128(awb, barHeight=ctrl["bc_height"] * inch, barWidth=ctrl["bc_width"])
            awb_barcode.quiet = 0  
            awb_barcode.drawOn(c, bc_x_pos, bc_y_pos)
        except:
            pass
        
        # 3. Dynamic Logo Control
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
        
        # 4. TO ADDRESS SECTION (Position & Boundary Width)
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
        
        # 5. FROM ADDRESS SECTION (Position & Boundary Width)
        bottom_area_y = 1.05 * inch
        
        if options['show_from']:
            from_x = width - (1.6 * inch) + (ctrl["from_x"] * inch)
            from_w = ctrl["from_w"] * inch  
            from_y = (bottom_area_y - 45) + (ctrl["from_y"] * inch)
            
            from_phone = data.get('from_phone','') if options['show_mobile'] else "0000000000"
            
            from_y = draw_wrapped_text(c, f"FROM: {data.get('from_name','')}".upper(), from_x, from_y, from_w, "Helvetica", 6.5, bold=True, align="right")
            from_y = draw_wrapped_text(c, f"PH: {from_phone}", from_x, from_y, from_w, "Helvetica", 6, bold=True, align="right")
            draw_wrapped_text(c, data.get('from_address',''), from_x, from_y, from_w, "Helvetica", 5, bold=False, line_spacing=1.1, align="right")
            
        # 6. FOOTER AREA (Thank you & Date Control)
        foot_y_pos = 0.10 * inch + (ctrl["foot_y"] * inch)
        foot_x_pos = 0.08 * inch + (ctrl["foot_x"] * inch)
        c.setFont("Helvetica-Bold", ctrl["foot_size"])
        c.drawString(foot_x_pos, foot_y_pos, "THANK YOU - VAYU VEGA")
        c.drawRightString(width - (0.08 * inch) + (ctrl["foot_x"] * inch), foot_y_pos, f"DT: {data.get('label_date','')}")

    else:
        # ==========================================
        # STANDARD 4X6 INCH LAYOUT (Untouched)
        # ==========================================
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
            except: pass

        c.line(0.12 * inch, line_y, width - (0.12 * inch), line_y)

        awb = str(data.get('awb', 'N/A'))
        awb_barcode = code128.Code128(awb, barHeight=0.6 * inch, barWidth=1.8)
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
        ref_bar = code128.Code128(ref, barHeight=0.4 * inch, barWidth=1.0)
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

# --- Helper to Show PDF Embed Frame ---
def show_pdf_preview(pdf_buffer, height=520):
    base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0&scrollbar=0" width="100%" height="{height}px" style="border: 2px solid #ddd; border-radius: 8px;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 3. STREAMLIT UI ---
st.set_page_config(page_title="Vayu Vega Ultra Pro", layout="wide")
st.title("🚀 Vayu Vega Multi-Tool - Advanced Label Controls")

# --- SIDEBAR GLOBAL SETTINGS ---
st.sidebar.header("⚙️ General Settings")
label_size = st.sidebar.selectbox("📐 Label Dimensions (Size)", ["50mm x 75mm", "4x6 Inch"])

show_logo = st.sidebar.checkbox("Show Fixed Logo (logo.png)", value=True)
uploaded_logo = st.sidebar.file_uploader("Upload Temporary Logo", type=['png', 'jpg'])

st.sidebar.markdown("---")
st.sidebar.header("👁️ Visibility Controls")
opt_amount = st.sidebar.toggle("Show Total Amount", value=True)
opt_mobile = st.sidebar.toggle("Show Mobile Numbers", value=True)
opt_from = st.sidebar.toggle("Show Sender (FROM) Details", value=True)

display_options = {
    'show_amount': opt_amount,
    'show_mobile': opt_mobile,
    'show_from': opt_from
}

logo_files = [f for f in os.listdir(LOGO_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))] if os.path.exists(LOGO_FOLDER) else []
selected_logo_name = st.sidebar.selectbox("Select Branch Logo", ["None"] + logo_files)
folder_logo_path = os.path.join(LOGO_FOLDER, selected_logo_name) if selected_logo_name != "None" else None

# --- DYNAMIC MASTER CONTROLS (JOYSTICKS & BOUNDARIES) ---
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
    st.sidebar.header("🕹️ Super Joysticks Dashboard")
    
    lock_dashboard = st.sidebar.toggle("🔒 LOCK ALL POSITIONS & BOUNDARIES", value=False, help="దీన్ని ఆన్ చేస్తే కింద ఉన్న కంట్రోల్స్ అన్నీ లాక్ అయిపోతాయి.")
    
    if not lock_dashboard:
        # Expander 1: Title Header
        with st.sidebar.expander("📝 1. Header Title Controls"):
            ctrl["title_x"] = st.slider("Title X (L/R)", -0.5, 0.5, 0.0, step=0.01)
            ctrl["title_y"] = st.slider("Title Y (Up/Down)", -0.3, 0.3, 0.0, step=0.01)
            ctrl["title_size"] = st.slider("Title Font Size", 6.0, 14.0, 9.0, step=0.5)

        # Expander 2: Barcode
        with st.sidebar.expander("📊 2. Barcode & Scale"):
            ctrl["bc_x"] = st.slider("Barcode X", -0.5, 0.5, 0.0, step=0.01)
            ctrl["bc_y"] = st.slider("Barcode Y", -0.5, 0.5, 0.0, step=0.01)
            ctrl["bc_width"] = st.slider("Barcode Bar Width (Scale)", 0.7, 1.8, 1.10, step=0.05)
            ctrl["bc_height"] = st.slider("Barcode Height (Size)", 0.2, 0.8, 0.45, step=0.05)

        # Expander 3: Logo
        with st.sidebar.expander("🖼️ 3. Branch Logo Scale"):
            ctrl["logo_x"] = st.slider("Logo X", -0.5, 0.5, 0.0, step=0.01)
            ctrl["logo_y"] = st.slider("Logo Y", -0.5, 0.5, 0.0, step=0.01)
            ctrl["logo_w"] = st.slider("Logo Max Width", 0.2, 1.0, 0.40, step=0.02)
            ctrl["logo_h"] = st.slider("Logo Max Height", 0.2, 1.0, 0.42, step=0.02)

        # Expander 4: TO Address
        with st.sidebar.expander("📍 4. TO Address Boundary"):
            ctrl["to_x"] = st.slider("TO X", -0.4, 0.4, 0.0, step=0.01)
            ctrl["to_y"] = st.slider("TO Y", -0.5, 0.5, 0.0, step=0.01)
            ctrl["to_w"] = st.slider("TO Boundary Wrap Width", 1.0, 2.5, 1.82, step=0.02)

        # Expander 5: FROM Address
        if opt_from:
            with st.sidebar.expander("🏢 5. FROM Address Boundary"):
                ctrl["from_x"] = st.slider("FROM X", -0.5, 0.5, 0.0, step=0.01)
                ctrl["from_y"] = st.slider("FROM Y", -0.5, 0.5, 0.0, step=0.01)
                ctrl["from_w"] = st.slider("FROM Boundary Width", 0.8, 2.2, 1.50, step=0.02)

        # Expander 6: Footer Thanks & Date
        with st.sidebar.expander("🎉 6. Footer Text & Date"):
            ctrl["foot_x"] = st.slider("Footer X", -0.3, 0.3, 0.0, step=0.01)
            ctrl["foot_y"] = st.slider("Footer Y", -0.2, 0.4, 0.0, step=0.01)
            ctrl["foot_size"] = st.slider("Footer Font Size", 4.0, 10.0, 6.5, step=0.5)
    else:
        st.sidebar.success("🔒 System Dashboard is Locked Securely.")

tab1, tab2 = st.tabs(["📄 Single Label", "📂 Bulk Upload"])

with tab1:
    c_form, c_view = st.columns([3, 2])
    
    with c_form:
        with st.form("single_form"):
            c1, c2 = st.columns(2)
            with c1:
                awb_no = st.text_input("AWB", "VV-100200")
                p_name, p_val = st.text_input("Product", "General"), st.text_input("Value", "1000")
                l_date = st.text_input("Date", datetime.now().strftime("%d-%m-%Y"))
                wt, t_amt, ref_no = st.text_input("Weight", "0.5"), st.text_input("Total Bill", "1100"), st.text_input("Ref", "REF-01")
                mode_opt = st.selectbox("Shipping Mode", ["Surface", "Express"])
                risk_opt = st.selectbox("Risk Type", ["Carrier", "No Risk"])
                
            with c2:
                t_name, t_phone, t_pin = st.text_input("To Name", "CHINNA RAO"), st.text_input("To Phone", "9876543210"), st.text_input("To Pin", "500001")
                t_addr = st.text_area("To Address", "D.No: 4-56/A, Main Road, Near Ramalayam Temple, Gudivada, Andhra Pradesh")
                f_name, f_phone = st.text_input("From Name", "Vayu Vega Hub"), st.text_input("From Phone", "8888888888")
                f_addr = st.text_area("From Address", "Hub Main Center, Vijayawada")
            
            submit_single = st.form_submit_button("🔥 Update Design & Prepare Label")

    # Data Sync Setup
    l_data = {
        'awb': awb_no, 'product_name': p_name, 'product_value': p_val, 'label_date': l_date, 
        'ref': ref_no, 'weight': wt, 'total_amount': t_amt, 'to_name': t_name, 
        'to_phone': t_phone, 'to_pincode': t_pin, 'to_address': t_addr, 
        'from_name': f_name, 'from_phone': f_phone, 'from_address': f_addr,
        'mode': mode_opt, 'risk': risk_opt
    }
    
    # Generate Live Output
    current_pdf = generate_vayu_vega_label(
        l_data, uploaded_logo.getvalue() if uploaded_logo else None, 
        show_logo, folder_logo_path, display_options, label_size, ctrl=ctrl
    )

    with c_view:
        st.subheader("🖥️ Super HD Live Preview")
        show_pdf_preview(current_pdf, height=540)
        st.download_button(f"📥 Download Current Design PDF", current_pdf, f"{awb_no}_{ref_no}.pdf", use_container_width=True)

with tab2:
    st.info("💡 CSV లేదా Excel ఫైల్‌ను అప్‌లోడ్ చేయండి. పైన సెట్ చేసిన జాయ్‌స్టిక్ సెట్టింగ్స్ అన్ని లేబుల్స్‌కి అప్లై అవుతాయి.")

    sample_data = {
        'awb': ['VV1001', 'VV1002'], 
        'product_name': ['General', 'Electronics'], 
        'product_value': ['1000', '5000'],
        'label_date': [datetime.now().strftime("%d-%m-%Y"), datetime.now().strftime("%d-%m-%Y")], 
        'ref': ['REF01', 'REF02'], 
        'weight': ['0.5', '1.2'],
        'total_amount': ['1100', '5200'], 
        'to_name': ['Rahul Kumar', 'Suresh Kumar'], 
        'to_phone': ['9876543210', '9999999999'],
        'to_pincode': ['500001', '520001'], 
        'to_address': ['H.No 1-2, Ameerpet, Hyderabad, Telangana', 'Plot 45, Benz Circle, Vijayawada, AP'], 
        'from_name': ['Vayu Vega Hub', 'Vayu Vega Hub'],
        'from_phone': ['8888888888', '8888888888'], 
        'from_address': ['Hub Main Road', 'Hub Main Road'],
        'mode': ['Surface', 'Express'], 
        'risk': ['Carrier', 'No Risk']
    }
    sample_df = pd.DataFrame(sample_data)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        csv_data = sample_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Sample CSV", data=csv_data, file_name="vayu_vega_sample.csv", mime="text/csv")
    with col_s2:
        output_xlsx = io.BytesIO()
        with pd.ExcelWriter(output_xlsx, engine='openpyxl') as writer:
            sample_df.to_excel(writer, index=False)
        st.download_button("📥 Download Sample Excel", data=output_xlsx.getvalue(), file_name="vayu_vega_sample.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("---")
    uploaded_file = st.file_uploader("Upload Your CSV or Excel File", type=['csv', 'xlsx'])
    
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.write("### Select Labels to Generate")
        
        if "Select" not in df.columns:
            df.insert(0, "Select", True)
            
        edited_df = st.data_editor(df, hide_index=True, use_container_width=True)
        selected_rows = edited_df[edited_df["Select"] == True]
        
        if st.button(f"Generate Labels for {len(selected_rows)} Selected Rows"):
            if len(selected_rows) == 0:
                st.error("Please select at least one row!")
            else:
                logo_bytes = uploaded_logo.getvalue() if uploaded_logo else None
                zip_buffer = io.BytesIO()
                bulk_pdf_buffer = io.BytesIO()
                
                if label_size == "50mm x 75mm":
                    b_width = (50 / 25.4) * inch
                    b_height = (75 / 25.4) * inch
                else:
                    b_width, b_height = 4 * inch, 6 * inch
                    
                bulk_c = canvas.Canvas(bulk_pdf_buffer, pagesize=(b_width, b_height))

                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for idx, row in selected_rows.iterrows():
                        l_dict = row.to_dict()
                        l_dict.pop('Select', None)
                        
                        single_pdf = generate_vayu_vega_label(l_dict, logo_bytes, show_logo, folder_logo_path, display_options, label_size, ctrl=ctrl)
                        
                        f_name = f"{l_dict.get('awb', idx)}_{l_dict.get('ref', 'REF')}.pdf"
                        zip_file.writestr(f_name, single_pdf.getvalue())
                        
                        generate_vayu_vega_label(l_dict, logo_bytes, show_logo, folder_logo_path, display_options, label_size, ctrl=ctrl, canvas_obj=bulk_c)
                
                bulk_c.save()
                bulk_pdf_buffer.seek(0)
                
                st.success(f"🎯 {len(selected_rows)} Labels Generated with Customized Dashboard Setup!")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(f"📥 Download ZIP ({label_size})", zip_buffer.getvalue(), "Selected_Labels.zip")
                with col_d2:
                    st.download_button(f"📥 Download Combined PDF ({label_size})", bulk_pdf_buffer.getvalue(), "Selected_Labels_Combined.pdf")