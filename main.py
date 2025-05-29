import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data(path: str = "curated-solubility-dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    return df
st.set_page_config(layout="wide")
st.sidebar.write("Directory")
page = st.sidebar.selectbox("Select function", ["Home",
                                                "Searcher",
                                                "2D Scatterplot",
                                                "3D Scatterplot",
                                                "Solubility Comparison",
                                                "Function 5"]) #add another functionality for #5 
df = load_data()

#HOMEPAGE ----------------------------------------

if page == "Home":
    st.title("🔬 Welcome to the AqSolDB Explorer!")
    st.write("Select a feature from the sidebar..")
    st.markdown("""
    - **Searcher**: lookup compounds by compound name/InChI/SMILES  
    - **2D Scatterplot** 2D Plot of Solubility vs one descriptor 
    - **3D Scatterplot** 3D Space of Solubility vs two descriptors
    - **Solubility Comparison Tool** Compare solubilities of different compounds!
    - **insert renzo's** under construction
    """)

#1. SEARCHER ----------------------------------------
elif page == "Searcher":
    st.title("🔎 Compound Searcher")
    q = st.text_input("Search Name/InChI/InChIKey/SMILES")
    filtered = df.copy()
    if q:
        masks = [filtered[col].str.contains(q, case=False, na=False)
                 for col in ["Name","InChI","InChIKey","SMILES"]]
        filtered = filtered[pd.concat(masks, axis=1).any(axis=1)]
    st.dataframe(filtered, use_container_width=True)

#2. 2D SCATTERPLOT ----------------------------------------
elif page == "2D Scatterplot":
    st.sidebar.header("Filter & Plot Settings")

    # 1) MolWt slider filter
    min_mw, max_mw = float(df["MolWt"].min()), float(df["MolWt"].max())
    mw_low, mw_high = st.sidebar.slider(
        "Show scatterplot datapoints based on molecular weight range:",
        min_value=min_mw,
        max_value=max_mw,
        value=(min_mw, max_mw),
        step=1.0
    )
    df = df[(df["MolWt"] >= mw_low) & (df["MolWt"] <= mw_high)]

    # 2) Choose X-axis descriptor
    x_option = st.sidebar.selectbox(
        "Select X-axis descriptor:",
        [
            "NumHAcceptors","NumHDonors","NumHeteroatoms","NumRotatableBonds",
            "NumValenceElectrons","NumAromaticRings","NumSaturatedRings",
            "NumAliphaticRings","RingCount","HeavyAtomCount","MolWt",
        ],
        index=10  # default to MolWt
    )

    # --- Scatter Plot ---
    fig = px.scatter(
        df,
        x=x_option,
        y="Solubility",
        color="Solubility",                      
        color_continuous_scale="Plasma",         
        hover_data=["Name", x_option, "Solubility"],
        labels={x_option: x_option, "Solubility": "Solubility (LogS)"},
        title=f"Solubility vs. {x_option} (filtered by MolWt)"
    )

    # Tweak layout if needed
    fig.update_layout(
        coloraxis_colorbar=dict(title="LogS"),
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # --- Display ---
    st.plotly_chart(fig, use_container_width=True)

elif page == "3D Scatterplot":
    st.title("🗺️ 3D Chemical Space: Solubility vs Descriptors")

    # — Load —
    st.sidebar.header("Filter & Plot Settings")

    # 1) MolWt slider filter
    min_mw, max_mw = float(df["MolWt"].min()), float(df["MolWt"].max())
    mw_low, mw_high = st.sidebar.slider(
        "Show scatterplot datapoints based on molecular weight range:",
        min_value=min_mw,
        max_value=max_mw,
        value=(min_mw, max_mw),
        step=1.0
    )
    df = df[(df["MolWt"] >= mw_low) & (df["MolWt"] <= mw_high)]

    # — Sidebar: axis selectors —
    st.sidebar.header("3D Scatter Settings")
    cols = [
        "NumHAcceptors","NumHDonors","NumHeteroatoms","NumRotatableBonds",
        "NumValenceElectrons","NumAromaticRings","NumSaturatedRings",
        "NumAliphaticRings","RingCount","HeavyAtomCount","MolWt"
    ]

    x_axis = st.sidebar.selectbox("X axis", cols, index=0)
    y_axis = st.sidebar.selectbox("Y axis", cols, index=1)

    # — Build 3D scatter —
    fig = px.scatter_3d(
        df,
        x=x_axis,
        y=y_axis,
        z="Solubility",
        color="Solubility",
        color_continuous_scale="Viridis",
        hover_name="Name",
        hover_data=[x_axis, y_axis, "Solubility"],
        labels={"Solubility":"LogS"},
        title=f"3D Scatter: {x_axis} vs {y_axis} vs Solubility"
    )

    fig.update_layout(
        scene=dict(
            xaxis_title=x_axis,
            yaxis_title=y_axis
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )

    # — Display —
    st.plotly_chart(fig, use_container_width=True)

elif page == "Solubility Comparison":
    st.title("📊 Solubility Comparison Tool")
    st.write("Select compounds below to compare their solubility values (LogS).")

    # Multiselect for compound names
    compound_options = df["Name"].dropna().unique()
    selected = st.multiselect("Select compounds to compare:", compound_options)

    # Filter and show comparison
    if selected:
        compare_df = df[df["Name"].isin(selected)][["Name", "Solubility"]].drop_duplicates()

        st.subheader("📋 Comparison Table")
        st.dataframe(compare_df, use_container_width=True)

        st.subheader("📈 Solubility Bar Chart (LogS)")
        fig = px.bar(
            compare_df,
            x="Name",
            y="Solubility",
            color="Solubility",
            color_continuous_scale="Blues",
            labels={"Solubility": "LogS"},
            title="Solubility Comparison"
        )
        fig.update_layout(xaxis_title="Compound", yaxis_title="Solubility (LogS)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select one or more compounds to compare.")

else:
    st.markdown("under construction")
