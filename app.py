"""
Azure Document Intelligence Demo - Streamlit Application
"""
import streamlit as st
import io
from PIL import Image
from pdf2image import convert_from_bytes
import pandas as pd
from datetime import datetime

from config import get_config
from document_processor import DocumentProcessor


def init_session_state():
    """Initialize session state variables"""
    if "processed_data" not in st.session_state:
        st.session_state.processed_data = None
    if "original_document" not in st.session_state:
        st.session_state.original_document = None
    if "document_name" not in st.session_state:
        st.session_state.document_name = None


def check_configuration():
    """Check if Azure credentials are configured"""
    config = get_config()
    if not config.is_configured():
        st.error("⚠️ Azure Document Intelligence not configured!")
        missing = config.get_missing_credentials()
        st.write("Missing environment variables:")
        for var in missing:
            st.code(f"export {var}=your_value_here")
        st.write("Please set these environment variables and restart the application.")
        st.stop()
    return config


def display_document_preview(uploaded_file):
    """Display preview of uploaded document"""
    try:
        if uploaded_file.type == "application/pdf":
            try:
                # Convert PDF to images for preview
                pdf_bytes = uploaded_file.getvalue()
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=3)  # Show first 3 pages

                st.write("**Document Preview (First 3 pages):**")
                for i, image in enumerate(images):
                    st.image(image, caption=f"Page {i+1}", use_column_width=True)
                    if i >= 2:  # Limit to 3 pages for preview
                        break
            except Exception as pdf_error:
                st.warning(f"PDF preview unavailable: {str(pdf_error)}")
                st.info("📄 PDF uploaded successfully. Preview requires poppler installation.")
                st.write(f"**File Info:**")
                st.write(f"- Name: {uploaded_file.name}")
                st.write(f"- Size: {uploaded_file.size / 1024:.1f} KB")
                st.write(f"- Type: {uploaded_file.type}")

        elif uploaded_file.type.startswith("image/"):
            # Display image
            image = Image.open(uploaded_file)
            st.image(image, caption="Document Preview", use_column_width=True)

    except Exception as e:
        st.error(f"Error displaying document preview: {str(e)}")


def process_document(uploaded_file, processor):
    """Process document with Azure Document Intelligence"""
    try:
        with st.spinner("🔍 Analyzing document with Azure Document Intelligence..."):
            # Get document bytes
            document_bytes = uploaded_file.getvalue()

            # Process with Azure DI
            result = processor.analyze_document(document_bytes)

            st.session_state.processed_data = result
            st.session_state.original_document = uploaded_file
            st.session_state.document_name = uploaded_file.name

            st.success("✅ Document analysis completed!")

    except Exception as e:
        st.error(f"❌ Document processing failed: {str(e)}")
        return False

    return True


def display_results():
    """Display analysis results"""
    if not st.session_state.processed_data:
        return

    data = st.session_state.processed_data

    # Summary metrics
    st.subheader("📊 Analysis Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Pages", data.get("pages", 0))
    with col2:
        st.metric("Key-Value Pairs", len(data.get("key_value_pairs", [])))
    with col3:
        st.metric("Tables", len(data.get("tables", [])))
    with col4:
        confidence = data.get("confidence_summary", {}).get("average", 0)
        st.metric("Avg Confidence", f"{confidence:.1%}" if confidence else "N/A")

    # Tabbed interface for results
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Key-Value Pairs", "📊 Tables", "📄 Text Content", "🎯 Confidence Details"])

    with tab1:
        display_key_value_pairs(data.get("key_value_pairs", []))

    with tab2:
        display_tables(data.get("tables", []))

    with tab3:
        display_text_content(data.get("text_content", {}))

    with tab4:
        display_confidence_details(data.get("confidence_summary", {}))


def display_key_value_pairs(kv_pairs):
    """Display key-value pairs in a formatted table"""
    if not kv_pairs:
        st.info("No key-value pairs found in the document.")
        return

    st.write(f"**Found {len(kv_pairs)} key-value pairs:**")

    # Convert to DataFrame for better display
    df = pd.DataFrame(kv_pairs)

    # Display without confidence columns
    st.dataframe(
        df[["key", "value"]],
        column_config={
            "key": "Key",
            "value": "Value"
        },
        use_container_width=True
    )


def display_tables(tables):
    """Display extracted tables"""
    if not tables:
        st.info("No tables found in the document.")
        return

    st.write(f"**Found {len(tables)} table(s):**")

    for table in tables:
        st.write(f"**Table {table['table_id']}** ({table['row_count']} rows × {table['column_count']} columns, Confidence: {table['confidence']:.1%})")

        if table["cells"]:
            # Create table matrix
            max_row = max(cell["row_index"] for cell in table["cells"]) + 1
            max_col = max(cell["column_index"] for cell in table["cells"]) + 1

            # Initialize matrix
            matrix = [["" for _ in range(max_col)] for _ in range(max_row)]

            # Fill matrix
            for cell in table["cells"]:
                matrix[cell["row_index"]][cell["column_index"]] = cell["content"]

            # Display as DataFrame
            df = pd.DataFrame(matrix)
            st.dataframe(df, use_container_width=True)

        st.write("---")


def display_text_content(text_data):
    """Display text content by pages"""
    if not text_data or not text_data.get("pages"):
        st.info("No text content found.")
        return

    st.write("**Extracted Text Content:**")

    # Page selector
    page_numbers = [page["page_number"] for page in text_data["pages"]]
    selected_page = st.selectbox("Select Page", page_numbers, key="text_page_selector")

    # Find selected page data
    page_data = next((p for p in text_data["pages"] if p["page_number"] == selected_page), None)

    if page_data:
        st.write(f"**Page {selected_page}** ({len(page_data['lines'])} lines)")

        # Display lines with confidence
        for line in page_data["lines"]:
            confidence_color = "🟢" if line["confidence"] > 0.8 else "🟡" if line["confidence"] > 0.6 else "🔴"
            st.write(f"{confidence_color} {line['content']} *(Confidence: {line['confidence']:.1%})*")


def display_confidence_details(confidence_summary):
    """Display detailed confidence statistics"""
    if not confidence_summary or confidence_summary.get('count', 0) == 0:
        st.info("Confidence scores are not available for the prebuilt-document model. Text OCR confidence is calculated where available.")
        return

    st.write("**Text OCR Confidence Statistics:**")
    st.caption("These scores reflect the OCR engine's confidence in reading the text")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Average Confidence", f"{confidence_summary.get('average', 0):.1%}")
        st.metric("Minimum Confidence", f"{confidence_summary.get('minimum', 0):.1%}")

    with col2:
        st.metric("Maximum Confidence", f"{confidence_summary.get('maximum', 0):.1%}")
        st.metric("Text Elements Analyzed", confidence_summary.get('count', 0))

    # Confidence level breakdown
    avg_conf = confidence_summary.get('average', 0)
    if avg_conf >= 0.9:
        st.success("🟢 Excellent OCR confidence - text is clearly readable")
    elif avg_conf >= 0.7:
        st.warning("🟡 Good OCR confidence - most text is readable")
    else:
        st.error("🔴 Low OCR confidence - document may be blurry or low quality")


def create_download_section():
    """Create download buttons for exports"""
    if not st.session_state.processed_data:
        return

    st.subheader("📥 Export Results")
    col1, col2 = st.columns(2)

    processor = DocumentProcessor("dummy", "dummy")  # We only need export methods

    with col1:
        # JSON Export
        if st.button("📄 Download JSON", use_container_width=True):
            json_data = processor.export_to_json(st.session_state.processed_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"document_analysis_{timestamp}.json"

            st.download_button(
                label="💾 Save JSON File",
                data=json_data,
                file_name=filename,
                mime="application/json",
                use_container_width=True
            )

    with col2:
        # Excel Export
        if st.button("📊 Download Excel", use_container_width=True):
            try:
                excel_bytes, _ = processor.export_to_excel(st.session_state.processed_data)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"document_analysis_{timestamp}.xlsx"

                st.download_button(
                    label="💾 Save Excel File",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Excel export failed: {str(e)}")


def main():
    """Main application"""
    st.set_page_config(
        page_title="Azure Document Intelligence Demo",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize
    init_session_state()
    config = check_configuration()

    # Header
    st.title("🔍 Azure Document Intelligence Demo")
    st.markdown("*Extract key-value pairs, tables, and text from documents using Azure AI*")

    # Sidebar for file upload
    with st.sidebar:
        st.header("📤 Upload Document")

        uploaded_file = st.file_uploader(
            "Choose a PDF or image file",
            type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff"],
            help="Supported formats: PDF, PNG, JPG, JPEG, BMP, TIFF"
        )

        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.write(f"Size: {uploaded_file.size / 1024:.1f} KB")
            st.write(f"Type: {uploaded_file.type}")

            # Process button
            if st.button("🚀 Analyze Document", use_container_width=True):
                processor = DocumentProcessor(config.endpoint, config.key)
                process_document(uploaded_file, processor)

        # Help section
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - **Best results**: Use high-quality, well-lit images
        - **PDF support**: Multi-page PDFs are supported
        - **File size**: Keep files under 50MB for best performance
        - **Formats**: PDF, PNG, JPG, JPEG, BMP, TIFF
        """)

    # Main content area
    if uploaded_file:
        # Two-column layout for document and results
        col1, col2 = st.columns([1, 1])

        with col1:
            st.header("📄 Original Document")
            display_document_preview(uploaded_file)

        with col2:
            st.header("🔍 Extracted Data")
            if st.session_state.processed_data:
                display_results()
            else:
                st.info("👈 Click 'Analyze Document' to start processing")

        # Full-width export section
        if st.session_state.processed_data:
            st.markdown("---")
            create_download_section()

    else:
        # Welcome screen
        st.markdown("""
        ### Welcome to Azure Document Intelligence Demo! 👋

        This application demonstrates the power of Azure Document Intelligence for extracting structured data from documents.

        **Features:**
        - 🔍 **Smart Extraction**: Automatically extract key-value pairs, tables, and text
        - 📊 **Confidence Scores**: See how confident the AI is about each extraction
        - 📥 **Multiple Exports**: Download results as JSON or Excel
        - 👀 **Side-by-Side View**: Compare original document with extracted data

        **Get Started:**
        1. Upload a document using the sidebar
        2. Click "Analyze Document" to process
        3. Explore the extracted data
        4. Export results for further analysis

        **Supported Documents:**
        - Forms and invoices
        - Contracts and agreements
        - Reports and certificates
        - Receipts and statements
        """)


if __name__ == "__main__":
    main()