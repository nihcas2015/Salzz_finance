import streamlit as st

# ✅ Ensure the user is authenticated
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("⚠️ Please log in first.")
    st.stop()

# ✅ Display the Debt Model content if authenticated
st.title("📊 Debt Model")
st.write("You are now viewing the Debt Model page.")

# 🔹 Collect user input for financial model
st.subheader("💰 Financial Information")

# ✅ Collect yearly income, total debt, and credit score
yearly_income = st.number_input("Yearly Income Rs", min_value=0.0, step=1000.0)
total_debt = st.number_input("Total Debt Rs", min_value=0.0, step=1000.0)
credit_score = st.number_input("Credit Score", min_value=300, max_value=850, step=10)

# ✅ Calculate debt-to-income (DTI) ratio
if yearly_income > 0:
    dti_ratio = (total_debt / yearly_income) * 100
    st.write(f"📊 Your Debt-to-Income Ratio: **{dti_ratio:.2f}%**")

    # ✅ Provide financial guidance based on DTI ratio
    if dti_ratio < 20:
        st.success("✅ Your DTI ratio is healthy. You have a low debt burden.")
    elif 20 <= dti_ratio < 35:
        st.warning("⚠️ Your DTI ratio is moderate. Be cautious with new loans.")
    else:
        st.error("❌ Your DTI ratio is high. Consider reducing your debt.")

    # ✅ Provide feedback based on credit score
    if credit_score >= 750:
        st.success("🌟 Excellent credit score! You qualify for the best rates.")
    elif 700 <= credit_score < 750:
        st.success("👍 Good credit score! You have access to favorable rates.")
    elif 650 <= credit_score < 700:
        st.warning("⚠️ Fair credit score. You may face slightly higher rates.")
    else:
        st.error("❌ Poor credit score. Work on improving your credit health.")
else:
    st.error("⚠️ Please enter a valid yearly income greater than 0.")

# ✅ Button to log out
if st.button("Logout", key="logout_button"):
    st.session_state.authenticated = False
    st.warning("⚠️ You have been logged out.")
    st.switch_page("pages/login.py")  # Redirect back to the login page
