# import pandas as pd
# import numpy as np
import streamlit as st
import polars as pl

# read in the excel file from path: "C:/Users/Darragh/Documents/Python/Work/Data/NL_2022_05.xlsx"

df=pl.read_excel(
    source="C:/Users/Darragh/Documents/Python/Work/Data/NL_2022_05.xlsx",
    sheet_name="Sheet1",
).lazy()

# Filter account codes from 920-0000 to 999-9999
# We'll use string comparison since account codes are stored as strings
filtered_df = df.filter(
    (pl.col("Account Code") >= "920-0000") & 
    (pl.col("Account Code") <= "999-9999")
)

# Calculate the total sum using LazyFrame operations
total_df = filtered_df.select(
    pl.sum("Journal Amount").alias("Total Amount")
).collect()

total_amount = total_df.item()  # Get the single value from the DataFrame
print(f"Total Journal Amount for accounts 920-0000 to 999-9999: {total_amount}")

# If you want to see the results grouped by account code:
summary_by_account = filtered_df.group_by("Account Code").agg(
    pl.sum("Journal Amount").alias("Total Amount")
).sort("Account Code").collect()


st.write(summary_by_account)
# st.write(df.head())




import polars as pl

def process_budget_file(file_path, sheet_name, num_months=12):
    """
    Read and process budget file.
    
    Parameters:
    -----------
    file_path : str
        Path to the Excel budget file
    sheet_name : str
        Name of the sheet to read
    num_months : int, default=12
        Number of budget months to sum (from BUDGET 1 to BUDGET n)
    
    Returns:
    --------
    pl.LazyFrame
        Processed budget data with extracted account codes
    """
    st.write(f"Reading sheet '{sheet_name}' from budget file...")
    
    # Read the specified sheet from the Excel file
    budget_df = pl.read_excel(
        source=file_path,
        sheet_name=sheet_name
    ).lazy()
    
    # Extract the account code (last 8 characters) from the ACCOUNT column
    budget_df = budget_df.with_columns(
        pl.col("ACCOUNT").str.slice(-8).alias("Account Code")
    )
    
    # Validate the number of months
    if num_months < 1 or num_months > 12:
        raise ValueError("Number of months must be between 1 and 12")
    
    st.write(f"Summing budget columns BUDGET 1 through BUDGET {num_months}")
    
    # Create a list of budget columns to sum based on num_months
    budget_cols = [f"BUDGET {i}" for i in range(1, num_months + 1)]
    
    # Sum the specified budget columns
    budget_df = budget_df.with_columns(
        pl.sum_horizontal(budget_cols).alias(f"Budget Sum (Months 1-{num_months})")
    )
    
    return budget_df

# Example usage
file_path = "C:/Users/Darragh/Documents/Python/Work/Data/Budget_2022.xlsx"
sheet_name = "Budget"  # Change this to the actual sheet name you want to use
num_months_to_sum = 6  # Change this to sum different number of months

# Process the budget file
budget_df = process_budget_file(file_path, sheet_name, num_months_to_sum)

# Filter account codes from 920-0000 to 999-9999 (same as previous query)
filtered_budget = budget_df.filter(
    (pl.col("Account Code") >= "920-0000") & 
    (pl.col("Account Code") <= "999-9999")
)

# Get the total budget for filtered accounts
total_budget = filtered_budget.select(
    pl.sum(f"Budget Sum (Months 1-{num_months_to_sum})").alias("Total Budget")
).collect()

total_budget_value = total_budget.item()
st.write(f"\nTOTAL AMOUNT: The total budget for accounts 920-0000 to 999-9999 (Months 1-{num_months_to_sum}) is {total_budget_value}")
st.write(f"Use this value ({total_budget_value}) to cross-check against your other source.")

# Summary by account code
budget_summary_by_account = filtered_budget.group_by("Account Code").agg(
    pl.sum(f"Budget Sum (Months 1-{num_months_to_sum})").alias("Total Budget")
).sort("Account Code").collect()


st.write('budget',budget_summary_by_account)