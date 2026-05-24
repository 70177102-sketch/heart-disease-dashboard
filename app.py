import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Heart Disease Dashboard Pro",
    layout="wide",
    page_icon="❤️"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

/* Main Background */
.main {
    background-color: #ffffff;
}

/* Title */
h1 {
    color: #000000;
    text-align: center;
    font-size: 42px;
    font-weight: bold;
}

/* Subheaders */
h2, h3 {
    color: #000000;
    font-weight: bold;
}

/* KPI CARD STYLING */
[data-testid="metric-container"] {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border: 2px solid #000000;
    text-align: center;
    box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
}

/* KPI TITLE */
[data-testid="metric-container"] label {
    color: #000000 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

/* KPI VALUE */
[data-testid="metric-container"] div {
    color: #000000 !important;
    font-size: 32px !important;
    font-weight: bold !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f3f4f6;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv("heart.csv")

# Dynamic column mapping to prevent code crashes depending on dataset schema
target_col = "target" if "target" in df.columns else df.columns[-1]
cp_col = "chest_pain_type" if "chest_pain_type" in df.columns else ("cp" if "cp" in df.columns else df.columns[2])
gender_col = "sex" if "sex" in df.columns else "gender"

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.title("⚙️ Filters")

# Age Filter
age_range = st.sidebar.slider(
    "Select Age Range",
    int(df["age"].min()),
    int(df["age"].max()),
    (int(df["age"].min()), int(df["age"].max()))
)

# Gender Filter
gender = st.sidebar.selectbox(
    "Select Gender (sex)",
    ["All"] + list(df[gender_col].unique())
)

# Apply Filters
filtered_df = df[
    (df["age"] >= age_range[0]) &
    (df["age"] <= age_range[1])
]

if gender != "All":
    filtered_df = filtered_df[filtered_df[gender_col] == gender]

# =========================================================
# TITLE
# =========================================================
st.title("❤️ Heart Disease Analytics Dashboard Pro")
st.markdown("<h3 style='text-align: center; color: #4b5563;'>Advanced Medical Data Insights</h3>", unsafe_allow_html=True)

st.divider()

# =========================================================
# KPI SECTION
# =========================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Patients", filtered_df.shape[0])

with col2:
    st.metric("Average Age", round(filtered_df["age"].mean(), 1) if not filtered_df.empty else 0)

with col3:
    st.metric("Disease Cases", int(filtered_df[target_col].sum()) if not filtered_df.empty else 0)

with col4:
    st.metric("Healthy Cases", int((filtered_df[target_col] == 0).sum()) if not filtered_df.empty else 0)

st.divider()

# =========================================================
# DATASET PREVIEW
# =========================================================
st.subheader("📌 Filtered Dataset")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# Set clean style globally for matplotlib/seaborn
sns.set_theme(style="whitegrid")

# =========================================================
# ROW 1: HEART DISEASE DISTRIBUTION & AGE DISTRIBUTION
# =========================================================
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("❤️ Heart Disease Distribution")
    
    # Create a copy to securely map text labels to prevent visualization offsets
    dist_df = filtered_df.copy()
    dist_df["Diagnosis_Label"] = dist_df[target_col].map({0: "No Disease", 1: "Disease"})
    
    fig1, ax1 = plt.subplots(figsize=(6, 4.5))
    
    # Using 'order' forces Seaborn to keep spots for both labels even if count is 0
    sns.countplot(
        x="Diagnosis_Label",
        data=dist_df,
        order=["No Disease", "Disease"],
        hue="Diagnosis_Label",
        palette={"No Disease": "#374151", "Disease": "#9ca3af"}, # Explicit color mapping 
        edgecolor="#000000",
        linewidth=1.5,
        legend=False,
        ax=ax1
    )
    
    ax1.set_title("Heart Disease Cases", fontsize=14, fontweight='bold', pad=10, color="#000000")
    ax1.set_xlabel("Diagnosis", fontsize=11, fontweight='bold', color="#000000")
    ax1.set_ylabel("Number of Patients", fontsize=11, fontweight='bold', color="#000000")
    
    # Clean setting of custom tick parameters safely
    ax1.tick_params(axis='x', labelsize=10, labelrotation=0)
    for label in ax1.get_xticklabels():
        label.set_fontweight('bold')

    # Add value annotations above bars safely
    for p in ax1.patches:
        height = p.get_height()
        if pd.notna(height) and height > 0:
            ax1.annotate(f'{int(height)}',
                        (p.get_x() + p.get_width()/2., height),
                        ha='center', va='bottom',
                        fontsize=10, fontweight='bold', color='#000000')
            
    plt.tight_layout()
    st.pyplot(fig1)

with row1_col2:
    st.subheader("📊 Age Distribution")
    
    fig2, ax2 = plt.subplots(figsize=(6, 4.5))
    if not filtered_df.empty:
        sns.histplot(
            filtered_df["age"],
            bins=12,
            kde=True,
            color="#4b5563", # Medium Charcoal
            edgecolor="#ffffff",
            linewidth=1.5,
            ax=ax2
        )
    # Style the KDE line to match monochrome theme
    if ax2.lines:
        ax2.lines[0].set_color("#000000")
        ax2.lines[0].set_linewidth(2)

    ax2.set_title("Distribution of Patient Ages", fontsize=14, fontweight='bold', pad=10, color="#000000")
    ax2.set_xlabel("Age", fontsize=11, fontweight='bold', color="#000000")
    ax2.set_ylabel("Frequency", fontsize=11, fontweight='bold', color="#000000")
    
    plt.tight_layout()
    st.pyplot(fig2)

st.divider()

# =========================================================
# ROW 2: CHEST PAIN TYPE & CORRELATION HEATMAP
# =========================================================
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("💔 Chest Pain Type Analysis")
    
    cp_df = filtered_df.copy()
    cp_map = {0: "Typical Angina", 1: "Atypical Angina", 2: "Non-Anginal", 3: "Asymptomatic"}
    if cp_col in cp_df.columns:
        cp_df[cp_col] = cp_df[cp_col].map(cp_map).fillna(cp_df[cp_col])

    fig3, ax3 = plt.subplots(figsize=(6.5, 5))
    
    if cp_col in cp_df.columns:
        sns.countplot(
            x=cp_col,
            data=cp_df,
            order=["Typical Angina", "Atypical Angina", "Non-Anginal", "Asymptomatic"],
            palette=["#1f2937", "#4b5563", "#9ca3af", "#e5e7eb"], # Distinct sequential gray palette
            edgecolor="#000000",
            linewidth=1.2,
            ax=ax3
        )
        
    ax3.set_title("Chest Pain Type Frequency", fontsize=14, fontweight='bold', pad=15, color="#000000")
    ax3.set_xlabel("Pain Type", fontsize=11, fontweight='bold', color="#000000")
    ax3.set_ylabel("Patient Count", fontsize=11, fontweight='bold', color="#000000")
    
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=15, ha='right', fontsize=9, fontweight='bold')
    ax3.grid(axis='y', linestyle='--', alpha=0.3)
    sns.despine(ax=ax3)

    for p in ax3.patches:
        height = p.get_height()
        if pd.notna(height) and height > 0:
            ax3.annotate(f'{int(height)}',
                        (p.get_x() + p.get_width()/2., height + 0.05),
                        ha='center', va='bottom',
                        fontsize=10, fontweight='bold', color='#000000')
            
    plt.tight_layout()
    st.pyplot(fig3)

with row2_col2:
    st.subheader("🔥 Correlation Heatmap")
    
    fig4, ax4 = plt.subplots(figsize=(7, 5))
    
    numeric_df = filtered_df.select_dtypes(include=['number'])
    
    if not numeric_df.empty and numeric_df.shape[0] > 1:
        sns.heatmap(
            numeric_df.corr(),
            annot=True,
            fmt=".2f",
            cmap="binary", # Pure Black and White / Grayscale mapping spectrum
            vmin=-1, vmax=1,
            linewidths=0.5,
            linecolor='#ffffff',
            square=False,
            cbar=True,
            annot_kws={"size": 8, "weight": "bold"},
            ax=ax4
        )
    else:
        # Graceful fallback display if there is 1 or 0 patients (where correlation can't be calculated)
        ax4.text(0.5, 0.5, "Insufficient data to calculate correlations\n(Select more patients)", 
                 ha='center', va='center', fontsize=12, color='#4b5563', weight='bold')
        ax4.grid(False)
        
    ax4.set_title("Feature Correlation Matrix", fontsize=14, fontweight='bold', pad=15, color="#000000")
    
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha='right', fontsize=9, fontweight='bold', color="#000000")
    ax4.set_yticklabels(ax4.get_yticklabels(), rotation=0, fontsize=9, fontweight='bold', color="#000000")
    
    plt.tight_layout()
    st.pyplot(fig4)

st.divider()

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<center>
<h5 style='color:#4b5563;'>
👨‍💻 Built with Streamlit | Professional Heart Disease Analytics Dashboard
</h5>
</center>
""", unsafe_allow_html=True)