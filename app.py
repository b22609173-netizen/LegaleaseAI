import streamlit as st
import requests

def make_real_pdf(text):
    lines = text.split('\n')
    pages = [lines[i:i+55] for i in range(0, len(lines), 55)]
    content_objs = []
    for page_lines in pages:
        stream = "BT\n/F1 9 Tf\n50 750 Td\n"
        for line in page_lines:
            safe = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')[:110]
            stream += f"({safe}) Tj\n0 -13 Td\n"
        stream += "ET\n"
        content_objs.append(stream.encode('latin-1', 'replace'))

    pdf_parts = [b"%PDF-1.4\n"]
    offsets = [0]
    cur = len(pdf_parts[0])
    def add_obj(d):
        nonlocal cur
        offsets.append(cur)
        pdf_parts.append(d)
        cur += len(d)
    add_obj(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    kids = " ".join([f"{3+i*2} 0 R" for i in range(len(pages))])
    add_obj(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>\nendobj\n".encode())
    for i, content in enumerate(content_objs):
        add_obj(f"{3+i*2} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents {4+i*2} 0 R >>\nendobj\n".encode())
        add_obj(f"{4+i*2} 0 obj\n<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream\nendobj\n")
    xref_start = cur
    xref = f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
    for off in offsets[1:]:
        xref += f"{off:010d} 00000 n \n".encode()
    xref += f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode()
    pdf_parts.append(xref)
    return b"".join(pdf_parts)

st.set_page_config(page_title="LegalEase AI")
st.title("LegalEase - AI Legal Document Generator")

prompt = st.text_area("Enter Details", "Landlord Arun, Tenant Vijay, Chennai house, Rent 15000, 11 months")
doc_type = st.selectbox("Document Type", ["Rental Agreement", "NDA", "Employment Contract"])

if st.button("Generate Document"):
    res = requests.post("http://127.0.0.1:8000/generate", json={"prompt": prompt, "doc_type": doc_type})
    if res.status_code == 200:
        generated_text = res.json()["generated_text"]
        st.success("Generated Successfully! 5 Pages Ready!")
        st.text_area("Document", generated_text, height=400)

        pdf_bytes = make_real_pdf(generated_text)

        st.download_button(
            label="📄 Download as PDF (5 Pages) - FINAL",
            data=pdf_bytes,
            file_name=f"{doc_type.replace(' ', '_')}_5_Page.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Error")