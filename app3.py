import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
import base64

st.set_page_config(page_title="📊 Universal CSV Analyzer", layout="wide")
st.title("📈 Universal Data Insights Dashboard")

# Sidebar with branding and info
st.sidebar.header("📂 Upload Options")
st.sidebar.markdown("Upload your CSV to begin analysis.")
st.sidebar.markdown("Built with ❤️ using Streamlit")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == 'object' else col)

    # Feature 1: Show key metrics
    st.subheader("📌 Dataset Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", f"{df.shape[0]:,}")
    col2.metric("Total Columns", f"{df.shape[1]:,}")
    col3.metric("Missing Values", f"{df.isnull().sum().sum():,}")

    # Feature 2: Column filter
    st.subheader("🔍 Raw Data Preview")
    selected_cols = st.multiselect("Select columns to view", df.columns.tolist(), default=df.columns.tolist())
    st.dataframe(df[selected_cols].head())

    st.subheader("📊 Column Summary")
    st.write(df.describe(include='all'))

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    # Graphs
    st.subheader("📌 Histogram")
    hist_col = st.selectbox("Select a numeric column", numeric_cols, key="hist")
    fig1, ax1 = plt.subplots()
    sns.histplot(df[hist_col].dropna(), kde=True, ax=ax1)
    st.pyplot(fig1)

    if len(numeric_cols) >= 2:
        st.subheader("🧊 Correlation Heatmap")
        fig2, ax2 = plt.subplots()
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax2)
        st.pyplot(fig2)

    st.subheader("🔄 Pair Plot")
    selected_pair_cols = st.multiselect("Choose numeric columns for pairplot", numeric_cols, default=numeric_cols[:2])
    if len(selected_pair_cols) >= 2:
        fig3 = sns.pairplot(df[selected_pair_cols].dropna())
        st.pyplot(fig3)

    st.subheader("🧁 Pie Chart")
    if categorical_cols:
        pie_col = st.selectbox("Choose a categorical column", categorical_cols, key="pie")
        pie_data = df[pie_col].value_counts().head(10)
        fig4, ax4 = plt.subplots()
        ax4.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
        ax4.axis('equal')
        st.pyplot(fig4)

    st.subheader("📦 Box Plot")
    if numeric_cols and categorical_cols:
        cat_col = st.selectbox("Category (X-axis)", categorical_cols, key="box_cat")
        num_col = st.selectbox("Numeric (Y-axis)", numeric_cols, key="box_num")
        fig5, ax5 = plt.subplots()
        sns.boxplot(x=cat_col, y=num_col, data=df, ax=ax5)
        plt.xticks(rotation=45)
        st.pyplot(fig5)

    st.subheader("📈 Line Chart")
    date_cols = df.select_dtypes(include=['datetime', 'object']).columns
    time_col = st.selectbox("X-axis (Time or Category)", date_cols, key="line_time")
    line_y = st.selectbox("Y-axis (Numeric)", numeric_cols, key="line_y")
    if time_col and line_y:
        try:
            df[time_col] = pd.to_datetime(df[time_col])
            df_sorted = df.sort_values(by=time_col)
            st.line_chart(df_sorted[[time_col, line_y]].set_index(time_col))
        except:
            st.warning("Couldn't parse dates in selected column.")

    st.subheader("📊 Bar Chart (Top Categories)")
    if categorical_cols:
        bar_col = st.selectbox("Select a column", categorical_cols, key="bar")
        bar_data = df[bar_col].value_counts().head(10)
        fig6, ax6 = plt.subplots()
        sns.barplot(x=bar_data.index, y=bar_data.values, ax=ax6)
        ax6.set_ylabel("Count")
        plt.xticks(rotation=45)
        st.pyplot(fig6)

    st.subheader("🔬 Scatter Plot")
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
        fig7, ax7 = plt.subplots()
        sns.scatterplot(x=df[x_col], y=df[y_col], ax=ax7)
        st.pyplot(fig7)

    st.subheader("🎻 Violin Plot")
    if numeric_cols and categorical_cols:
        v_cat = st.selectbox("Category (X-axis)", categorical_cols, key="violin_cat")
        v_num = st.selectbox("Numeric (Y-axis)", numeric_cols, key="violin_num")
        fig8, ax8 = plt.subplots()
        sns.violinplot(x=v_cat, y=v_num, data=df, ax=ax8)
        plt.xticks(rotation=45)
        st.pyplot(fig8)

    st.subheader("🌄 Area Chart")
    area_x = st.selectbox("X-axis (Time/Category)", date_cols, key="area_x")
    area_y = st.selectbox("Y-axis (Numeric)", numeric_cols, key="area_y")
    if area_x and area_y:
        try:
            df[area_x] = pd.to_datetime(df[area_x])
            df_sorted = df.sort_values(by=area_x)
            st.area_chart(df_sorted[[area_x, area_y]].set_index(area_x))
        except:
            st.warning("Couldn't parse dates.")

    st.subheader("📉 Count Plot (Category Frequency)")
    if categorical_cols:
        count_col = st.selectbox("Select a categorical column", categorical_cols, key="count")
        fig9, ax9 = plt.subplots()
        sns.countplot(data=df, x=count_col, order=df[count_col].value_counts().iloc[:10].index, ax=ax9)
        plt.xticks(rotation=45)
        st.pyplot(fig9)

    # Feature 3: Show missing value heatmap
    st.subheader("🩺 Missing Data Heatmap")
    fig10, ax10 = plt.subplots()
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis', ax=ax10)
    st.pyplot(fig10)

    # Feature 4: Download button
    st.subheader("📥 Download Processed CSV")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "cleaned_data.csv", "text/csv")

    # Feature 5: Raw column data insights
    st.subheader("🧠 Quick Insights")
    top_col = st.selectbox("Select column for summary", df.columns.tolist(), key="quick")
    st.write("Top 5 most frequent values:")
    st.write(df[top_col].value_counts().head())

else:
    st.info("Please upload a CSV file to begin.")
