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
    (pl.col("Account Code") == "921-0500") |
    (pl.col("Account Code") == "921-0550") |     
    (pl.col("Account Code") == "921-0600") |
    (pl.col("Account Code") == "921-0702") 
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
# Get the actual max period for default value
actual_max_period = filtered_df.select(pl.max("Per.")).collect().to_series().item()

# User input for max period
max_period = st.number_input(
    "Select the period number to filter by:",
    min_value=1,
    max_value=12,
    value=actual_max_period,
    step=1
)

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
    index=["Project", "Name", "Emp. num", "Emp. type", "Division", "Dept", "Title"],
    on=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    variable_name="Per.",
    value_name="Amount"
).with_columns(
    pl.col("Per.").cast(pl.Int64),  # Convert Month column from string to integer
    pl.col("Emp. num").cast(pl.Utf8),  # Convert to string after reading
    (pl.col("Amount") * 0.1105).alias("ER PRSI"),  # Add ER PRSI column (Amount * 11.05%)
    pl.when(pl.col("Division") == "TV")
        .then(pl.col("Amount") * 0.0145)  # 10% for tv
        .when(pl.col("Division") == "CG")
        .then(pl.col("Amount") * 0.018)  # 20% for dvd
        .when(pl.col("Division") == "Post")
        .then(pl.col("Amount") * 0.02)  # 50% for video
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
st.write("**Data type of BUDGET 'Per.' column:**")
st.write(df_budget_all_detail.collect_schema()["Per."])


# this is to get the summary employee for the same period as the ledger
# FIXED: Removed .collect() since df_budget_all_detail is already a DataFrame
budget_by_employee_filtered_max_period = df_budget_all_detail.filter(
    pl.col("Per.") == max_period
).group_by(["Name","Emp. num"]).agg(
    pl.sum("Amount")
).sort("Name")  # Removed .collect() here

st.write("**Budget Summary by Employee for max period:**")
st.write(budget_by_employee_filtered_max_period)

# NEW CODE: Use the max_period from user input for analysis
specific_period = max_period

# Create summaries for specific period (month 6 only)
st.write(f"## Analysis for Period {specific_period} Only")

# Ledger summary for specific period
ledger_summary_specific_period = filtered_df.filter(
    pl.col("Per.") == specific_period
).group_by(["Employee","Employee - Ext. Code"]).agg(
    pl.sum("Journal Amount")
).sort("Employee").collect()

# Budget summary for specific period
budget_summary_specific_period = df_budget_all_detail.filter(
    pl.col("Per.") == specific_period
).group_by(["Name","Emp. num"]).agg(
    pl.sum("Amount")
).sort("Name")

# Create summaries for cumulative periods (up to and including month 6)
st.write(f"## Analysis for Periods 1 through {specific_period} (Cumulative)")

# Ledger summary for cumulative periods
ledger_summary_cumulative = filtered_df.filter(
    pl.col("Per.") <= specific_period
).group_by(["Employee","Employee - Ext. Code"]).agg(
    pl.sum("Journal Amount")
).sort("Employee").collect()

# Budget summary for cumulative periods
budget_summary_cumulative = df_budget_all_detail.filter(
    pl.col("Per.") <= specific_period
).group_by(["Name","Emp. num"]).agg(
    pl.sum("Amount")
).sort("Name")

# FIRST MERGED SUMMARY: For specific period only (month 6)
ledger_summary_specific_renamed = ledger_summary_specific_period.rename({
    "Journal Amount": "Ledger_Amount"
})

budget_summary_specific_renamed = budget_summary_specific_period.rename({
    "Amount": "Budget_Amount"
})

merged_summary_specific_period = ledger_summary_specific_renamed.join(
    budget_summary_specific_renamed,
    left_on="Employee - Ext. Code",
    right_on="Emp. num",
    how="full"
).with_columns(
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

st.write(f"**Merged Summary: Ledger vs Budget (Period {specific_period} Only):**")
st.write(merged_summary_specific_period)

# Calculate totals for specific period
totals_specific = merged_summary_specific_period.select([
    pl.sum("Ledger_Amount").fill_null(0).alias("Total_Ledger"),
    pl.sum("Budget_Amount").fill_null(0).alias("Total_Budget"),
    pl.sum("Variance").fill_null(0).alias("Total_Variance")
])

st.write(f"**Totals for Period {specific_period}:**")
st.write(totals_specific)

# SECOND MERGED SUMMARY: For cumulative periods (up to and including month 6)
ledger_summary_cumulative_renamed = ledger_summary_cumulative.rename({
    "Journal Amount": "Ledger_Amount"
})

budget_summary_cumulative_renamed = budget_summary_cumulative.rename({
    "Amount": "Budget_Amount"
})

merged_summary_cumulative = ledger_summary_cumulative_renamed.join(
    budget_summary_cumulative_renamed,
    left_on="Employee - Ext. Code",
    right_on="Emp. num",
    how="full"
).with_columns(
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

st.write(f"**Merged Summary: Ledger vs Budget (Cumulative Periods 1-{specific_period}):**")
st.write(merged_summary_cumulative)

# Calculate totals for cumulative periods
totals_cumulative = merged_summary_cumulative.select([
    pl.sum("Ledger_Amount").fill_null(0).alias("Total_Ledger"),
    pl.sum("Budget_Amount").fill_null(0).alias("Total_Budget"),
    pl.sum("Variance").fill_null(0).alias("Total_Variance")
])

st.write(f"**Totals for Cumulative Periods 1-{specific_period}:**")
st.write(totals_cumulative)
