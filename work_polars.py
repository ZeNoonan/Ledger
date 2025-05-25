import streamlit as st
import polars as pl


###
# The output is showing in the table "account description" and "account description right".  I only want one "account description" column.   Is there an issue?  Is that something to do with duplicates?  
# Can you also check that the sum of the "Total Amount" column and "Total Budget" column agrees to the line of code we wrote to call out "Total Amount: The total Journal Amount....".  I want to be sure that the table includes everything in the original data, so i guess it's a test.
# Do not sort the table and do not include the "Variance %" column
###

def add_account_descriptions(df):
    """
    Add account descriptions based on account codes.
    
    Parameters:
    -----------
    df : pl.LazyFrame
        DataFrame with 'Account Code' column
    
    Returns:
    --------
    pl.LazyFrame
        DataFrame with added 'account_description' column
    """
    
    # Define mapping for first 3 digits to descriptions
    # You can modify these mappings as needed
    three_digit_mapping = {
        "920": "Sales",
        "921": "Cost of Sales",
        "924": "Cost of Sales",
        "940": "Indirect Costs",
        "941": "Direct Costs",
        "942": "Materials",
        "943": "Labor",
        "944": "Overhead",
        "946": "Utilities",
        "947": "Legal Audit",
        "948": "Computer Costs",
        "951": "Depreciation",
        "953": "Other 953",
        "954": "Other 954",
        "955": "Other 955",
        "956": "Other 956",
        "971": "Bank Charges",
        "972": "Interest",
        "973": "FX Gains/Losses",
        # Add more mappings as needed for codes up to 980
        "980": "Tax"
    }
    
    # Define specific mapping for 999 codes
    # You can add more specific 999 mappings here
    specific_999_mapping = {
        "999-0110": "Interco Shared Services",
        "999-0200": "Write-off",
        # Add more specific 999 mappings as needed
        # "999-0300": "Another Description",
    }
    
    # Create the account description column
    df = df.with_columns(
        pl.when(
            # Handle specific 999 codes first
            pl.col("Account Code").is_in(list(specific_999_mapping.keys()))
        ).then(
            pl.col("Account Code").replace(specific_999_mapping)
        ).when(
            # Handle first 3 digits mapping
            pl.col("Account Code").str.slice(0, 3).is_in(list(three_digit_mapping.keys()))
        ).then(
            pl.col("Account Code").str.slice(0, 3).replace(three_digit_mapping)
        ).otherwise(
            # Default for unmapped codes
            pl.lit("Unmapped Account")
        ).alias("account_description")
    )
    
    return df

# LEDGER ACTUALS PROCESSING
st.header("Ledger Actuals Analysis")

# Read in the excel file from path: "C:/Users/Darragh/Documents/Python/Work/Data/NL_2022_05.xlsx"
# this is the ledger actuals file
df = pl.read_excel(
    source="C:/Users/Darragh/Documents/Python/ledger/NL_2022_05.xlsx",
    sheet_name="Sheet1",
).lazy()

# Add account descriptions to ledger actuals
df = add_account_descriptions(df)

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
st.write(f"**TOTAL AMOUNT**: The total Journal Amount for accounts 920-0000 to 999-9999 is {total_amount:,.0f}")
st.write(f"Use this value ({total_amount:,.0f}) to cross-check against your other source.")

# Summary by account code with descriptions
summary_by_account = filtered_df.group_by(["Account Code", "account_description"]).agg(
    pl.sum("Journal Amount").alias("Total Amount")
).sort("Account Code").collect()

st.write("**Ledger Summary by Account Code:**")
st.write(summary_by_account)

# Summary by account description category
summary_by_description = filtered_df.group_by("account_description").agg(
    pl.sum("Journal Amount").alias("Total Amount")
).sort("Total Amount", descending=True).collect()

st.write("**Ledger Summary by Account Description:**")
st.write(summary_by_description)

# BUDGET PROCESSING
st.header("Budget Analysis")

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
file_path = "C:/Users/Darragh/Documents/Python/ledger/Budget_2022.xlsx"
sheet_name = "Budget"  # Change this to the actual sheet name you want to use
num_months_to_sum = 6  # Change this to sum different number of months

# Process the budget file
budget_df = process_budget_file(file_path, sheet_name, num_months_to_sum)

# Add account descriptions
budget_df = add_account_descriptions(budget_df)

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
st.write(f"**TOTAL AMOUNT**: The total budget for accounts 920-0000 to 999-9999 (Months 1-{num_months_to_sum}) is {total_budget_value:,.0f}")
st.write(f"Use this value ({total_budget_value:,.0f}) to cross-check against your other source.")

# Summary by account code with descriptions
summary_by_account_budget = filtered_budget.group_by(["Account Code", "account_description"]).agg(
    pl.sum(f"Budget Sum (Months 1-{num_months_to_sum})").alias("Total Budget")
).sort("Account Code").collect()

st.write("**Budget Summary by Account Code:**")
st.write(summary_by_account_budget)

# Summary by account description category
summary_by_description_budget = filtered_budget.group_by("account_description").agg(
    pl.sum(f"Budget Sum (Months 1-{num_months_to_sum})").alias("Total Budget")
).sort("Total Budget", descending=True).collect()

st.write("**Budget Summary by Account Description:**")
st.write(summary_by_description_budget)

# VARIANCE ANALYSIS
st.header("Variance Analysis - Actuals vs Budget")

# Merge ledger and budget summaries by account description
variance_analysis = summary_by_description.join(
    summary_by_description_budget,
    on="account_description",
    how="full"
).with_columns([
    # Fill null values with 0 for accounts that don't exist in both datasets
    pl.col("Total Amount").fill_null(0),
    pl.col("Total Budget").fill_null(0)
]).with_columns([
    # Calculate variance (Actual - Budget)
    (pl.col("Total Amount") - pl.col("Total Budget")).alias("Variance"),
    # Calculate variance percentage
    (((pl.col("Total Amount") - pl.col("Total Budget")) / pl.col("Total Budget")) * 100).alias("Variance %")
]).sort("Variance", descending=True)

st.write("**Variance Analysis by Account Description (Actuals vs Budget):**")
st.write("Positive variance = Actual > Budget | Negative variance = Actual < Budget")
st.write(variance_analysis)