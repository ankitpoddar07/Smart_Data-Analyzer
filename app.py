import streamlit as st
import pandas as pd
import plotly.express as px
import os
import tempfile
from fpdf import FPDF
import plotly.io as pio
import base64
from io import BytesIO

# Set up Streamlit page
st.set_page_config(page_title="Data Analyzer", layout="wide")
st.title("📊 Smart Data Analyzer :")

# File upload functionality with better validation
uploaded_file = st.sidebar.file_uploader(
    "📤 Upload your Excel or CSV file", 
    type=["xlsx", "xls", "csv"],
    help="Upload a file with at least 2 columns (one categorical, one numeric)"
)

def validate_dataframe(df):
    """Validate the dataframe meets our requirements"""
    if df.empty:
        st.error("❌ The file is empty. Please upload a file with data.")
        return False
    
    if len(df.columns) < 2:
        st.error("❌ The file needs at least 2 columns to create visualizations.")
        return False
    
    # Check for at least one numeric and one categorical column
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'datetime']).columns.tolist()
    
    if not numeric_cols:
        st.error("❌ No numeric columns found. Please include at least one column with numbers.")
        return False
    
    if not categorical_cols:
        st.error("❌ No categorical columns found. Please include at least one text or date column.")
        return False
    
    return True

def load_data(uploaded_file):
    """Load data from uploaded file with proper error handling"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:  # Excel file
            df = pd.read_excel(uploaded_file)
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Convert string numbers to numeric
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass
        
        return df
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        return None

# Load data
df = None
if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None and not validate_dataframe(df):
        st.stop()
else:
    # Use default file if no upload
    file_path = "data/coffee_sales_full.xlsx"
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, sheet_name="Coffee Sales")
            if not validate_dataframe(df):
                st.stop()
        except Exception as e:
            st.error(f"❌ Error reading default file: {str(e)}")
            st.stop()
    else:
        st.info("ℹ️ No default file found. Please upload your data file.")
        st.stop()

# Data preparation
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category', 'datetime']).columns.tolist()

# Initialize filtered_df with full dataset
filtered_df = df.copy()

# Sidebar Filters
st.sidebar.header("📊 Filter Options")

if len(categorical_cols) >= 1:
    col1 = st.sidebar.selectbox("Select first filter column", categorical_cols)
    filter1_options = ['All'] + df[col1].unique().tolist()
    filter1 = st.sidebar.selectbox(f"Select {col1}", filter1_options)
    
    if filter1 != 'All':
        filtered_df = filtered_df[filtered_df[col1] == filter1]

if len(categorical_cols) >= 2 and len(filtered_df) > 0:
    available_cols = [col for col in categorical_cols if col != col1]
    if available_cols:
        col2 = st.sidebar.selectbox("Select second filter column", available_cols)
        filter2_options = ['All'] + filtered_df[col2].unique().tolist()
        filter2 = st.sidebar.selectbox(f"Select {col2}", filter2_options)
        
        if filter2 != 'All':
            filtered_df = filtered_df[filtered_df[col2] == filter2]

# Add option to view full data or top 20 rows
data_view_option = st.radio(
    "Select data view:",
    ("Top 20 Rows", "Full Data"),
    horizontal=True,
    index=0
)

# Show data table based on user selection
st.subheader(f"📋 Filtered Data ({data_view_option})")
if data_view_option == "Top 20 Rows":
    st.dataframe(filtered_df.head(20), use_container_width=True)
else:
    st.dataframe(filtered_df, use_container_width=True)

# Chart selection
st.sidebar.header("📈 Chart Options")
chart_types = {
    "Bar Chart": px.bar,
    "Line Chart": px.line,
    "Pie Chart": px.pie,
    "Scatter Plot": px.scatter,
    "Histogram": px.histogram
}

# Initialize figures list
figures = []

# Chart 1
if len(numeric_cols) >= 1 and len(categorical_cols) >= 1 and len(filtered_df) > 0:
    st.subheader("📊 Chart 1")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        col1_x = st.selectbox("X-axis for Chart 1", categorical_cols, key="x1")
    with col2:
        col1_y = st.selectbox("Y-axis for Chart 1", numeric_cols, key="y1")
    with col3:
        chart1_type = st.selectbox("Chart 1 Type", list(chart_types.keys()), key="c1")
    
    try:
        if chart1_type == "Pie Chart":
            # Pie charts need different handling
            agg_df1 = filtered_df.groupby(col1_x)[col1_y].sum().reset_index()
            fig1 = px.pie(agg_df1, names=col1_x, values=col1_y, title=f"{col1_y} by {col1_x}")
        elif chart1_type == "Histogram":
            agg_df1 = filtered_df[[col1_x, col1_y]].copy()
            fig1 = px.histogram(agg_df1, x=col1_x, y=col1_y, title=f"{col1_y} by {col1_x}")
        else:
            agg_df1 = filtered_df.groupby(col1_x)[col1_y].sum().reset_index()
            fig1 = chart_types[chart1_type](agg_df1, x=col1_x, y=col1_y, title=f"{col1_y} by {col1_x}")
        
        st.plotly_chart(fig1, use_container_width=True)
        figures.append(fig1)
    except Exception as e:
        st.warning(f"⚠️ Could not create Chart 1: {str(e)}")

# Chart 2 - Only show if we have enough data
if len(numeric_cols) >= 2 and len(categorical_cols) >= 1 and len(filtered_df) > 0:
    st.subheader("📊 Chart 2")
    
    # Exclude the column already used in Chart 1 if possible
    available_x_cols = [col for col in categorical_cols if col != col1_x] if 'col1_x' in locals() else categorical_cols
    available_y_cols = [col for col in numeric_cols if col != col1_y] if 'col1_y' in locals() else numeric_cols
    
    if available_x_cols and available_y_cols:
        col1, col2, col3 = st.columns(3)
        with col1:
            col2_x = st.selectbox("X-axis for Chart 2", available_x_cols, key="x2")
        with col2:
            col2_y = st.selectbox("Y-axis for Chart 2", available_y_cols, key="y2")
        with col3:
            chart2_type = st.selectbox("Chart 2 Type", list(chart_types.keys()), key="c2")
        
        try:
            if chart2_type == "Pie Chart":
                # Pie charts need different handling
                agg_df2 = filtered_df.groupby(col2_x)[col2_y].sum().reset_index()
                fig2 = px.pie(agg_df2, names=col2_x, values=col2_y, title=f"{col2_y} by {col2_x}")
            elif chart2_type == "Histogram":
                agg_df2 = filtered_df[[col2_x, col2_y]].copy()
                fig2 = px.histogram(agg_df2, x=col2_x, y=col2_y, title=f"{col2_y} by {col2_x}")
            else:
                agg_df2 = filtered_df.groupby(col2_x)[col2_y].sum().reset_index()
                fig2 = chart_types[chart2_type](agg_df2, x=col2_x, y=col2_y, title=f"{col2_y} by {col2_x}")
            
            st.plotly_chart(fig2, use_container_width=True)
            figures.append(fig2)
        except Exception as e:
            st.warning(f"⚠️ Could not create Chart 2: {str(e)}")

# --- Enhanced PDF Export Function ---
def generate_pdf(data, figs, filters):
    """Generate PDF report with properly spaced tables and charts"""

    # Set landscape orientation and margins
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # Title
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Smart Data Analyzer Report", ln=True, align='C')
    pdf.ln(5)

    # Show Filters
    if filters:
        pdf.set_font("Arial", '', 10)
        filter_text = ", ".join([f"{k} = {v}" for k, v in filters.items() if v != 'All'])
        pdf.multi_cell(0, 8, f"Filters Applied: {filter_text}", align='C')
        pdf.ln(5)

    # Section: Data Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Data Summary (Top 20 Rows)", ln=True)
    pdf.ln(3)

    # Extract top 20 rows
    sample_data = data.head(20)
    col_names = list(sample_data.columns)

    # Determine column width
    num_cols = len(col_names)
    available_width = 270  # A4 landscape usable width
    col_width = max(20, available_width / num_cols)  # Minimum 20mm

    # Table Header
    pdf.set_font("Arial", 'B', 7)
    for col in col_names:
        pdf.cell(col_width, 6, str(col)[:25], border=1, align='C')
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", '', 7)
    for _, row in sample_data.iterrows():
        for item in row:
            text = str(item)
            pdf.cell(col_width, 6, text[:25], border=1)
        pdf.ln()

    # Charts Section
    temp_dir = tempfile.mkdtemp()
    for i, fig in enumerate(figs):
        try:
            chart_path = os.path.join(temp_dir, f"chart_{i+1}.png")
            pio.write_image(fig, chart_path, format='png', width=1000, height=500, scale=2)
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Chart {i+1}", ln=True)
            pdf.image(chart_path, x=10, y=25, w=270)
        except Exception as e:
            pdf.add_page()
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 10, f"Could not render chart {i+1}: {str(e)}", ln=True)

    # Output PDF as BytesIO
    pdf_output = pdf.output(dest='S').encode('latin1', errors='ignore')
    pdf_bytes = BytesIO(pdf_output)

    # Cleanup temp files
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)

    return pdf_bytes


# PDF Export Button - UPDATED VERSION
if not filtered_df.empty and len(figures) > 0:
    if st.button("⬇️ Generate Full Report", help="Download a PDF with the current data and charts"):
        # Get current filters
        filters = {}
        if 'col1' in locals() and 'filter1' in locals(): 
            if filter1 != 'All':
                filters[col1] = filter1
        if 'col2' in locals() and 'filter2' in locals(): 
            if filter2 != 'All':
                filters[col2] = filter2
        
        with st.spinner("Generating PDF report..."):
            try:
                # Generate PDF
                pdf_bytes = generate_pdf(filtered_df, figures, filters)
                
                # Create download button
                st.download_button(
                    label="📥 Download Full Report (PDF)",
                    data=pdf_bytes.getvalue(),
                    file_name="data_analysis_report.pdf",
                    mime="application/pdf"
                )
                
                st.success("✅ PDF report generated successfully! Click the download button above.")
                
            except Exception as e:
                st.error(f"❌ Failed to generate PDF: {str(e)}")
                st.error("Please check if you have write permissions in the temporary directory.")
elif len(figures) == 0:
    st.warning("⚠️ No charts available to include in report. Please create at least one chart.")
else:
    st.warning("⚠️ No data available for report generation.")

# Data validation tips
if uploaded_file is not None and len(figures) == 0:
    st.info("""
    💡 **Tips for better results:**
    
    1. Make sure your file has both numeric and text/date columns
    2. Column headers should be in the first row
    3. Avoid blank rows or columns
    4. Numeric columns should contain only numbers
    5. For best results, structure your data like:
    
    | Date       | Product | Sales |
    |------------|---------|-------|
    | 2023-01-01 | Coffee  | 100   |
    | 2023-01-02 | Tea     | 75    |
    """)