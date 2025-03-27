import streamlit as st
import hashlib
import os
import json
from datetime import datetime
import uuid
import pdfplumber
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
import google.generativeai as genai  # Import Google Generative AI

load_dotenv()

# Initialize Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Gemini API key loaded successfully from .env file")
else:
    print("Gemini API key not found in .env file. Financial advice features will be limited.")
    # We'll handle this in the financial_advice_page method

class MobileAuthApp:
    def __init__(self):
        # Initialize session state variables
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
        
        # User credentials file
        self.credentials_file = 'user_credentials.txt'
        
        # PDF upload directory
        self.upload_dir = 'uploaded_pdfs'
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # PDF metadata file
        self.pdf_metadata_file = 'pdf_metadata.json'
        if not os.path.exists(self.pdf_metadata_file):
            with open(self.pdf_metadata_file, 'w') as f:
                json.dump({}, f)
        
        # Custom CSS for dark-themed mobile-like design
        self.apply_custom_css()
    
    def apply_custom_css(self):
        st.markdown("""
        <style>
        :root {
            /* Dark theme color palette */
            --bg-primary: #121212;
            --bg-secondary: #1E1E1E;
            --text-primary: #E0E0E0;
            --text-secondary: #B0B0B0;
            --accent-primary: #BB86FC;
            --accent-secondary: #03DAC6;
        }
        
        .stApp {
            max-width: 400px;
            margin: 0 auto;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
        }
        
        /* Override Streamlit default styles */
        .stTextInput > div > div > input {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--accent-primary) !important;
            border-radius: 10px;
            height: 50px;
            padding: 0 15px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--accent-secondary) !important;
            box-shadow: 0 0 5px rgba(187, 134, 252, 0.5);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
            color: var(--bg-primary) !important;
            font-weight: bold;
            border-radius: 25px;
            height: 50px;
            width: 100%;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            opacity: 0.9 !important;
            transform: scale(1.02);
        }
        
        .login-container {
            background-color: var(--bg-secondary);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }
        
        /* Custom link styles */
        a {
            color: var(--accent-secondary);
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        a:hover {
            color: var(--accent-primary);
            text-decoration: underline;
        }
        
        /* Error and success message styles */
        .stAlert-error {
            background-color: rgba(255, 23, 68, 0.1);
            color: #FF1744;
            border-left: 4px solid #FF1744;
        }
        
        .stAlert-success {
            background-color: rgba(0, 230, 118, 0.1);
            color: #00E676;
            border-left: 4px solid #00E676;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def hash_credentials(self, username, password):
        """
        Convert username and password to SHA-256 hash
        """
        # Combine username and password before hashing
        combined = f"{username}:{password}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def save_credentials(self, name, client_id, username, password):
        """
        Save user credentials to a text file
        """
        hashed_credentials = self.hash_credentials(username, password)
        
        # Check if credentials already exist
        if self.check_credentials_exist(hashed_credentials):
            return False
        
        # Append new credentials to file
        with open(self.credentials_file, 'a') as f:
            # Format: hashed_credentials,name,client_id,username
            f.write(f"{hashed_credentials},{name},{client_id},{username}\n")
        
        return True
    
    def check_credentials_exist(self, hashed_credentials):
        """
        Check if hashed credentials already exist in the file
        """
        if not os.path.exists(self.credentials_file):
            return False
        
        with open(self.credentials_file, 'r') as f:
            for line in f:
                if line.startswith(hashed_credentials):
                    return True
        
        return False
    
    def validate_login(self, username, password):
        """
        Validate user login credentials
        """
        hashed_credentials = self.hash_credentials(username, password)
        
        if not os.path.exists(self.credentials_file):
            return False
        
        with open(self.credentials_file, 'r') as f:
            for line in f:
                if line.startswith(hashed_credentials):
                    return True
        
        return False
    
    def login_page(self):
        """Render login page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Welcome Back</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:var(--text-secondary);">Sign in to continue</p>', unsafe_allow_html=True)
        
        # Login form
        username = st.text_input("Username", key="login_username", 
                                 help="Enter your registered username")
        password = st.text_input("Password", type="password", key="login_password",
                                 help="Enter your account password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_btn = st.button("Login")
        
        with col2:
            signup_btn = st.button("Create Account")
        
        if login_btn:
            if username and password:
                if self.validate_login(username, password):
                    # Set session state for login
                    st.session_state['current_username'] = username
                    st.session_state['page'] = 'file_upload'
                    # Use st.rerun() instead of st.experimental_rerun()
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please fill in all fields")
        
        if signup_btn:
            st.session_state['page'] = 'signup'
            st.rerun()
        
        # Forgot password link
        st.markdown('''
        <div style="text-align:center; margin-top:10px;">
            <a href="#">Forgot Password?</a>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def signup_page(self):
        """Render signup page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Create Account</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:var(--text-secondary);">Join our platform</p>', unsafe_allow_html=True)
        
        # Signup form
        name = st.text_input("Full Name", key="signup_name",
                             help="Enter your full legal name")
        client_id = st.text_input("Client ID", key="signup_client_id",
                                  help="Your unique client identification number")
        username = st.text_input("Username", key="signup_username",
                                 help="Choose a unique username")
        password = st.text_input("Password", type="password", key="signup_password",
                                 help="Create a strong password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            signup_btn = st.button("Sign Up")
        
        with col2:
            login_return_btn = st.button("Back to Login")
        
        if signup_btn:
            if name and client_id and username and password:
                # Attempt to save credentials
                if self.save_credentials(name, client_id, username, password):
                    st.success("Account Created Successfully!")
                    # Redirect to login page
                    st.session_state['page'] = 'login'
                    st.rerun()
                else:
                    st.error("Username already exists. Please choose another.")
            else:
                st.error("Please fill in all fields")
        
        if login_return_btn:
            st.session_state['page'] = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def get_user_upload_dir(self, username):
        """Create and return a user-specific upload directory"""
        user_dir = os.path.join(self.upload_dir, username)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir
    
    def extract_table_pdfplumber(self, pdf_path, password=None):
        """Extract tables from PDF using pdfplumber"""
        all_data = []
        column_names = None
        
        try:
            # Open PDF with password if provided
            with pdfplumber.open(pdf_path, password=password) as pdf:
                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    extracted_table = page.extract_table()
                    
                    if extracted_table:
                        # For the first table with data, get column names
                        if column_names is None and len(extracted_table) > 0:
                            column_names = extracted_table[0]
                            # Add data rows from first table (skip header row)
                            all_data.extend(extracted_table[1:])
                        else:
                            # Check if subsequent tables have the same column structure
                            if len(extracted_table) > 0:
                                if extracted_table[0] == column_names:
                                    # Same structure, skip header
                                    all_data.extend(extracted_table[1:])
                                else:
                                    # Different header structure, try to map columns or add as is
                                    all_data.extend(extracted_table)
                                    
                        st.write(f"Processed page {page_num}: Found {len(extracted_table)} rows")

            # Create DataFrame from collected data
            if all_data and column_names:
                # Create DataFrame with consistent column names
                all_data = [row[:5] + row[6:] if len(row) > 5 else row for row in all_data]
                df = pd.DataFrame(all_data, columns=column_names)
                
                # Clean data - convert numeric columns
                for col in df.columns:
                    # Try to convert to numeric if possible
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except:
                        pass  # Keep as is if conversion fails
                
                # Drop NaN rows that don't contain essential information
                if 'Particulars' in df.columns:
                    df = df.dropna(subset=['Particulars'])
                if 'Balance' in df.columns:
                    df = df.dropna(subset(['Balance']))
                
                # Store only the DataFrame directly in session state
                st.session_state['extracted_df'] = df
                st.session_state['current_pdf'] = pdf_path
                
                # Generate basic transaction summary
                result = self.generate_transaction_summary(df)
                st.session_state['transaction_summary'] = result
                
                return df
            else:
                return None
                
        except Exception as e:
            st.error(f"Error extracting tables: {e}")
            return None

    def generate_transaction_summary(self, df):
        """Generate a summary of transactions"""
        try:
            # Create a copy of the DataFrame to avoid modifying the original
            summary_df = df.copy()
            
            # Handle withdrawals and deposits if they exist
            if 'Withdrawl' in summary_df.columns and 'Deposit' in summary_df.columns:
                # Convert to numeric if they aren't already
                summary_df['Withdrawl'] = pd.to_numeric(summary_df['Withdrawl'], errors='coerce').fillna(0)
                summary_df['Deposit'] = pd.to_numeric(summary_df['Deposit'], errors='coerce').fillna(0)
                
                # Generate summary text
                summary_text = "Transaction Summary:\n\n"
                
                # Calculate totals
                total_expense = summary_df['Withdrawl'].sum()
                total_income = summary_df['Deposit'].sum()
                net_flow = total_income - total_expense
                
                summary_text += f"Total Expense: ₹{total_expense:.2f}"
                summary_text += f"\nTotal Income: ₹{total_income:.2f}"
                summary_text += f"\nNet Cash Flow: ₹{net_flow:.2f} ({'Positive' if net_flow >= 0 else 'Negative'})"
                
                return summary_text
            else:
                # If no withdrawals/deposits columns
                summary_text = f"Found {len(df)} transactions in the statement."
                return summary_text
                
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def save_pdf_metadata(self, username, filename, original_filename):
        """Save metadata about uploaded PDF files"""
        try:
            # Read existing metadata
            with open(self.pdf_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Add new file metadata
            file_id = str(uuid.uuid4())
            metadata[file_id] = {
                'username': username,
                'filename': filename,
                'original_filename': original_filename,
                'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'file_size': os.path.getsize(filename)
            }
            
            # Write updated metadata
            with open(self.pdf_metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            return file_id
        except Exception as e:
            st.error(f"Error saving file metadata: {str(e)}")
            return None
    
    def file_upload_page(self):
        """Render PDF file upload page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">PDF Upload</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:var(--text-secondary);">Upload your PDF files securely</p>', unsafe_allow_html=True)
        
        # Retrieve current username from session state
        current_username = st.session_state.get('current_username', 'Unknown User')
        st.write(f"Welcome, {current_username}")
        
        # File upload section
        uploaded_file = st.file_uploader(
            "Choose a PDF file", 
            type=['pdf'],
            help="Select a PDF file to upload"
        )
        
        # Optional password for protected PDFs
        pdf_password = st.text_input(
            "PDF Password (if protected)", 
            type="password",
            help="Leave blank if the PDF is not password-protected"
        )
        
        # File tags or categories
        file_tags = st.text_input(
            "Tags (comma separated)",
            help="Add tags to help organize your files"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            upload_btn = st.button("Upload PDF")
        
        with col2:
            view_files_btn = st.button("View My Files")
        
        logout_btn = st.button("Logout")
        
        if upload_btn and uploaded_file is not None:
            try:
                # Validate file extension
                if not uploaded_file.name.lower().endswith('.pdf'):
                    st.error("Only PDF files are allowed!")
                    return
                
                # Get user-specific directory
                user_dir = self.get_user_upload_dir(current_username)
                
                # Generate a unique filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = uploaded_file.name.replace(' ', '_')
                unique_filename = os.path.join(
                    user_dir, 
                    f"{timestamp}_{safe_filename}"
                )
                
                # Save the uploaded file
                with open(unique_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Save metadata including any tags
                tags = [tag.strip() for tag in file_tags.split(',')] if file_tags else []
                file_id = self.save_pdf_metadata(
                    current_username,
                    unique_filename,
                    uploaded_file.name,
                )
                
                if file_id:
                    st.success(f"PDF '{uploaded_file.name}' uploaded successfully!")
                    st.info(f"File ID: {file_id}")
                    
                    # Process the PDF to extract tables
                    with st.spinner("Extracting data from PDF..."):
                        password = pdf_password if pdf_password else None
                        df = self.extract_table_pdfplumber(unique_filename, password)
                        
                        if df is not None:
                            # Store the DataFrame in session state
                            st.session_state['extracted_df'] = df
                            st.session_state['current_pdf'] = unique_filename
                            st.session_state['page'] = 'view_dataframe'
                            st.success("Data extracted successfully! View the data table.")
                            st.rerun()
                        else:
                            st.warning("No tables found in the PDF or extraction failed.")
                else:
                    st.warning("File uploaded but metadata could not be saved.")
            except Exception as e:
                st.error(f"Error uploading PDF: {str(e)}")
        
        if view_files_btn:
            st.session_state['page'] = 'view_files'
            st.rerun()
        
        if logout_btn:
            # Clear login-related session state
            if 'current_username' in st.session_state:
                del st.session_state['current_username']
            st.session_state['page'] = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def view_dataframe_page(self):
        """Display the extracted DataFrame from PDF"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Extracted Data</h2>', unsafe_allow_html=True)
        
        # Get the DataFrame from session state
        df = st.session_state.get('extracted_df', None)
        current_pdf = st.session_state.get('current_pdf', 'Unknown PDF')
        transaction_summary = st.session_state.get('transaction_summary', None)
        
        if df is not None:
            # Show PDF file name
            st.write(f"Data from: {os.path.basename(current_pdf)}")
            
            # Display DataFrame statistics
            st.write(f"Found {len(df)} rows and {len(df.columns)} columns")
            
            # Display tabs for data view and analysis
            tab1, tab2 = st.tabs(["Data", "Transaction Analysis"])
            
            with tab1:
                # Add search/filter capability
                search_term = st.text_input("Search in data", "")
                
                # Filter DataFrame if search term is provided
                filtered_df = df
                if search_term:
                    filtered_df = df[df.astype(str).apply(
                        lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
                    st.write(f"Found {len(filtered_df)} matching rows")
                
                # Display the DataFrame
                st.dataframe(filtered_df)
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    # Download as CSV
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download as CSV",
                        data=csv,
                        file_name=f"extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Download as Excel - Fixed implementation using BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        filtered_df.to_excel(writer, index=False)
                    output.seek(0)  # Go to the beginning of the BytesIO buffer
                    
                    st.download_button(
                        label="Download as Excel",
                        data=output,
                        file_name=f"extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with tab2:
                # Show transaction summary
                if transaction_summary:
                    st.subheader("Transaction Summary")
                    st.text(transaction_summary)
                
                # If we have withdrawal/deposit data, show transaction trends
                if 'Withdrawl' in df.columns and 'Date' in df.columns:
                    try:
                        st.subheader("Transaction Trends")
                        # Convert date column to datetime if it's not already
                        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                        # Group by date and sum withdrawals and deposits
                        date_summary = df.groupby(df['Date'].dt.date).agg({
                            'Withdrawl': 'sum',
                            'Deposit': 'sum'
                        }).reset_index()
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(date_summary['Date'], date_summary['Withdrawl'], label='Withdrawals')
                        ax.plot(date_summary['Date'], date_summary['Deposit'], label='Deposits')
                        plt.legend()
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(fig)
                    except Exception as e:
                        st.warning(f"Could not create transaction trend chart: {e}")
                else:
                    st.info("Date or transaction amount information not available. Unable to show trends.")
            
        else:
            st.error("No data available. Please upload a PDF first.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            back_btn = st.button("Back to Upload")
        
        with col2:
            logout_btn = st.button("Logout")
        
        with col3:
            # Add new button for financial advice
            advice_btn = st.button("Get Financial Advice")
        
        if back_btn:
            st.session_state['page'] = 'file_upload'
            st.rerun()
        
        if logout_btn:
            if 'current_username' in st.session_state:
                del st.session_state['current_username']
            st.session_state['page'] = 'login'
            st.rerun()
            
        if advice_btn and df is not None:
            st.session_state['page'] = 'financial_advice'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def financial_advice_page(self):
        """Display financial advice based on transaction data using Gemini AI"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Financial Insights</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:var(--text-secondary);">AI-powered financial analysis</p>', unsafe_allow_html=True)
        
        # Get the DataFrame from session state
        df = st.session_state.get('extracted_df', None)
        transaction_summary = st.session_state.get('transaction_summary', None)
        
        if df is None:
            st.error("No transaction data available. Please upload a PDF first.")
            back_btn = st.button("Back to Upload")
            if back_btn:
                st.session_state['page'] = 'file_upload'
                st.rerun()
            return
        
        # Check if Gemini API key is available
        if not GOOGLE_API_KEY:
            st.error("Gemini API key not found in your .env file.")
            st.info("""
            To use the financial advice feature:
            
            1. Create a .env file in the application root directory
            2. Add the following line to your .env file:
               GOOGLE_API_KEY=your_api_key_here
            3. Get an API key from [Google AI Studio](https://makersuite.google.com/)
            4. Restart the application after adding your API key
            """)
            back_btn = st.button("Back")
            if back_btn:
                st.session_state['page'] = 'view_dataframe'
                st.rerun()
            return
        
        # Prepare transaction data for Gemini
        try:
            # Create a summary of the data for the AI
            summary_text = "Transaction data summary:\n\n"
            
            # Add transaction summary if available
            if transaction_summary:
                summary_text += transaction_summary + "\n\n"
            
            # Add column information
            summary_text += f"Data columns: {', '.join(df.columns.tolist())}\n\n"
            
            # Add sample data (first 5 rows)
            summary_text += "Sample transaction data:\n"
            summary_text += df.head(5).to_string() + "\n\n"
            
            # Add current date for real-time context
            current_date = datetime.now().strftime("%Y-%m-%d")
            summary_text += f"Current date: {current_date}\n"
            
            # Show loading spinner while generating advice
            with st.spinner("Analyzing your financial data..."):
                # Set up Gemini model (using Gemini 1.5 Flash for faster response)
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Generate different types of financial insights
                    insights_prompt = f"""
                    Based on the financial transaction data below, please provide the following insights:
                    
                    1. Spending Patterns: Identify major spending categories and patterns
                    2. Budget Recommendations: Suggest budget improvements based on spending habits
                    3. Saving Opportunities: Highlight areas where the person could save money
                    4. Financial Health Summary: Overall assessment of financial health based on the data
                    
                    Please keep your analysis professional, factual, and helpful. Do not make assumptions beyond what's in the data.
                    
                    {summary_text}
                    """
                    
                    response = model.generate_content(insights_prompt)
                    financial_advice = response.text
                    
                    # Store the advice in session state
                    st.session_state['financial_advice'] = financial_advice
                    
                except Exception as e:
                    st.error(f"Error generating financial insights: {str(e)}")
                    financial_advice = "Unable to generate financial insights at this time."
                    st.session_state['financial_advice'] = financial_advice
            
            # Display the financial advice
            st.subheader("Your Financial Insights")
            st.markdown(financial_advice)
            
            # Option to ask follow-up questions
            st.subheader("Have questions about your finances?")
            user_question = st.text_input("Ask a question about your financial data:")
            
            if user_question:
                with st.spinner("Generating response..."):
                    try:
                        followup_prompt = f"""
                        Based on the financial transaction data summary below and the user's question, 
                        please provide a helpful response. Focus only on the financial aspects and what 
                        can be inferred from the data.
                        
                        Financial data summary: {summary_text}
                        
                        Previous financial insights: {financial_advice}
                        
                        User question: {user_question}
                        """
                        
                        response = model.generate_content(followup_prompt)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
            
        except Exception as e:
            st.error(f"Error analyzing transaction data: {str(e)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            back_btn = st.button("Back to Data View")
        
        with col2:
            logout_btn = st.button("Logout")
        
        if back_btn:
            st.session_state['page'] = 'view_dataframe'
            st.rerun()
        
        if logout_btn:
            if 'current_username' in st.session_state:
                del st.session_state['current_username']
            st.session_state['page'] = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def view_files_page(self):
        """Render page to view uploaded PDF files"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Your Files</h2>', unsafe_allow_html=True)
        
        # Retrieve current username from session state
        current_username = st.session_state.get('current_username', 'Unknown User')
        
        try:
            # Load metadata
            with open(self.pdf_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Filter for current user's files
            user_files = {k: v for k, v in metadata.items() if v['username'] == current_username}
            
            if not user_files:
                st.info("You haven't uploaded any files yet.")
            else:
                st.write(f"You have {len(user_files)} file(s) uploaded:")
                
                # Display files in a nice format
                for file_id, file_data in user_files.items():
                    with st.expander(f"{file_data['original_filename']} ({file_data['upload_date']})"):
                        st.write(f"Upload date: {file_data['upload_date']}")
                        st.write(f"File size: {file_data['file_size']/1024:.2f} KB")
                        
                        # Option to download the file
                        if os.path.exists(file_data['filename']):
                            with open(file_data['filename'], "rb") as f:
                                st.download_button(
                                    label="Download PDF",
                                    data=f,
                                    file_name=file_data['original_filename'],
                                    mime="application/pdf"
                                )
        except Exception as e:
            st.error(f"Error loading your files: {str(e)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            back_btn = st.button("Back to Upload")
        
        with col2:
            logout_btn = st.button("Logout")
        
        if back_btn:
            st.session_state['page'] = 'file_upload'
            st.rerun()
        
        if logout_btn:
            if 'current_username' in st.session_state:
                del st.session_state['current_username']
            st.session_state['page'] = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        # Render the appropriate page based on session state
        page = st.session_state.get('page', 'login')
        
        if page == 'login':
            self.login_page()
        elif page == 'signup':
            self.signup_page()
        elif page == 'file_upload':
            self.file_upload_page()
        elif page == 'view_files':
            self.view_files_page()
        elif page == 'view_dataframe':
            self.view_dataframe_page()
        elif page == 'financial_advice':
            self.financial_advice_page()

def main():
    app = MobileAuthApp()
    app.run()

if __name__ == "__main__":
    main()
