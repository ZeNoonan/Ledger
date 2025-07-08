import streamlit as st
import polars as pl

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

# print(df.collect_schema())

# st.dataframe(df.collect())
# print(df.collect())


df_long = df.unpivot(
    id_vars=["Project Name", "Emp. num", "Emp. tpe", "Division", "Dept", "Title"],
    value_vars=[1, 2, 3, 4, 5, 6],
    variable_name="Month",
    value_name="Amount"
)


# date_columns = [col for col in df.columns if col.endswith("-25") or col.endswith("-26")]
# description_columns = [col for col in df.columns if col not in date_columns]

# df_long = df.melt(
#     id_vars=description_columns,
#     value_vars=date_columns,
#     variable_name="Month",
#     value_name="Amount"
# )


st.write("**Budget:**")
st.write(df_long)

