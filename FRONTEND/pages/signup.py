import streamlit as st
import sqlite3
import hashlib

# Hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to add a new user
def add_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        st.success(f"Account created for {username}!")
    except sqlite3.IntegrityError:
        st.error("Username already exists!")
    
    conn.close()

st.title("📝 Sign Up Page")

new_username = st.text_input("Choose a UserId")
new_password = st.text_input("Create a Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

if st.button("Sign Up"):
    if new_password != confirm_password:
        st.error("Passwords do not match")
    elif len(new_password) < 6:
        st.error("Password must be at least 6 characters long")
    else:
        add_user(new_username, new_password)

st.markdown("""
    <div class='cta-button'>
        <a href='/login' target='_self'>Already have an account?? Login...</a>
    </div>
""", unsafe_allow_html=True)
