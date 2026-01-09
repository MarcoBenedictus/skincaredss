import streamlit as st
import pandas as pd
import numpy as np

############################### PAGE CONFIG & CSS ##############################

st.set_page_config(page_title="Skincare DSS", layout="centered")

# load external CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("style.css")
except FileNotFoundError:
    st.error("style.css not found.")

############################## HEADER ##############################

st.markdown("""
    <div class="pink-header">
        <h1> Skincare DSS </h1>
        <p>Decision Support System based on the Baumann Skin Type & TOPSIS</p>
    </div>
    """, unsafe_allow_html=True)

############################## DATA LOADING & PREPROCESSING ##############################

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cosmetic_p.csv')
    except FileNotFoundError:
        return None

    # Precalculate C5 based on Ingredient List Length
    def calculate_safety(ingredients):
        if not isinstance(ingredients, str): return 1
        count = len(ingredients.split(','))
        if count < 10: return 5
        elif count < 20: return 4
        elif count < 30: return 3
        elif count < 40: return 2
        else: return 1

    df['C5_Safety'] = df['ingredients'].apply(calculate_safety)
    return df

df = load_data()

if df is None:
    st.error("cosmetic_p.csv not found.")
    st.stop()


############################## BAUMANN QUESTIONNAIRE ##############################

st.markdown("### 📝 Determine Your Skin Type")
st.write("Please answer the following questions to calculate your Baumann Skin Type (C2 & C3 Criteria).")

col_q1, col_q2 = st.columns(2)

with col_q1:
    st.markdown("#### Oiliness (O/D)")
    q1 = st.radio("1. Does your skin feel sticky or oily, especially at noon?", ("Yes (Oily)", "No (Dry)"), key="q1")
    
    st.markdown("#### Pigmentation (P/N)")
    q3 = st.radio("3. Do you have acne marks, dark spots, or uneven tone?", ("Yes (Pigmented)", "No (Non-Pigmented)"), key="q3")

with col_q2:
    st.markdown("#### Sensitivity (S/R)")
    q2 = st.radio("2. Is your skin itchy or red when changing skincare routines?", ("Yes (Sensitive)", "No (Resistant)"), key="q2")
    
    st.markdown("#### Aging (W/T)")
    q4 = st.radio("4. Are you concerned about fine lines or wrinkles?", ("Yes (Wrinkled)", "No (Tight)"), key="q4")

# Process Inputs
user_oily = True if "Yes" in q1 else False
user_sensitive = True if "Yes" in q2 else False
user_pigmented = True if "Yes" in q3 else False
user_wrinkled = True if "Yes" in q4 else False

# Determine Baumann skin Code
skin_type_code = ""
skin_type_code += "O" if user_oily else "D"
skin_type_code += "S" if user_sensitive else "R"
skin_type_code += "P" if user_pigmented else "N"
skin_type_code += "W" if user_wrinkled else "T"

st.success(f"**Detected Skin Type: {skin_type_code}**")
st.markdown("---")

############################## WEIGHTING CRITERIA SELECTION ##############################

st.markdown("### ⚙️ Set Your Priorities")
st.write("Adjust the sliders based on what is most important to you.")

col_w1, col_w2, col_w3 = st.columns(3)

with col_w1:
    w_c1 = st.slider("C1: Importance of Price ( Higher = Cheaper )", 1, 5, 1) # min max default
with col_w2:
    w_c4 = st.slider("C4: Importance of User Ratings ( Higher = Better )", 1, 5, 1)
with col_w3:
    w_c5 = st.slider("C5: Importance of Safety ( Higher = Safer )", 1, 5, 1)

w_c2 = 4 
w_c3 = 3

st.markdown("---")

############################## TOPSIS CALCULATION & RECOMMENDATIONS ##############################
# read README for more keywords and the risk.
brightening_keywords = ['niacinamide', 'vitamin c', 'ascorbic', 'arbutin', 'licorice', 'kojic', 'azelaic', 'retinol', 'glycolic', 'lactic']
anti_aging_keywords = ['retinol', 'peptide', 'hyaluronic', 'ceramide', 'collagen', 'adenosine', 'tocopherol', 'coq10', 'snail']

def calculate_c2_score(row):
    score = 1 
    if user_oily and row['Oily'] == 1: score += 2
    elif not user_oily and row['Dry'] == 1: score += 2
        
    if user_sensitive and row['Sensitive'] == 1: score += 2
    elif not user_sensitive: score += 2
        
    return min(score, 5)

def calculate_c3_score(row):
    ingredients = str(row['ingredients']).lower()
    matches = 0
    
    if user_pigmented:
        for k in brightening_keywords:
            if k in ingredients: matches += 1
                
    if user_wrinkled:
        for k in anti_aging_keywords:
            if k in ingredients: matches += 1
    
    score = 1 + matches
    return min(score, 5)

if st.button("🚀 Calculate Recommendations", type="primary"):
    
    # Calculate Scores
    df['C2_Suitability'] = df.apply(calculate_c2_score, axis=1)
    df['C3_Effectiveness'] = df.apply(calculate_c3_score, axis=1)
    
    data = df[df['price'] > 0].copy()

    # TOPSIS Math
    denom_c1 = np.sqrt((data['price']**2).sum())
    denom_c2 = np.sqrt((data['C2_Suitability']**2).sum())
    denom_c3 = np.sqrt((data['C3_Effectiveness']**2).sum())
    denom_c4 = np.sqrt((data['rank']**2).sum())
    denom_c5 = np.sqrt((data['C5_Safety']**2).sum())

    data['n_C1'] = data['price'] / denom_c1
    data['n_C2'] = data['C2_Suitability'] / denom_c2
    data['n_C3'] = data['C3_Effectiveness'] / denom_c3
    data['n_C4'] = data['rank'] / denom_c4
    data['n_C5'] = data['C5_Safety'] / denom_c5

    data['w_C1'] = data['n_C1'] * w_c1
    data['w_C2'] = data['n_C2'] * w_c2
    data['w_C3'] = data['n_C3'] * w_c3
    data['w_C4'] = data['n_C4'] * w_c4
    data['w_C5'] = data['n_C5'] * w_c5

    ideal_best = {
        'C1': data['w_C1'].min(),
        'C2': data['w_C2'].max(),
        'C3': data['w_C3'].max(),
        'C4': data['w_C4'].max(),
        'C5': data['w_C5'].max()
    }

    ideal_worst = {
        'C1': data['w_C1'].max(),
        'C2': data['w_C2'].min(),
        'C3': data['w_C3'].min(),
        'C4': data['w_C4'].min(),
        'C5': data['w_C5'].min()
    }

    data['D_plus'] = np.sqrt(
        (data['w_C1'] - ideal_best['C1'])**2 +
        (data['w_C2'] - ideal_best['C2'])**2 +
        (data['w_C3'] - ideal_best['C3'])**2 +
        (data['w_C4'] - ideal_best['C4'])**2 +
        (data['w_C5'] - ideal_best['C5'])**2
    )

    data['D_minus'] = np.sqrt(
        (data['w_C1'] - ideal_worst['C1'])**2 +
        (data['w_C2'] - ideal_worst['C2'])**2 +
        (data['w_C3'] - ideal_worst['C3'])**2 +
        (data['w_C4'] - ideal_worst['C4'])**2 +
        (data['w_C5'] - ideal_worst['C5'])**2
    )

    data['TOPSIS_Score'] = data['D_minus'] / (data['D_plus'] + data['D_minus'])

    # Results
    st.markdown(f"### 🏆 Top 10 Recommendations for {skin_type_code}")
    top_products = data.sort_values(by='TOPSIS_Score', ascending=False).head(10)

    for i, (index, row) in enumerate(top_products.iterrows()):
        # RENDER THE CARD WITHOUT THE INGREDIENTS
        st.markdown(f"""
        <div class="product-card">
            <h3>#{i+1} {row['brand']} - {row['name']}</h3>
            <p style="margin: 5px 0 10px 0; font-weight: bold;">TOPSIS Score: {row['TOPSIS_Score']:.4f}</p>
            <div class="product-card-stats">
                <span>💰 Price: ${row['price']}</span>
                <span>⭐ User Rating: {row['rank']}</span>
                <span>🛡️ Safety: {row['C5_Safety']}/5</span>
            </div>
             <div class="product-card-scores">
                <span>Skin Match: {row['C2_Suitability']}/5</span>
                <span>Ingredient Match: {row['C3_Effectiveness']}/5</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # native streamlit expander for ingredsients
        with st.expander("Show Ingredients"):
            st.write(row['ingredients'])

st.markdown("---")
with st.expander("📂 View Full Dataset (All Products)"):
    st.write("This table shows the raw data used for calculations.")
    st.markdown("credits where credits' due : https://www.kaggle.com/datasets/dominoweir/skincare-product-ingredients")
    st.dataframe(df)