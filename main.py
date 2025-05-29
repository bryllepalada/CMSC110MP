import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_ketcher import st_ketcher

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
                                                "Molecule Visualizer"]) 
df = load_data()

#HOMEPAGE ----------------------------------------

if page == "Home":
    st.title("Welcome to _SoluSilip_!")
    st.write("This interactive web app is based on AqSolDB dataset by  Murat Sorkhun, Abishek Khetan and Er Süleyman.")
    st.write(
    "You may view their data set [here](https://www.nature.com/articles/s41597-019-0151-1)"
    ", published in *Scientific Data* last 2018 with 204 citations.")
    st.header("Select a feature from the sidebar.")
    st.markdown("""
    - **Searcher**: Lookup compounds by compound IUPAC Name/InChI/SMILES!  
    - **2D Scatterplot**: 2D Plot of Solubility vs one descriptor chosen by you!
    - **3D Scatterplot**: 3D Space of Solubility vs two descriptors chosen by you!
    - **Solubility Comparison Tool**: Compare solubilities of different compounds!
    - **Molecule Visualizer**: Generate 2-D structures of compounds in the database! Or Search compound name from your drawing!
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
    st.title("📈 2D Scatterplot")
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

    fig.update_layout(
        coloraxis_colorbar=dict(title="LogS"),
        margin=dict(l=40, r=40, t=80, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

elif page == "3D Scatterplot":
    st.title("🗺️ 3D Chemical Space: Solubility vs Descriptors")

    st.sidebar.header("Filter & Plot Settings")

    min_mw, max_mw = float(df["MolWt"].min()), float(df["MolWt"].max())
    mw_low, mw_high = st.sidebar.slider(
        "Show scatterplot datapoints based on molecular weight range:",
        min_value=min_mw,
        max_value=max_mw,
        value=(min_mw, max_mw),
        step=1.0
    )
    df = df[(df["MolWt"] >= mw_low) & (df["MolWt"] <= mw_high)]

    st.sidebar.header("3D Scatter Settings")
    cols = [
        "NumHAcceptors","NumHDonors","NumHeteroatoms","NumRotatableBonds",
        "NumValenceElectrons","NumAromaticRings","NumSaturatedRings",
        "NumAliphaticRings","RingCount","HeavyAtomCount","MolWt"
    ]

    x_axis = st.sidebar.selectbox("X axis", cols, index=0)
    y_axis = st.sidebar.selectbox("Y axis", cols, index=1)

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

    st.plotly_chart(fig, use_container_width=True)

elif page == "Solubility Comparison":
    st.title("📊 Solubility Comparison Tool")
    st.write("Select compounds below to compare their solubility values (LogS).")

    compound_options = df["Name"].dropna().unique()
    selected = st.multiselect("Select compounds to compare:", compound_options)

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
            color_continuous_scale="Viridis",
            labels={"Solubility": "LogS"},
            title="Solubility Comparison"
        )
        fig.update_layout(xaxis_title="Compound", yaxis_title="Solubility (LogS)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select one or more compounds to compare.")

else:
    st.title("⚛️ Molecule Visualizer")
    st.caption("Pick one compound from the dataset, then enter its name or ID in the sidebar to see its 2-D structure.")
    st.sidebar.header("Dataset Browser")

    def show_table():
        st.dataframe(
            df[["ID", "Name", "SMILES", "Solubility", "MolWt", "MolLogP"]].sort_values("Solubility"),
            use_container_width=True,
        )

    if st.sidebar.checkbox("Show data table"):
        show_table()

    query = st.sidebar.text_input("🔍 Quick search (Name or ID)")
    if query:
        hits = df[df["Name"].str.contains(query, case=False) | df["ID"].str.contains(query, case=False)]
        st.sidebar.write(f"Found {len(hits)} match(es)")
        for idx, row in hits.head(5).iterrows():
            if st.sidebar.button(f"Load ➜ {row['Name']} ({row['ID']})"):
                st.session_state["preset_smiles"] = row["SMILES"]
    
    smiles = st_ketcher(value=st.session_state.get("preset_smiles", ""))
    if smiles:
        records = df[df["SMILES"] == smiles]
        if not records.empty:
            st.success("Match found in dataset! Displaying properties below.")
            st.dataframe(records.T.rename(columns={records.index[0]: "Value"}))
        else:
            st.info("No matching entry in the dataset. Try browsing or drawing another molecule.")
    else:
        st.info("Draw or load a molecule to see its properties here.")
