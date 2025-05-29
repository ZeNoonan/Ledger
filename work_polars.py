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












































































































import streamlit as st
import polars as pl


def add_account_descriptions(df):
    """
    Add account descriptions based on account codes.
    Ensures 'account_description' is always a non-null string.
    
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
        "980": "Tax"
    }
    
    # Define specific mapping for 999 codes
    specific_999_mapping = {
        "999-0110": "Interco Shared Services",
        "999-0200": "Write-off",
    }
    
    # Ensure 'Account Code' is a string and fill any nulls before processing
    df = df.with_columns(
        pl.col("Account Code").cast(pl.String).fill_null("").alias("Account Code_processed")
    )
    
    # Create the account description column
    df = df.with_columns(
        pl.when(
            # Handle specific 999 codes first
            pl.col("Account Code_processed").is_in(list(specific_999_mapping.keys()))
        ).then(
            pl.col("Account Code_processed").replace(specific_999_mapping)
        ).when(
            # Handle first 3 digits mapping
            pl.col("Account Code_processed").str.slice(0, 3).is_in(list(three_digit_mapping.keys()))
        ).then(
            pl.col("Account Code_processed").str.slice(0, 3).replace(three_digit_mapping)
        ).otherwise(
            # Default for unmapped codes
            pl.lit("Unmapped Account")
        ).alias("account_description")
    ).drop("Account Code_processed") # Drop the temporary processed column
    
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
# Separate "Unmapped Account" from the rest
unmapped_ledger_summary = summary_by_description.filter(pl.col("account_description") == "Unmapped Account")
mapped_ledger_summary = summary_by_description.filter(pl.col("account_description") != "Unmapped Account")

if not unmapped_ledger_summary.is_empty():
    st.subheader("Unmapped Ledger Accounts:")
    st.write(unmapped_ledger_summary)
    st.markdown("---") # Add a separator

st.subheader("Mapped Ledger Accounts:")
st.write(mapped_ledger_summary)


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

# --- DEBUGGING STEP: Inspect budget_df after adding descriptions ---
st.subheader("DEBUGGING: Budget DataFrame after adding descriptions (first 10 rows)")
st.write(budget_df.head(10).collect())
st.write("Check 'account_description' column for any None values here.")
st.markdown("---")
# --- END DEBUGGING STEP ---


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
# Separate "Unmapped Account" from the rest
unmapped_budget_summary = summary_by_description_budget.filter(pl.col("account_description") == "Unmapped Account")
mapped_budget_summary = summary_by_description_budget.filter(pl.col("account_description") != "Unmapped Account")

if not unmapped_budget_summary.is_empty():
    st.subheader("Unmapped Budget Accounts:")
    st.write(unmapped_budget_summary)
    st.markdown("---") # Add a separator

st.subheader("Mapped Budget Accounts:")
st.write(mapped_budget_summary)


# VARIANCE ANALYSIS
st.header("Variance Analysis - Actuals vs Budget")

# Merge ledger and budget summaries by account code AND account description
variance_analysis_full = summary_by_account.join(
    summary_by_account_budget,
    on=["Account Code", "account_description"],
    how="full"
).with_columns([
    # Fill null values with 0 for accounts that don't exist in both datasets
    pl.col("Total Amount").fill_null(0),
    pl.col("Total Budget").fill_null(0)
]).with_columns([
    # Calculate variance (Actual - Budget)
    (pl.col("Total Amount") - pl.col("Total Budget")).alias("Variance"),
    # Add a column for the first three digits of the Account Code for sorting
    pl.col("Account Code").str.slice(0, 3).alias("Account Prefix") 
]).sort(["Account Prefix", "Account Code"]) # Sort by Account Prefix first, then Account Code

# Verification: Check that table totals match individual calculations
# These calculations use the full variance_analysis_full DataFrame
table_total_amount = variance_analysis_full.select(pl.sum("Total Amount")).item()
table_total_budget = variance_analysis_full.select(pl.sum("Total Budget")).item()

st.write("**DATA VERIFICATION:**")
st.write(f"Individual calculation - Total Amount: {total_amount:,.0f}")
st.write(f"Table sum - Total Amount: {table_total_amount:,.0f}")
st.write(f"✓ Match: {total_amount == table_total_amount}")

st.write(f"Individual calculation - Total Budget: {total_budget_value:,.0f}")
st.write(f"Table sum - Total Budget: {table_total_budget:,.0f}")
st.write(f"✓ Match: {total_budget_value == table_total_budget}")

st.write("**Variance Analysis by Account Description (Actuals vs Budget):**")
st.write("Positive variance = Actual > Budget | Negative variance = Actual < Budget")

# Group by account_description and sum the amounts for the final display
final_variance_display = variance_analysis_full.group_by("account_description").agg(
    pl.sum("Total Amount").alias("Total Amount"),
    pl.sum("Total Budget").alias("Total Budget"),
    pl.sum("Variance").alias("Variance") # Also sum the variance for consistency
).sort("account_description") # Sort by description for a clean output

st.write(final_variance_display)

# Calculate and display the sums of Total Amount and Total Budget from final_variance_display
total_amount_variance_sum = final_variance_display.select(pl.sum("Total Amount")).item()
total_budget_variance_sum = final_variance_display.select(pl.sum("Total Budget")).item()
total_variance_sum = final_variance_display.select(pl.sum("Variance")).item()

st.markdown("---")
st.subheader("Overall Variance Totals:")
st.write(f"**Total Actual Amount (from Variance Table):** {total_amount_variance_sum:,.0f}")
st.write(f"**Total Budget Amount (from Variance Table):** {total_budget_variance_sum:,.0f}")
st.write(f"**Overall Variance (Actual - Budget):** {total_variance_sum:,.0f}")
