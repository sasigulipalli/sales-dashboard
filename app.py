# @Email:  contact@pythonandvba.com
# @Website:  https://pythonandvba.com
# @YouTube:  https://youtube.com/c/CodingIsFun
# @Project:  Sales Dashboard w/ Streamlit



import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

# ---- READ EXCEL ----
@st.cache
def get_data_from_excel():
    df = pd.read_excel(
        io="supermarkt_sales.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=3,
        usecols="B:R",
        nrows=1000,
    )
    # Add 'hour' column to dataframe
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    #add date column
    # Convert the Date column to datetime format
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = get_data_from_excel()
Summary = df.describe()
st.dataframe(df)
st.title(":bar_chart: Sales summary")
st.dataframe(Summary)


# Remove the count row as it is not relevant for visualization
summary = Summary.drop("count")

# Create the pie chart
fig = px.pie(summary.T, values="mean", names=summary.T.index, 
             title="<b>Summary Statistics</b>", template="plotly_white")

st.plotly_chart(fig,  use_container_width=True)

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
city = st.sidebar.multiselect(
    "Select the City:",
    options=df["City"].unique(),
    default=df["City"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select the Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique(),
)

gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

df_selection = df.query(
    "City == @city & Customer_type ==@customer_type & Gender == @gender"
)
#st.dataframe(df_selection)

# ---- MAINPAGE ----
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"US $ {average_sale_by_transaction}")

st.markdown("""---""")

# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = (
    df_selection.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
)
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY HOUR [BAR CHART]
sales_by_hour = df_selection.groupby(by=["hour"]).sum()[["Total"]]
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

#most used payment methods
# Group by both Gender and Payment columns and count the occurrences
grouped_df = df_selection.groupby(["Gender", "Payment"]).size().reset_index(name="count")

# Create the grouped bar chart
fig_payment = px.bar(
    grouped_df,
    x="Payment",
    y="count",
    color="Gender",
    title="<b>Payment Method by Gender</b>",
    barmode="group",
    color_discrete_sequence=["#0083B8", "#F5A623"],
    template="plotly_white",
)

# Customize the layout
fig_payment.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(showgrid=False),
)

# Most profitable product lines # bubblee plot
profitable_products = df_selection.groupby("Product line").agg({"Quantity": "sum", "Total": "sum", "gross income": "sum"})
profitable_products = profitable_products.reset_index()

# Create bubble chart
fig_product = px.scatter(profitable_products, x="Total", y="Quantity", size="gross income", color="Product line",
                 title="<b>Profitable Product Lines</b>")
fig_product.update_layout(xaxis_title="Total Sales", yaxis_title="Quantity Sold", showlegend=False,
                  plot_bgcolor="rgba(0,0,0,0)")


# Scatter plot
# Group the data by customer type and gender, and calculate the mean rating for each group
df_grouped = df_selection.groupby(["Customer_type", "Gender"], as_index=False)["Rating"].mean()

fig_scatter = px.scatter(df_grouped, x="Customer_type", y="Rating", color="Gender", color_discrete_sequence=["#0083B8", "#F5A623"])

# Update the layout
fig_scatter.update_layout(
    title="<b>Relationship between Customer Type, Gender, and Rating</b>",
    xaxis_title="Customer Type",
    yaxis_title="Rating",
    template="plotly_white",
)

#heat map
# Select the columns to include in the correlation matrix
cols = ["Total", "Quantity", "Unit price", "Tax 5%"]

# Create the correlation matrix
corr = df_selection[cols].corr()

# Create the heatmap
fig = px.imshow(corr, x=cols, y=cols,
                color_continuous_scale="RdBu",
                title="<b>Correlation between Total, Quantity, Unit Price, and Tax 5%</b>",
                labels=dict(x="Column", y="Column", color="Correlation"),
                width=500, height=500)

# Update the layout
fig.update_layout(
    title="<b>Correlation between Total, Quantity, Unit Price, and Tax 5%</b>",
    xaxis_title="Column",
    yaxis_title="Column",
    coloraxis=dict(colorscale="RdBu", colorbar=dict(title="Correlation")),
    template="plotly_white"
)

# Filter the data by gender and group the data by date and gender, and calculate the mean rating for each day and gender
df_rating = df_selection.groupby(["Date", "Gender"], as_index=False)["Rating"].mean()

# Create the line chart
fig_rating = px.line(df_rating, x="Date", y="Rating", color="Gender",
              title="<b>Average Rating Over Time by Gender</b>",
              labels={"Date": "Date", "Rating": "Average Rating", "Gender": "Gender"},
              template="plotly_white")

# Update the layout
fig_rating.update_layout(
    xaxis_title="Date",
    yaxis_title="Average Rating",
)


#trail plot

# Group the data by date and time, and calculate the total sales and number of products sold for each group
df_grouped = df.groupby(["Date", "Time"], as_index=False).agg({"Total": "sum", "Quantity": "sum"})

# Create the bubble chart
fig_trial = px.scatter(df_grouped, x="Date", y="Time", size="Total", color="Total",
                 title="<b>Total Sales vs. Date and Time</b>",
                 labels={"Total": "Total Sales", "Quantity": "Number of Products Sold"},
                 template="plotly_white")

# Update the layout
fig_trial.update_layout(
    xaxis_title="Date",
    yaxis_title="Time",
)



left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales,  use_container_width=True)
left_column.plotly_chart(fig_payment,  use_container_width=True)
left_column.plotly_chart(fig_scatter,  use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)
right_column.plotly_chart(fig_product, use_container_width=True)
right_column.plotly_chart(fig, use_container_width=True)
left_column.plotly_chart(fig_rating, use_container_width=True)
right_column.plotly_chart(fig_trial, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
