import streamlit as st
import pickle
import numpy as np

# Load the saved KMeans model and Scaler
with open("kmeans_model (4).pkl", "rb") as model_file:
    kmeans = pickle.load(model_file)

with open("scaler.pkl", "rb") as scaler_file:
    scaler = pickle.load(scaler_file)

# Set Page Layout
st.set_page_config(page_title="Financial Clustering & Insights", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px 24px;
        transition: 0.3s;
        border: none;
    }
    .stButton > button:hover {
        background-color: #005f7f;
        transform: scale(1.07);
    }
    .title {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
    }
    .sub-title {
        font-size: 24px;
        font-weight: bold;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit UI
st.markdown('<p class="title">📊 Customer Clustering Prediction</p>', unsafe_allow_html=True)

# Columns for better layout
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("🎂 Enter your Age", min_value=18, max_value=100, step=1)
    income = st.number_input("💰 Enter your Income", min_value=1000, step=100)

with col2:
    debt = st.number_input("💳 Enter your Debt", min_value=1, step=100)
    credit_score = st.number_input("📈 Enter your Credit Score", min_value=300, max_value=850, step=10)

dti_ratio = (debt / income)

# Ensure 'cluster' exists in session state
if "cluster" not in st.session_state:
    st.session_state.cluster = None

# Predict Cluster
if st.button("🔍 Find My Cluster", key="cluster_btn"):
    user_data = np.array([[age, income, debt, credit_score, dti_ratio]])
    scaled_data = scaler.transform(user_data)
    st.session_state.cluster = kmeans.predict(scaled_data)[0]
    st.success(f"✅ You belong to Cluster: *{st.session_state.cluster}*")

# Cluster Descriptions
cluster_descriptions = {
    0: "🔹 *High-Income, High Debt\nYou have strong earnings but high debt. Focus on **debt consolidation* and strategic *investment planning*.",
    1: "📊 *Mid-Income, Moderate Debt\nYou have financial stability. Consider **long-term investments* like mutual funds.",
    2: "🛡 *Retirees / Low Debt Holders\nFinancially stable. Prioritize **low-risk investments* and estate planning.",
    3: "⚠ *Mid-Income, High Debt, Lower Credit\nPrioritize **debt repayment strategies* to improve your financial standing."
}

# Show Cluster Insights
if st.session_state.cluster is not None:
    st.info(cluster_descriptions.get(st.session_state.cluster, "❓ Cluster not found."))

# Investment Recommendations
investment_recommendations = {
    0: "🏠 *Real Estate Investment*\n\n💡 Contact our fintech company for expert guidance.",
    1: "📈 *Stock Market & ETFs*\n\n💡 Learn about the best funds and market trends with us.",
    2: "💰 *Fixed Deposits & Bonds*\n\n💡 Secure your savings with low-risk financial products.",
    3: "⚠ *Debt Repayment & Emergency Fund*\n\n💡 Talk to us about financial restructuring and savings."
}

# Columns for button alignment
col3, col4 = st.columns([1, 1])

with col3:
    if st.button("💰 Best Investment Strategy", key="investment_btn"):
        if st.session_state.cluster is not None:
            st.success(investment_recommendations.get(st.session_state.cluster, "⚠ Cluster not found."))
        else:
            st.warning("⚠ Please find your cluster first.")

# --- Debt Repayment Section ---
st.markdown('<p class="sub-title">💳 Debt Repayment Calculator</p>', unsafe_allow_html=True)

# Columns for better alignment
col5, col6 = st.columns(2)

with col5:
    retirement_age = st.number_input("🎯 Enter Your Expected Retirement Age", min_value=50, max_value=70, step=1)

# Debt repayment function
def calculate_yearly_repayment(debt, income, interest_rate, years_left):
    if years_left <= 0:
        return "⚠ Retirement age must be greater than current age!"
    
    r = interest_rate / 100
    n = years_left
    A = (debt * r * (1 + r)*n) / ((1 + r)*n - 1)

    # Ensure yearly payment does not exceed 40% of income
    max_allowed_payment = 0.4 * income
    return min(A, max_allowed_payment)

# Interest rates based on cluster risk level
interest_rates = {0: 6.5, 1: 8.0, 2: 5.5, 3: 10.5}

# Debt repayment strategies
debt_repayment_strategies = {
    0: "🔹 *Smart Balance:* Use extra income to clear high-interest debt while investing.",
    1: "📊 *Structured Plan:* Focus on long-term stability by clearing debt gradually.",
    2: "🛡 *Low-Risk Approach:* Preserve cash flow and make steady repayments.",
    3: "⚠ *Emergency Mode:* Prioritize high-interest debts to avoid financial stress."
}

# Calculate and display debt repayment
if st.session_state.cluster is not None:
    years_left = retirement_age - age

    with col6:
        if st.button("💳 Calculate My Yearly Debt Repayment", key="debt_btn"):
            interest_rate = interest_rates.get(st.session_state.cluster, 8.0)
            yearly_payment = calculate_yearly_repayment(debt, income, interest_rate, years_left)

            if isinstance(yearly_payment, str):
                st.error(yearly_payment)
            else:
                st.success(f"📅 You should aim to pay *${yearly_payment:,.2f} per year*.")
                st.success("💡 Contact our fintech company for expert financial assistance.")
                st.info(debt_repayment_strategies.get(st.session_state.cluster, "No strategy found."))

else:
    st.warning("⚠ Please find your cluster first before calculating debt repayment.")