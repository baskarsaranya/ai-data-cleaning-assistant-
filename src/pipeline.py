import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_data(filepath):
    print("=" * 50)
    print("LOADING DATA")
    print("=" * 50)
    
    # Check if file exists
    import os
    if not os.path.exists(filepath):
        print("ERROR: File not found. Please check your filepath.")
        return None
    
    # Check file extension
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_extension = os.path.splitext(filepath)[1].lower()
    
    if file_extension not in allowed_extensions:
        print(f"ERROR: Unsupported file type '{file_extension}'.")
        print(f"Supported formats: CSV, Excel (.xlsx, .xls)")
        return None
    
    # Try loading the file
    try:
        if file_extension == '.csv':
            df = pd.read_csv(filepath)
            print(f"SUCCESS: CSV file loaded.")
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
            print(f"SUCCESS: Excel file loaded.")
        
        # Check if file is empty
        if df.empty:
            print("ERROR: File is empty. Please upload a file with data.")
            return None
        
        # Check if file has at least 2 columns
        if df.shape[1] < 2:
            print("ERROR: File has less than 2 columns. Not enough data to analyse.")
            return None
        
        print(f"Rows loaded: {df.shape[0]}")
        print(f"Columns loaded: {df.shape[1]}")
        print("=" * 50)
        return df
    
    except Exception as e:
        print(f"ERROR: Could not read file. Reason: {str(e)}")
        return None
def standardize_column_names(df):
    print("\n--- Step 1: Standardizing Column Names ---")
    
    old_columns = df.columns.tolist()
    
    # Convert to lowercase, strip spaces, replace spaces with underscores
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # Rename the two confusing lead time columns
    rename_map = {}
    if 'lead_times' in df.columns:
        rename_map['lead_times'] = 'supplier_lead_time'
    if 'lead_time' in df.columns:
        rename_map['lead_time'] = 'customer_lead_time'
    
    df = df.rename(columns=rename_map)
    
    new_columns = df.columns.tolist()
    
    # Report changes
    changes = 0
    for old, new in zip(old_columns, new_columns):
        if old != new:
            print(f"  Renamed: '{old}' → '{new}'")
            changes += 1
    
    print(f"\n  Total columns renamed: {changes}")
    print("  ✓ Column names standardized")
    return df
def fix_datatypes(df):
    print("\n--- Step 2: Fixing Data Types ---")
    
    fixes = 0
    
    for col in df.columns:
        
        # Only attempt conversion on object columns
        if df[col].dtype == 'object':
            
            # Check if majority of values look numeric
            # Try converting and see how many succeed
            converted = pd.to_numeric(df[col], errors='coerce')
            success_rate = converted.notna().sum() / len(df)
            
            # Only convert if 90% or more values are numeric
            if success_rate >= 0.90:
                df[col] = converted
                print(f"  Converted '{col}' from text to numeric (success rate: {success_rate*100:.1f}%)")
                fixes += 1
                continue
            
            # Check if it looks like a date column
            if any(keyword in col.lower() for keyword in 
                   ['date', 'time', 'day', 'month', 'year']):
                try:
                    df[col] = pd.to_datetime(df[col])
                    print(f"  Converted '{col}' to datetime")
                    fixes += 1
                    continue
                except:
                    pass
    
    if fixes == 0:
        print("  All columns already have correct data types")
    else:
        print(f"\n  Total dtype fixes: {fixes}")
    
    print("  ✓ Data types checked")
    return df
def remove_duplicates(df):
    print("\n--- Step 3: Removing Duplicates ---")
    
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    removed = before - after
    
    if removed == 0:
        print("  No duplicate rows found")
    else:
        print(f"  Removed {removed} duplicate rows")
        print(f"  Rows before: {before}")
        print(f"  Rows after: {after}")
    
    print("  ✓ Duplicates checked")
    return df
def handle_missing_values(df):
    print("\n--- Step 4: Handling Missing Values ---")
    
    # Also treat suspicious text values as missing
    suspicious = ['unknown', 'n/a', 'na', 'none', 'null',
                  'not available', 'missing', 'undefined']
    
    # Replace suspicious text values with NaN first
    for col in df.select_dtypes(include='object').columns:
        mask = df[col].str.lower().str.strip().isin(suspicious)
        count = mask.sum()
        if count > 0:
            df.loc[mask, col] = np.nan
            print(f"  Converted {count} suspicious values to NaN in '{col}'")
    
    fixes = 0
    
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        
        if missing_count > 0:
            missing_pct = (missing_count / len(df)) * 100
            
            # If more than 50% missing suggest dropping
            if missing_pct > 50:
                print(f"  WARNING: '{col}' has {missing_pct:.1f}% missing")
                print(f"  Suggestion: Consider dropping this column")
                choice = input(f"  Drop '{col}'? (yes/no): ").strip().lower()
                if choice == 'yes':
                    df = df.drop(columns=[col])
                    print(f"  ✓ Dropped '{col}'")
                    fixes += 1
                    continue
            
            # Fill numeric columns
            if df[col].dtype in ['int64', 'float64']:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                print(f"  Filled {missing_count} missing in '{col}' with median {median_val:.2f}")
                fixes += 1
            
            # Fill categorical columns
            elif df[col].dtype == 'object':
                mode_val = df[col].mode()[0]
                df[col] = df[col].fillna(mode_val)
                print(f"  Filled {missing_count} missing in '{col}' with mode '{mode_val}'")
                fixes += 1
    
    if fixes == 0:
        print("  No missing values found")
    
    print("  ✓ Missing values handled")
    return df
def fix_text_consistency(df):
    print("\n--- Step 5: Fixing Text Consistency ---")
    
    fixes = 0
    
    for col in df.select_dtypes(include='object').columns:
        # Strip extra spaces
        before = df[col].copy()
        df[col] = df[col].str.strip()
        
        # Standardize to title case
        df[col] = df[col].str.title()
        
        # Check if anything changed
        changes = (before != df[col]).sum()
        if changes > 0:
            print(f"  Fixed {changes} inconsistent values in '{col}'")
            fixes += 1
    
    if fixes == 0:
        print("  No text inconsistencies found")
    
    print("  ✓ Text consistency fixed")
    return df

def detect_outliers(df):
    print("\n--- Step 6: Detecting Outliers ---")
    
    outlier_report = []
    
    for col in df.select_dtypes(include='number').columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        
        if len(outliers) > 0:
            outlier_report.append({
                'column': col,
                'count': len(outliers),
                'lower_bound': round(lower, 2),
                'upper_bound': round(upper, 2)
            })
            print(f"  '{col}': {len(outliers)} outliers found")
            print(f"    Acceptable range: {lower:.2f} to {upper:.2f}")
    
    if not outlier_report:
        print("  No outliers detected")
    else:
        print(f"\n  NOTE: Outliers are flagged but NOT removed.")
        print(f"  In supply chain, extreme values may be real events.")
        print(f"  Review them manually before deciding to remove.")
    
    print("  ✓ Outlier check complete")
    return df, outlier_report
def save_cleaned_data(df):
    print("\n--- Step 7: Saving Cleaned Data ---")
    
    output_path = 'C:/SupplyChainAssistant/outputs/supply_chain_cleaned.csv'
    df.to_csv(output_path, index=False)
    
    print(f"  ✓ Cleaned data saved to:")
    print(f"    {output_path}")
    print(f"  Rows: {df.shape[0]}")
    print(f"  Columns: {df.shape[1]}")
    return output_path
def run_pipeline(filepath):
    print("=" * 50)
    print("SUPPLY CHAIN DATA CLEANING PIPELINE")
    print("=" * 50)
    
    # Load data
    df = load_data(filepath)
    if df is None:
        return None
    
    # Make a copy - never touch original
    df_clean = df.copy()
    
    # Run all cleaning steps in order
    df_clean = standardize_column_names(df_clean)
    df_clean = fix_datatypes(df_clean)
    df_clean = remove_duplicates(df_clean)
    df_clean = handle_missing_values(df_clean)
    df_clean = fix_text_consistency(df_clean)
    df_clean, outlier_report = detect_outliers(df_clean)
    save_cleaned_data(df_clean)
    
    # Final summary
    print("\n" + "=" * 50)
    print("PIPELINE COMPLETE")
    print("=" * 50)
    print(f"Original shape:  {df.shape}")
    print(f"Cleaned shape:   {df_clean.shape}")
    print(f"Columns removed: {df.shape[1] - df_clean.shape[1]}")
    print(f"Rows removed:    {df.shape[0] - df_clean.shape[0]}")
    print("=" * 50)
    
    return df_clean

def plot_numeric_distributions(df):
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    
    print(f"Plotting distributions for {len(numeric_cols)} numeric columns...")
    
    # Calculate grid size
    cols = 3
    rows = (len(numeric_cols) + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 4))
    axes = axes.flatten()
    
    for i, col in enumerate(numeric_cols):
        axes[i].hist(df[col], bins=20, color='steelblue', 
                     edgecolor='white', alpha=0.8)
        axes[i].set_title(f'{col}', fontsize=11, fontweight='bold')
        axes[i].set_xlabel('Value')
        axes[i].set_ylabel('Count')
    
    # Hide empty subplots
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle('Numeric Column Distributions', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('C:/SupplyChainAssistant/outputs/numeric_distributions.png',
                bbox_inches='tight')
    print("✓ Saved: numeric_distributions.png")
    return fig  # ADD THIS LINE


def plot_categorical_distributions(df):
    # Skip ID-like columns
    cat_cols = [col for col in df.select_dtypes(include='object').columns
                if df[col].nunique() < 15]
    
    print(f"Plotting bar charts for {len(cat_cols)} categorical columns...")
    
    cols = 2
    rows = (len(cat_cols) + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(14, rows * 4))
    axes = axes.flatten()
    
    for i, col in enumerate(cat_cols):
        value_counts = df[col].value_counts()
        axes[i].bar(value_counts.index, value_counts.values,
                   color=sns.color_palette("husl", len(value_counts)))
        axes[i].set_title(f'{col}', fontsize=11, fontweight='bold')
        axes[i].set_xlabel('Category')
        axes[i].set_ylabel('Count')
        axes[i].tick_params(axis='x', rotation=30)
    
    # Hide empty subplots
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle('Categorical Column Distributions',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('C:/SupplyChainAssistant/outputs/categorical_distributions.png',
                bbox_inches='tight')
    
    print("✓ Saved: categorical_distributions.png")
    return fig


def plot_correlation_heatmap(df):
    print("Plotting correlation heatmap...")
    
    numeric_df = df.select_dtypes(include='number')
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    correlation = numeric_df.corr()
    
    sns.heatmap(correlation, 
                annot=True, 
                fmt='.2f',
                cmap='coolwarm',
                center=0,
                square=True,
                ax=ax,
                cbar_kws={'shrink': 0.8})
    
    ax.set_title('Correlation Between Numeric Columns',
                fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('C:/SupplyChainAssistant/outputs/correlation_heatmap.png',
                bbox_inches='tight')
    
    print("✓ Saved: correlation_heatmap.png")
    return fig



def analyze_supplier_performance(df):
    print("=" * 50)
    print("SUPPLIER PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    insights = []
    
    # Average defect rate by supplier
    supplier_defects = df.groupby('supplier_name')['defect_rates'].mean().sort_values(ascending=False)
    
    print("\n📊 Average Defect Rate by Supplier:")
    for supplier, rate in supplier_defects.items():
        flag = " ⚠️  HIGH" if rate > supplier_defects.mean() else ""
        print(f"  {supplier}: {rate:.2f}%{flag}")
    
    worst_supplier = supplier_defects.index[0]
    best_supplier = supplier_defects.index[-1]
    insights.append(f"Highest defect rate: {worst_supplier} ({supplier_defects[worst_supplier]:.2f}%)")
    insights.append(f"Lowest defect rate: {best_supplier} ({supplier_defects[best_supplier]:.2f}%)")
    
    # Average lead time by supplier
    supplier_leadtime = df.groupby('supplier_name')['supplier_lead_time'].mean().sort_values(ascending=False)
    
    print("\n📊 Average Lead Time by Supplier (days):")
    for supplier, days in supplier_leadtime.items():
        flag = " ⚠️  SLOW" if days > supplier_leadtime.mean() else ""
        print(f"  {supplier}: {days:.1f} days{flag}")
    
    slowest_supplier = supplier_leadtime.index[0]
    insights.append(f"Slowest supplier: {slowest_supplier} ({supplier_leadtime[slowest_supplier]:.1f} days avg lead time)")
    
    # Plot supplier performance
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    supplier_defects.plot(kind='bar', ax=axes[0], color='salmon', edgecolor='white')
    axes[0].set_title('Defect Rate by Supplier', fontweight='bold')
    axes[0].set_xlabel('Supplier')
    axes[0].set_ylabel('Avg Defect Rate (%)')
    axes[0].axhline(y=supplier_defects.mean(), color='red', 
                    linestyle='--', label='Average')
    axes[0].legend()
    axes[0].tick_params(axis='x', rotation=30)
    
    supplier_leadtime.plot(kind='bar', ax=axes[1], color='steelblue', edgecolor='white')
    axes[1].set_title('Lead Time by Supplier', fontweight='bold')
    axes[1].set_xlabel('Supplier')
    axes[1].set_ylabel('Avg Lead Time (days)')
    axes[1].axhline(y=supplier_leadtime.mean(), color='red',
                    linestyle='--', label='Average')
    axes[1].legend()
    axes[1].tick_params(axis='x', rotation=30)
    
    plt.suptitle('Supplier Performance Dashboard', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('C:/SupplyChainAssistant/outputs/supplier_performance.png',
                bbox_inches='tight')
    
    
    print("\n💡 KEY INSIGHTS:")
    for insight in insights:
        print(f"  → {insight}")
    
    return fig, insights

def analyze_quality(df):
    print("=" * 50)
    print("QUALITY & INSPECTION ANALYSIS")
    print("=" * 50)
    
    insights = []
    
    # Overall inspection results
    inspection_counts = df['inspection_results'].value_counts()
    total = len(df)
    
    print("\n📊 Inspection Results Overview:")
    for result, count in inspection_counts.items():
        pct = (count / total) * 100
        flag = " ⚠️  CRITICAL" if result == 'Fail' and pct > 20 else ""
        print(f"  {result}: {count} products ({pct:.1f}%){flag}")
    
    fail_pct = (inspection_counts.get('Fail', 0) / total) * 100
    pass_pct = (inspection_counts.get('Pass', 0) / total) * 100
    
    if fail_pct > 20:
        insights.append(f"CRITICAL: {fail_pct:.1f}% of products are failing inspection")
    if pass_pct < 30:
        insights.append(f"WARNING: Only {pass_pct:.1f}% of products passing inspection")
    
    # Defect rate by product type
    product_defects = df.groupby('product_type')['defect_rates'].mean().sort_values(ascending=False)
    
    print("\n📊 Defect Rate by Product Type:")
    for product, rate in product_defects.items():
        flag = " ⚠️" if rate > product_defects.mean() else ""
        print(f"  {product}: {rate:.2f}%{flag}")
    
    worst_product = product_defects.index[0]
    insights.append(f"Highest defect product: {worst_product} ({product_defects[worst_product]:.2f}%)")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    colors = {'Pass': 'green', 'Fail': 'red', 'Pending': 'orange'}
    bar_colors = [colors.get(x, 'gray') for x in inspection_counts.index]
    
    axes[0].bar(inspection_counts.index, inspection_counts.values,
               color=bar_colors, edgecolor='white')
    axes[0].set_title('Inspection Results', fontweight='bold')
    axes[0].set_xlabel('Result')
    axes[0].set_ylabel('Count')
    
    product_defects.plot(kind='bar', ax=axes[1], 
                        color='coral', edgecolor='white')
    axes[1].set_title('Defect Rate by Product Type', fontweight='bold')
    axes[1].set_xlabel('Product Type')
    axes[1].set_ylabel('Avg Defect Rate (%)')
    axes[1].tick_params(axis='x', rotation=30)
    
    plt.suptitle('Quality Analysis Dashboard',
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('C:/SupplyChainAssistant/outputs/quality_analysis.png',
                bbox_inches='tight')
    
    
    print("\n💡 KEY INSIGHTS:")
    for insight in insights:
        print(f"  → {insight}")
    
    return fig, insights


def analyze_shipping(df):
    print("=" * 50)
    print("SHIPPING & ROUTE ANALYSIS")
    print("=" * 50)
    
    insights = []
    
    # Average shipping time by carrier
    carrier_times = df.groupby('shipping_carriers')['shipping_times'].mean().sort_values(ascending=False)
    
    print("\n📊 Average Shipping Time by Carrier (days):")
    for carrier, days in carrier_times.items():
        flag = " ⚠️  SLOW" if days > carrier_times.mean() else ""
        print(f"  {carrier}: {days:.1f} days{flag}")
    
    slowest_carrier = carrier_times.index[0]
    insights.append(f"Slowest carrier: {slowest_carrier} ({carrier_times[slowest_carrier]:.1f} days avg)")
    
    # Average shipping cost by route
    route_costs = df.groupby('routes')['shipping_costs'].mean().sort_values(ascending=False)
    
    print("\n📊 Average Shipping Cost by Route:")
    for route, cost in route_costs.items():
        flag = " ⚠️  EXPENSIVE" if cost > route_costs.mean() else ""
        print(f"  {route}: {cost:.2f}{flag}")
    
    expensive_route = route_costs.index[0]
    insights.append(f"Most expensive route: {expensive_route} (avg cost {route_costs[expensive_route]:.2f})")
    
    # Route utilisation
    route_util = df['routes'].value_counts()
    underused = route_util[route_util < route_util.mean()]
    if len(underused) > 0:
        for route in underused.index:
            insights.append(f"Underutilised route: {route} (only {route_util[route]} shipments)")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    carrier_times.plot(kind='bar', ax=axes[0], 
                      color='mediumpurple', edgecolor='white')
    axes[0].set_title('Shipping Time by Carrier', fontweight='bold')
    axes[0].set_xlabel('Carrier')
    axes[0].set_ylabel('Avg Shipping Time (days)')
    axes[0].axhline(y=carrier_times.mean(), color='red',
                   linestyle='--', label='Average')
    axes[0].legend()
    axes[0].tick_params(axis='x', rotation=30)
    
    route_costs.plot(kind='bar', ax=axes[1],
                    color='teal', edgecolor='white')
    axes[1].set_title('Shipping Cost by Route', fontweight='bold')
    axes[1].set_xlabel('Route')
    axes[1].set_ylabel('Avg Shipping Cost')
    axes[1].axhline(y=route_costs.mean(), color='red',
                   linestyle='--', label='Average')
    axes[1].legend()
    axes[1].tick_params(axis='x', rotation=30)
    
    plt.suptitle('Shipping & Route Analysis Dashboard',
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('C:/SupplyChainAssistant/outputs/shipping_analysis.png',
                bbox_inches='tight')
    
    
    print("\n💡 KEY INSIGHTS:")
    for insight in insights:
        print(f"  → {insight}")
    
    return fig, insights


def generate_insights_summary(supplier_insights, quality_insights, shipping_insights):
    print("=" * 50)
    print("SUPPLY CHAIN INSIGHTS SUMMARY REPORT")
    print("=" * 50)
    
    all_insights = supplier_insights + quality_insights + shipping_insights
    
    print(f"\nTotal issues detected: {len(all_insights)}")
    
    print("\n🏭 SUPPLIER ISSUES:")
    for i in supplier_insights:
        print(f"  → {i}")
    
    print("\n🔍 QUALITY ISSUES:")
    for i in quality_insights:
        print(f"  → {i}")
    
    print("\n🚚 SHIPPING ISSUES:")
    for i in shipping_insights:
        print(f"  → {i}")
    
    print("\n" + "=" * 50)
    print("END OF INSIGHTS REPORT")
    print("=" * 50)

    return all_insights
