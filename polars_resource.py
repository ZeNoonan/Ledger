import streamlit as st
import polars as pl

st.set_page_config(layout="wide")

st.write('I think the next thing to work on is the Employee Number in the ledger, as that is what is in the Budget file')

df = pl.read_excel(
    source="C:/Users/Darragh/Documents/Python/ledger/NL_2022_05.xlsx",
    sheet_name="Sheet1",
).lazy()

# We'll use string comparison since account codes are stored as strings
filtered_df = df.filter(
    (pl.col("Account Code") >= "921-0500") & 
    (pl.col("Account Code") <= "921-0700")
)

# Calculate the total sum using LazyFrame operations
total_df = filtered_df.select(
    pl.sum("Journal Amount")
).collect()

total_amount = total_df.item()  # Get the single value from the DataFrame
st.write(f"**TOTAL AMOUNT**: The total Journal Amount for accounts 921-0500 to 921-0700 is {total_amount:,.0f}")
st.write(f"Use this value ({total_amount:,.0f}) to cross-check against your other source.")

# This is the summary by employee for the entire filtered DataFrame
summary_by_employee_all_periods = filtered_df.group_by(["Employee"]).agg(
    pl.sum("Journal Amount")
).sort("Employee").collect()

# However Can I also get this summary by employee filtered further by 'Per.' column where it is filtered by the largest amount in the 'Per.' column?
max_period = filtered_df.select(pl.max("Per.")).collect().to_series().item()
summary_by_account_filtered_max_period = filtered_df.filter(
    pl.col("Per.") == max_period
).group_by(["Employee"]).agg(
    pl.sum("Journal Amount")
).sort("Employee").collect()

# Summary by account code with descriptions
summary_by_account_account = filtered_df.group_by(["Account Code"]).agg(
    pl.sum("Journal Amount")
).sort("Account Code").collect()


st.write("**Ledger Summary by Employee all periods:**")
st.write(summary_by_employee_all_periods)

st.write("**Ledger Summary by Employee latest period (max function on Per col):**")
st.write(summary_by_account_filtered_max_period)

# this is crazy why isnt it reading the period number correctly, i guess i can change it

df = pl.read_excel(
    source="C:/Users/Darragh/Documents/Python/ledger/Budget_Resourcing.xlsx",
    sheet_name="Budget",
    has_header=True,
).lazy()

# Fixed column names based on the actual schema from the error message
df_long = df.unpivot(
    index=["Project", "Name", "Emp. num", "Emp. tpe", "Division", "Dept", "Title"],
    on=["1", "2", "3", "4", "5", "6"],
    variable_name="Month",
    value_name="Amount"
).with_columns(
    pl.col("Month").cast(pl.Int64),  # Convert Month column from string to integer
    (pl.col("Amount") * 0.1105).alias("ER PRSI"),  # Add ER PRSI column (Amount * 11.05%)
    pl.when(pl.col("Division") == "TV")
        .then(pl.col("Amount") * 0.10)  # 10% for tv
        .when(pl.col("Division") == "CG")
        .then(pl.col("Amount") * 0.20)  # 20% for dvd
        .when(pl.col("Division") == "Post")
        .then(pl.col("Amount") * 0.50)  # 50% for video
        .otherwise(0)  # Default to 0 if none match
        .alias("Pension")
).with_columns(
    (pl.col("Amount") + pl.col("ER PRSI") + pl.col("Pension")).alias("Total_Amount")  # Sum all three columns
).collect()

st.write("**Budget:**")
st.write(df_long)

