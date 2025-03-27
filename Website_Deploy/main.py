import streamlit as st
import sqlite3

#BACKGROUND COLOUR
st.set_page_config(page_title="SALZZ FINANCE",layout="wide")

st.markdown(
    """
    <style>
        /* Main page background */
        .main {
            background: linear-gradient(135deg, #FFA500, #32CD32);  
        }

        /* Sidebar background */
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, #32CD32, #FFA500);  
        }
    </style>
    """,
    unsafe_allow_html=True
)



# Initialize database connection
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Initialize DB
init_db()

st.markdown("""
    <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideIn {
            from { transform: translateY(-20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @keyframes bgTransition {
            0% { background: #0f2027; }
            50% { background: #203a43; }
            100% { background: #2c5364; }
        }
        body {
            background: linear-gradient(to right, #0f2027, #203a43);
            animation: bgTransition 5s ease-in-out infinite alternate;
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 60px 20px;
        }
        .title {
            font-size: 60px;
            font-weight: bold;
            color: #FFD700;
            animation: slideIn 2s ease-in-out;
        }
        .subheader {
            font-size: 28px;
            color: #FFA500;
            animation: fadeIn 3s ease-in-out;
            margin-bottom: 20px;
        }
        .content {
            font-size: 20px;
            max-width: 900px;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: left;
            animation: fadeIn 3s ease-in-out;
        }
        .cta-button {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .cta-button a {
            background: #FFD700;
            color: #000;
            padding: 12px 30px;
            font-size: 20px;
            font-weight: bold;
            text-decoration: none;
            border-radius: 5px;
            transition: 0.3s;
        }
        .cta-button a:hover {
            background: #FFA500;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class='container'>
        <div class='title'>Welcome to AI-Powered Fintech</div>
        <div class='subheader'>Revolutionizing Financial Wellness Through AI</div>
        <div class='content'>
            <p>SALZZ FINANCE is a wellness platform designed to provide users with personalized financial insights,
            budgeting recommendations, investment strategies, and debt management solutions. By leveraging advanced 
            machine learning algorithms, we analyze financial patterns and help users make informed decisions for a 
            secure and prosperous future.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
*Key Features:*

                    \t- 📊 *Smart Budgeting*: AI-driven recommendations based on income, expenses, and spending habits.
                    - 💹 *Investment Strategies*: Tailored investment suggestions aligned with your financial goals.
                    - 📉 *Debt Management*: Optimize repayments and manage financial obligations effectively.
                    - 🌍 *Cross-Platform Accessibility*: Use our platform on any device, anywhere, anytime.
                    - 🔒 *Banking API Integration*: Securely connect with financial institutions for seamless transactions.
""")

st.markdown("""
    <div class='cta-button'>
        <a href='/signup' target='_self'>Get Started</a>
    </div>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import pdfplumber
import os


# Create upload directory
upload_folder = "uploads"
os.makedirs(upload_folder, exist_ok=True)

# PDF Extraction Function
def extract_tables_from_pdf(pdf_path):
    """Extract tables from PDF and return as DataFrame with cleaned columns"""
    all_data = []
    column_names = None

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_table()

                if tables:
                    # Convert all table cells to strings and handle empty cells
                    tables = [[str(cell) if cell is not None else '' for cell in row] for row in tables]

                    if not column_names:
                        # Use the first table's header as column names
                        column_names = tables[0]

                        # Handle empty column names
                        column_names = [
                            f"Unnamed_{i}" if col == '' else col
                            for i, col in enumerate(column_names)
                        ]

                        # Fix duplicate column names using pd.Series
                        column_names = pd.Series(column_names).apply(
                            lambda x: x if column_names.count(x) == 1 else f"{x}_{column_names.count(x)}"
                        ).tolist()

                        data_rows = tables[1:]

                        # Adjust rows to match the column count
                        for row in data_rows:
                            if len(row) < len(column_names):
                                row.extend([''] * (len(column_names) - len(row)))  # Pad with empty cells
                            elif len(row) > len(column_names):
                                row = row[:len(column_names)]  # Trim excess columns
                            
                            all_data.append(row)
                    else:
                        # Adjust subsequent tables to match existing headers
                        for row in tables:
                            if len(row) < len(column_names):
                                row.extend([''] * (len(column_names) - len(row)))  # Pad
                            elif len(row) > len(column_names):
                                row = row[:len(column_names)]  # Trim
                            
                            all_data.append(row)

        # Create DataFrame with cleaned columns
        if all_data and column_names:
            df = pd.DataFrame(all_data, columns=column_names)
            
            # Ensure no duplicate columns after DataFrame creation using pd.Series
            df.columns = pd.Series(df.columns).apply(
                lambda x: x if list(df.columns).count(x) == 1 else f"{x}_{list(df.columns).count(x)}"
            ).tolist()

            return df
        else:
            return None

    except Exception as e:
        st.error(f"Error extracting PDF: {str(e)}")
        return None


# Streamlit UI
st.title("📄 PDF Table Extractor")
st.write("Upload a PDF file with tabular data, and extract it into a DataFrame.")

# PDF Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    # Save the uploaded file
    file_path = os.path.join(upload_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"Uploaded PDF: {uploaded_file.name}")

    # Extract data
    with st.spinner("Extracting tables from PDF..."):
        df = extract_tables_from_pdf(file_path)
        
        if df is not None:
            st.success("✅ PDF tables extracted successfully!")

            # Display extracted DataFrame
            st.dataframe(df)

            # Download buttons
            st.markdown("### 📥 Download Extracted Data")

            col1, col2 = st.columns(2)

            # Download CSV
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name="extracted_data.csv",
                    mime="text/csv"
                )

            # Download Excel
            with col2:
                excel = df.to_excel("extracted_data.xlsx", index=False)
                with open("extracted_data.xlsx", "rb") as f:
                    st.download_button(
                        label="Download as Excel",
                        data=f,
                        file_name="extracted_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.error("⚠️ No tables were found in the PDF.")


