import streamlit as st
import polars as pl

st.set_page_config(layout="wide")

st.write('I think the next thing to work on is the Employee Number in the ledger, as that is what is in the Budget file')

df = pl.read_excel(
    source="C:/Users/Darragh/Documents/Python/ledger/NL_2022_05.xlsx",
    sheet_name="Sheet1",
    columns=["Employee - Ext. Code", "Per.", "Account Code", "Journal Amount", "Employee"]
).with_columns(
    pl.col("Per.")
    .fill_null("")
    .str.strip_chars()  # Remove whitespace
    .map_elements(lambda x: None if x == "" else x, return_dtype=pl.Utf8)  # Convert empty strings to null
    .cast(pl.Int64)
).lazy()


# Check the data types more specifically
st.write("**Data type of 'Employee - Ext. Code' column:**")
st.write(df.collect_schema()["Employee - Ext. Code"])

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
summary_by_employee_all_periods = filtered_df.group_by(["Employee","Employee - Ext. Code"]).agg(
    pl.sum("Journal Amount")
).sort("Employee").collect()

# However Can I also get this summary by employee filtered further by 'Per.' column where it is filtered by the largest amount in the 'Per.' column?
max_period = filtered_df.select(pl.max("Per.")).collect().to_series().item()
summary_by_employee_filtered_max_period = filtered_df.filter(
    pl.col("Per.") == max_period
).group_by(["Employee","Employee - Ext. Code"]).agg(
    pl.sum("Journal Amount")
).sort("Employee").collect()

# Summary by account code with descriptions
summary_by_account_account = filtered_df.group_by(["Account Code"]).agg(
    pl.sum("Journal Amount")
).sort("Account Code").collect()


st.write("**Ledger Summary by Employee all periods:**")
st.write(summary_by_employee_all_periods)

st.write("**Ledger Summary by Employee latest period (max function on Per col):**")
st.write(summary_by_employee_filtered_max_period)

# this is crazy why isnt it reading the period number correctly, i guess i can change it

df_budget = pl.read_excel(
    source="C:/Users/Darragh/Documents/Python/ledger/Budget_Resourcing.xlsx",
    sheet_name="Budget",
    has_header=True,
).lazy()

# Fixed column names based on the actual schema from the error message
df_budget_all_detail = df_budget.unpivot(
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

st.write("**Budget:** all periods for all employees")
st.write(df_budget_all_detail)

# This is the summary by employee for the entire budget detail DataFrame
budget_by_employee_all_periods = df_budget_all_detail.group_by(["Name","Emp. num"]).agg(
    pl.sum("Amount")
).sort("Name")

st.write("**Budget Summary by Employee all periods:**")
st.write(budget_by_employee_all_periods)

# Check the data type of Ledger on the join column
st.write("**Data type of LEDGER 'Employee - Ext. Code' column:**")
st.write(df.collect_schema()["Employee - Ext. Code"])

# # Check the data type of Budget on the join column
st.write("**Data type of BUDGET 'Emp. num' column:**")
st.write(df_budget_all_detail.collect_schema()["Emp. num"])

# Check the data type of Ledger on the period which is in the 'Per.' column
st.write("**Data type of LEDGER 'Per.' column:**")
st.write(df.collect_schema()["Per."])

# # Check the data type of Budget on the period which is in the 'Month' column
st.write("**Data type of BUDGET 'Month' column:**")
st.write(df_budget_all_detail.collect_schema()["Month"])


# this is to get the summary employee for the same period as the ledger
# FIXED: Removed .collect() since df_budget_all_detail is already a DataFrame
budget_by_employee_filtered_max_period = df_budget_all_detail.filter(
    pl.col("Month") == max_period
).group_by(["Name","Emp. num"]).agg(
    pl.sum("Amount")
).sort("Name")  # Removed .collect() here

st.write("**Budget Summary by Employee for max period:**")
st.write(budget_by_employee_filtered_max_period)

# Join the ledger summary with budget summary
# First, let's rename columns to be clearer after the join
ledger_summary_renamed = summary_by_employee_all_periods.rename({
    "Journal Amount": "Ledger_Amount"
})

budget_summary_renamed = budget_by_employee_all_periods.rename({
    "Amount": "Budget_Amount"
})

# Perform the join on Employee - Ext. Code (ledger) and Emp. num (budget)
merged_summary = ledger_summary_renamed.join(
    budget_summary_renamed,
    left_on="Employee - Ext. Code",
    right_on="Emp. num",
    how="full"  # Use outer join to see all employees from both tables
).with_columns(
    # Calculate variance (Ledger - Budget)
    (pl.col("Ledger_Amount").fill_null(0) - pl.col("Budget_Amount").fill_null(0)).alias("Variance")
).select([
    "Employee",
    "Name", 
    "Employee - Ext. Code",
    "Emp. num",
    "Ledger_Amount",
    "Budget_Amount", 
    "Variance"
]).sort("Employee")

st.write("**Merged Summary: Ledger vs Budget (All Periods):**")
st.write(merged_summary)

# Calculate totals for the three numeric columns
totals = merged_summary.select([
    pl.sum("Ledger_Amount").fill_null(0).alias("Total_Ledger"),
    pl.sum("Budget_Amount").fill_null(0).alias("Total_Budget"),
    pl.sum("Variance").fill_null(0).alias("Total_Variance")
])

st.write("**Totals:**")
st.write(totals)