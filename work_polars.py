import streamlit as st
import polars as pl


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
        "926": "Advertising",
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

# DEBUGGING SECTION - Let's investigate the data before joining
st.subheader("Debug Information")

# Check actuals data
actuals_debug = filtered_df.select([
    "Account Code", 
    "Journal Amount"
]).filter(pl.col("Account Code").is_null()).collect()

st.write(f"**Actuals with NULL Account Codes:** {len(actuals_debug)} records")
if len(actuals_debug) > 0:
    st.write(actuals_debug.head(10))

# Check budget data
budget_debug = filtered_budget.select([
    "Account Code", 
    f"Budget Sum (Months 1-{num_months_to_sum})"
]).filter(pl.col("Account Code").is_null()).collect()

st.write(f"**Budget with NULL Account Codes:** {len(budget_debug)} records")
if len(budget_debug) > 0:
    st.write(budget_debug.head(10))

# Check unique account codes in each dataset
actuals_accounts = filtered_df.select("Account Code").unique().sort("Account Code").collect()
budget_accounts = filtered_budget.select("Account Code").unique().sort("Account Code").collect()

st.write(f"**Unique Account Codes in Actuals:** {len(actuals_accounts)}")
st.write(f"**Unique Account Codes in Budget:** {len(budget_accounts)}")

# Find accounts that exist in budget but not in actuals
budget_only = budget_accounts.join(actuals_accounts, on="Account Code", how="anti")
st.write(f"**Accounts in Budget but NOT in Actuals:** {len(budget_only)}")
if len(budget_only) > 0:
    st.write(budget_only.head(10))

# Find accounts that exist in actuals but not in budget  
actuals_only = actuals_accounts.join(budget_accounts, on="Account Code", how="anti")
st.write(f"**Accounts in Actuals but NOT in Budget:** {len(actuals_only)}")
if len(actuals_only) > 0:
    st.write(actuals_only.head(10))

# Create variance analysis table
# First, get actuals data grouped by account code
actuals_for_variance = filtered_df.group_by("Account Code").agg([
    pl.sum("Journal Amount").alias("Total Amount"),
    pl.first("account_description").alias("Account Description")
]).with_columns(
    # Add 3-digit mapping column
    pl.col("Account Code").str.slice(0, 3).alias("3_digit_mapping")
)

# Get budget data grouped by account code
budget_for_variance = filtered_budget.group_by("Account Code").agg([
    pl.sum(f"Budget Sum (Months 1-{num_months_to_sum})").alias("Total Budget"),
    pl.first("account_description").alias("Account Description")
]).with_columns(
    # Add 3-digit mapping column
    pl.col("Account Code").str.slice(0, 3).alias("3_digit_mapping")
)

st.write('budget for variance', budget_for_variance)

# Perform full outer join to capture all accounts from both datasets
variance_analysis = actuals_for_variance.join(
    budget_for_variance,
    on="Account Code",
    how="full"
).with_columns([
    # Coalesce account descriptions (use actuals first, then budget)
    pl.coalesce([pl.col("Account Description"), pl.col("Account Description_right")]).alias("Account Description"),
    # Coalesce 3-digit mappings
    pl.coalesce([pl.col("3_digit_mapping"), pl.col("3_digit_mapping_right")]).alias("3_digit_mapping"),
    # Fill nulls with 0 for amounts
    pl.col("Total Amount").fill_null(0),
    pl.col("Total Budget").fill_null(0)
]).with_columns([
    # Calculate variance (Actual - Budget)
    (pl.col("Total Amount") - pl.col("Total Budget")).alias("Variance")
]).select([
    "Account Code",
    "Account Description", 
    "3_digit_mapping",
    "Total Amount",
    "Total Budget",
    "Variance"
]).sort("Account Code")

# Collect the variance analysis
variance_table = variance_analysis.collect()

st.write("**Variance Analysis Table:**")
st.write(variance_table)

# VALIDATION TESTS
st.subheader("Validation Tests")

# Test 1: Verify actuals total matches original
original_actuals_total = total_amount
variance_actuals_total = variance_table.select(pl.sum("Total Amount")).item()

st.write(f"**Actuals Validation:**")
st.write(f"Original actuals total: {original_actuals_total:,.0f}")
st.write(f"Variance table actuals total: {variance_actuals_total:,.0f}")
st.write(f"Difference: {abs(original_actuals_total - variance_actuals_total):,.0f}")

if abs(original_actuals_total - variance_actuals_total) < 0.01:
    st.success("✅ PASS: Actuals totals match!")
else:
    st.error("❌ FAIL: Actuals totals do not match!")

# Test 2: Verify budget total matches original
original_budget_total = total_budget_value
variance_budget_total = variance_table.select(pl.sum("Total Budget")).item()

st.write(f"**Budget Validation:**")
st.write(f"Original budget total: {original_budget_total:,.0f}")
st.write(f"Variance table budget total: {variance_budget_total:,.0f}")
st.write(f"Difference: {abs(original_budget_total - variance_budget_total):,.0f}")

if abs(original_budget_total - variance_budget_total) < 0.01:
    st.success("✅ PASS: Budget totals match!")
else:
    st.error("❌ FAIL: Budget totals do not match!")


























st.write("###################################################################################################")










































































































st.write("###################################################################################################")
st.header('PANDAS CODE')

import streamlit as st
import pandas as pd


def add_account_descriptions(df):
    """
    Add account descriptions based on account codes.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with 'Account Code' column
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with added 'account_description' column
    """
    
    # Define mapping for first 3 digits to descriptions
    # You can modify these mappings as needed
    three_digit_mapping = {
        "920": "Sales",
        "921": "Cost of Sales",
        "924": "Cost of Sales",
        "926": "Advertising",
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
    
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()
    
    # Initialize the account_description column
    df['account_description'] = 'Unmapped Account'
    
    # Apply specific 999 codes first
    mask_999 = df['Account Code'].isin(specific_999_mapping.keys())
    df.loc[mask_999, 'account_description'] = df.loc[mask_999, 'Account Code'].map(specific_999_mapping)
    
    # Apply three-digit mapping for non-999 codes
    mask_three_digit = (~mask_999) & (df['Account Code'].str[:3].isin(three_digit_mapping.keys()))
    df.loc[mask_three_digit, 'account_description'] = df.loc[mask_three_digit, 'Account Code'].str[:3].map(three_digit_mapping)
    
    return df

# LEDGER ACTUALS PROCESSING
st.header("Ledger Actuals Analysis")

# Read in the excel file from path: "C:/Users/Darragh/Documents/Python/Work/Data/NL_2022_05.xlsx"
# this is the ledger actuals file
st.cache_data()
df = pd.read_excel(
    "C:/Users/Darragh/Documents/Python/ledger/NL_2022_05.xlsx",
    sheet_name="Sheet1"
)

# Add account descriptions to ledger actuals
df = add_account_descriptions(df)

# Filter account codes from 920-0000 to 999-9999
# We'll use string comparison since account codes are stored as strings
filtered_df = df[
    (df["Account Code"] >= "920-0000") & 
    (df["Account Code"] <= "999-9999")
].copy()

# Calculate the total sum
total_amount = filtered_df["Journal Amount"].sum()
st.write(f"**TOTAL AMOUNT**: The total Journal Amount for accounts 920-0000 to 999-9999 is {total_amount:,.0f}")
st.write(f"Use this value ({total_amount:,.0f}) to cross-check against your other source.")

# Summary by account code with descriptions
summary_by_account = (filtered_df.groupby(["Account Code", "account_description"])["Journal Amount"]
                     .sum()
                     .reset_index()
                     .rename(columns={"Journal Amount": "Total Amount"})
                     .sort_values("Account Code"))

# st.write("**Ledger Summary by Account Code:**")
# st.write(summary_by_account)

# Summary by account description category
summary_by_description = (filtered_df.groupby("account_description")["Journal Amount"]
                         .sum()
                         .reset_index()
                         .rename(columns={"Journal Amount": "Total Amount"})
                         .sort_values("Total Amount", ascending=False))


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
    pd.DataFrame
        Processed budget data with extracted account codes
    """
    st.write(f"Reading sheet '{sheet_name}' from budget file...")
    
    # Read the specified sheet from the Excel file
    budget_df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Extract the account code (last 8 characters) from the ACCOUNT column
    budget_df['Account Code'] = budget_df['ACCOUNT'].str[-8:]
    
    # Validate the number of months
    if num_months < 1 or num_months > 12:
        raise ValueError("Number of months must be between 1 and 12")
    
    st.write(f"Summing budget columns BUDGET 1 through BUDGET {num_months}")
    
    # Create a list of budget columns to sum based on num_months
    budget_cols = [f"BUDGET {i}" for i in range(1, num_months + 1)]
    
    # Sum the specified budget columns
    budget_df[f"Budget Sum (Months 1-{num_months})"] = budget_df[budget_cols].sum(axis=1)
    
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
filtered_budget = budget_df[
    (budget_df["Account Code"] >= "920-0000") & 
    (budget_df["Account Code"] <= "999-9999")
].copy()

# Get the total budget for filtered accounts
total_budget_value = filtered_budget[f"Budget Sum (Months 1-{num_months_to_sum})"].sum()
st.write(f"**TOTAL AMOUNT**: The total budget for accounts 920-0000 to 999-9999 (Months 1-{num_months_to_sum}) is {total_budget_value:,.0f}")
st.write(f"Use this value ({total_budget_value:,.0f}) to cross-check against your other source.")

# Summary by account code with descriptions
summary_by_account_budget = (filtered_budget.groupby(["Account Code", "account_description"])[f"Budget Sum (Months 1-{num_months_to_sum})"]
                            .sum()
                            .reset_index()
                            .rename(columns={f"Budget Sum (Months 1-{num_months_to_sum})": "Total Budget"})
                            .sort_values("Account Code"))


# Summary by account description category
summary_by_description_budget = (filtered_budget.groupby("account_description")[f"Budget Sum (Months 1-{num_months_to_sum})"]
                                .sum()
                                .reset_index()
                                .rename(columns={f"Budget Sum (Months 1-{num_months_to_sum})": "Total Budget"})
                                .sort_values("Total Budget", ascending=False))


# VARIANCE ANALYSIS
st.header("Variance Analysis - Actuals vs Budget")

# Check unique account codes in each dataset
actuals_accounts = filtered_df["Account Code"].unique()
budget_accounts = filtered_budget["Account Code"].unique()


# Find accounts that exist in budget but not in actuals
budget_only = pd.DataFrame({"Account Code": budget_accounts})
budget_only = budget_only[~budget_only["Account Code"].isin(actuals_accounts)].sort_values("Account Code")
# st.write(f"**Accounts in Budget but NOT in Actuals:** {len(budget_only)}")
# if len(budget_only) > 0:
#     st.write(budget_only.head(10))

# Find accounts that exist in actuals but not in budget  
actuals_only = pd.DataFrame({"Account Code": actuals_accounts})
actuals_only = actuals_only[~actuals_only["Account Code"].isin(budget_accounts)].sort_values("Account Code")
# st.write(f"**Accounts in Actuals but NOT in Budget:** {len(actuals_only)}")
# if len(actuals_only) > 0:
#     st.write(actuals_only.head(10))

# Create variance analysis table
# First, get actuals data grouped by account code
actuals_for_variance = (filtered_df.groupby("Account Code")
                       .agg({
                           "Journal Amount": "sum",
                           "account_description": "first"
                       })
                       .reset_index()
                       .rename(columns={"Journal Amount": "Total Amount", 
                                      "account_description": "Account Description"}))

# Add 3-digit mapping column
actuals_for_variance["3_digit_mapping"] = actuals_for_variance["Account Code"].str[:3]

# Get budget data grouped by account code
budget_for_variance = (filtered_budget.groupby("Account Code")
                      .agg({
                          f"Budget Sum (Months 1-{num_months_to_sum})": "sum",
                          "account_description": "first"
                      })
                      .reset_index()
                      .rename(columns={f"Budget Sum (Months 1-{num_months_to_sum})": "Total Budget",
                                     "account_description": "Account Description"}))

# Add 3-digit mapping column
budget_for_variance["3_digit_mapping"] = budget_for_variance["Account Code"].str[:3]


# Perform full outer join to capture all accounts from both datasets
variance_analysis = pd.merge(
    actuals_for_variance,
    budget_for_variance,
    on="Account Code",
    how="outer",
    suffixes=("", "_budget")
)

# Coalesce account descriptions (use actuals first, then budget)
variance_analysis["Account Description"] = variance_analysis["Account Description"].fillna(
    variance_analysis["Account Description_budget"]
)

# Coalesce 3-digit mappings
variance_analysis["3_digit_mapping"] = variance_analysis["3_digit_mapping"].fillna(
    variance_analysis["3_digit_mapping_budget"]
)

# Fill nulls with 0 for amounts
variance_analysis["Total Amount"] = variance_analysis["Total Amount"].fillna(0)
variance_analysis["Total Budget"] = variance_analysis["Total Budget"].fillna(0)

# Calculate variance (Actual - Budget)
variance_analysis["Variance"] = variance_analysis["Total Amount"] - variance_analysis["Total Budget"]

# Select final columns
variance_table = variance_analysis[["Account Code", "Account Description", "3_digit_mapping", 
                                  "Total Amount", "Total Budget", "Variance"]].sort_values("Account Code")

st.write("**Variance Analysis Table:**")
st.write(variance_table)

# VALIDATION: Check that variance table totals match original totals
st.header("Validation - Total Reconciliation")

variance_total_amount = variance_table["Total Amount"].sum()
variance_total_budget = variance_table["Total Budget"].sum()

st.write("**Reconciliation Check:**")
st.write(f"Original Ledger Total Amount: {total_amount:,.0f}")
st.write(f"Variance Table Total Amount: {variance_total_amount:,.0f}")
st.write(f"Difference (Ledger - Variance): {total_amount - variance_total_amount:,.0f}")

st.write(f"Original Budget Total Amount: {total_budget_value:,.0f}")
st.write(f"Variance Table Total Budget: {variance_total_budget:,.0f}")
st.write(f"Difference (Budget - Variance): {total_budget_value - variance_total_budget:,.0f}")

# Check if totals match (allowing for small floating point differences)
ledger_match = abs(total_amount - variance_total_amount) < 0.01
budget_match = abs(total_budget_value - variance_total_budget) < 0.01

if ledger_match and budget_match:
    st.success("✅ VALIDATION PASSED: All totals match between original analysis and variance table!")
else:
    st.error("❌ VALIDATION FAILED: Totals do not match!")
    if not ledger_match:
        st.error(f"Ledger totals mismatch: {total_amount:,.2f} vs {variance_total_amount:,.2f}")
    if not budget_match:
        st.error(f"Budget totals mismatch: {total_budget_value:,.2f} vs {variance_total_budget:,.2f}")
