import streamlit as st
import pandas as pd
from pypdf import PdfReader
from openai import OpenAI

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="GenAI Loan Risk Assessment", layout="wide")

st.title("🏦 GenAI Loan Risk Assessment Assistant")
st.caption("ITI122 – Loan Risk Assessment with Generative AI")

st.markdown("---")
st.caption("Jun Ren · Adam · Shao Xian")



# ===============================
# OPENAI CLIENT
# ===============================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ===============================
# SIMULATED DATABASE TABLES
# ===============================
credit_score_df = pd.DataFrame([
    {"ID": 1111, "Name": "Loren", "Email": "loren@gmail.com", "Credit Score": 455},
    {"ID": 2222, "Name": "Matt", "Email": "matt@yahoo.com", "Credit Score": 685},
    {"ID": 3333, "Name": "Hilda", "Email": "halida@gmail.com", "Credit Score": 825},
    {"ID": 4444, "Name": "Andy", "Email": "andy@gmail.com", "Credit Score": 840},
    {"ID": 5555, "Name": "Kit", "Email": "kit@yahoo.com", "Credit Score": 350},
])

account_status_df = pd.DataFrame([
    {"ID": 1111, "Nationality": "Singaporean", "Account Status": "good-standing"},
    {"ID": 2222, "Nationality": "Non-Singaporean", "Account Status": "closed"},
    {"ID": 3333, "Nationality": "Singaporean", "Account Status": "delinquent"},
    {"ID": 4444, "Nationality": "Non-Singaporean", "Account Status": "good-standing"},
    {"ID": 5555, "Nationality": "Singaporean", "Account Status": "delinquent"},
])

pr_status_df = pd.DataFrame([
    {"ID": 2222, "PR Status": True},
    {"ID": 4444, "PR Status": False},
])

# ===============================
# PDF LOADER
# ===============================
def load_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

risk_policy_text = load_pdf_text("Bank Loan Overall Risk Policy.pdf")
interest_policy_text = load_pdf_text("Bank Loan Interest Rate Policy.pdf")

# ===============================
# UI INPUT
# ===============================
customer_id = st.selectbox(
    "Select Customer ID",
    credit_score_df["ID"].tolist()
)

if st.button("Assess Loan Risk"):
    # ===============================
    # DATA RETRIEVAL
    # ===============================
    credit_row = credit_score_df[credit_score_df["ID"] == customer_id].iloc[0]
    account_row = account_status_df[account_status_df["ID"] == customer_id].iloc[0]

    pr_row = pr_status_df[pr_status_df["ID"] == customer_id]
    pr_status = pr_row.iloc[0]["PR Status"] if not pr_row.empty else "N/A"

    # ===============================
    # STEP 1 & 2 (SYSTEM GENERATED)
    # ===============================
    st.subheader("📋 Loan Assessment Walkthrough")

    step_text = f"""Customer Information:
Name: {credit_row['Name']}
ID: {credit_row['ID']}
Email: {credit_row['Email']}

Step 1. Retrieve information for customer information
Credit Score: {credit_row['Credit Score']}, Account Status: {account_row['Account Status']}, Nationality: {account_row['Nationality']}
"""

    if account_row["Nationality"] == "Non-Singaporean":
        step_text += f"""
Step 2. Check PR Status (For Non-Singapore this extra Step is needed)
PR Status -> {pr_status}
"""

    st.code(step_text, language="text")

    # ===============================
    # GENAI PROMPT (STEP 3–5 ONLY)
    # ===============================
    prompt = f"""
You are a bank loan officer.
Follow the official workflow and continue from Step 3 onward.

Bank Loan Overall Risk Policy:
{risk_policy_text}

Bank Loan Interest Rate Policy:
{interest_policy_text}

Customer Details:
Credit Score: {credit_row['Credit Score']}
Account Status: {account_row['Account Status']}
Nationality: {account_row['Nationality']}
PR Status: {pr_status}

Continue in this EXACT format:

Step 3. Check Overall Risk
Credit Score: <value>, Account Status: <value> -> overall risk: <low/medium/high>

Step 4. Check interest rate
overall risk: <risk> -> <interest rate>

Step 5. Report
<Final recommendation sentence>

Rules:
- Use lowercase for risk
- Use arrows (->) exactly
- If Non-Singaporean and PR is false, do NOT recommend
- Keep wording concise
"""

    # ===============================
    # OPENAI CALL
    # ===============================
    with st.spinner("GenAI is assessing the loan risk..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

    # ===============================
    # OUTPUT (STEP 3–5)
    # ===============================
    st.code(response.choices[0].message.content, language="text")


