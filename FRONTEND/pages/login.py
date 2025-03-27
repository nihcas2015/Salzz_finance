
'''import streamlit as st
import sqlite3
import hashlib

# Hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to authenticate user
def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    conn.close()

    if result and result[0] == hash_password(password):
        return True
    return False

st.title("🔑 Login Page")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if authenticate_user(username, password):
        st.success("Login successful")
        st.markdown("""<div class='cta-button'><a href='/transaction' target='_self'>Transaction</a></div> """, unsafe_allow_html=True)
   '''     
import streamlit as st
import sqlite3
import hashlib

# ✅ Hashing function
def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Function to authenticate user
def authenticate_user(username, password):
    """Check user credentials from SQLite database"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    conn.close()

    # Compare stored hash with entered password hash
    return result and result[0] == hash_password(password)

# ✅ Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ✅ Streamlit UI
st.title("🔑 Login Page")

# ✅ If not authenticated, show the login form
if not st.session_state.authenticated:
    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")

    # ✅ Login button with unique key
    if st.button("Login", key="login_button"):
        if authenticate_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("✅ Login successful!")

            # ✅ Redirect to the transaction page
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# ✅ If authenticated, show success message and navigation buttons
else:
    st.success(f"✅ Welcome back, {st.session_state.username}!")

    col1, col2 = st.columns(2)

    # ✅ Navigation buttons with unique keys
    with col1:
        if st.button("Go to Transaction", key="transaction_button"):
            st.switch_page("pages/transaction.py")

    with col2:
        if st.button("Go to Financial Info", key="financial_button"):
            st.switch_page("pages/debtmodel.py")

    # ✅ Logout button
    if st.button("Logout", key="logout_button"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.warning("⚠️ You have been logged out.")
        st.rerun()
