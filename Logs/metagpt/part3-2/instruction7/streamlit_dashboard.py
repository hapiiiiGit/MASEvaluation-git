
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Data Exploration Dashboard")

df = pd.read_csv("train_for_bi.csv")
st.write("## Data Preview")
st.dataframe(df.head())

st.write("## Feature Distribution")
numeric_cols = df.select_dtypes(include="number").columns.tolist()
feature = st.selectbox("Select feature", numeric_cols)
fig, ax = plt.subplots()
sns.histplot(df[feature], kde=True, ax=ax)
st.pyplot(fig)

if "label" in df.columns:
    st.write("## Boxplot by Label")
    fig2, ax2 = plt.subplots()
    sns.boxplot(x="label", y=feature, data=df, ax=ax2)
    st.pyplot(fig2)
