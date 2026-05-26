import pandas as pd
import numpy as np
import plotly.express as px
import os

def main():
    """
    Standalone Ticker Bubble Chart Diagnostic Script
    Reads the market analysis CSV, prints stats, and generates a standalone interactive bubble chart.
    """
    csv_path = "indian_market_analysis.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file '{csv_path}' not found.")
        print("💡 Please run the main analyzer first: python data_market_visualization.py")
        return

    print("======================================================================")
    print("🇮🇳  STANDALONE BUBBLE CHART DIAGNOSTIC RUN")
    print("======================================================================")
    
    print("\n📖 Loading market data...")
    df_raw = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df_raw)} stock records successfully.")

    # Drop missing values in the required columns
    required_cols = ['PE Ratio', 'Revenue Growth %', 'Market Cap (Cr)']
    df = df_raw.dropna(subset=required_cols)
    print(f"⚡ Cleaned {len(df_raw) - len(df)} rows with missing data. {len(df)} active stocks remaining.")

    # 1. Print Raw Statistics (Highlighting Outlier Squishing)
    print("\n📊 Pre-Filter Data Ranges (The Outlier Issue):")
    print(f"   • PE Ratio: Min = {df['PE Ratio'].min():.2f}, Max = {df['PE Ratio'].max():.2f}, Median = {df['PE Ratio'].median():.2f}")
    print(f"   • Revenue Growth %: Min = {df['Revenue Growth %'].min():.2f}%, Max = {df['Revenue Growth %'].max():.2f}%, Median = {df['Revenue Growth %'].median():.2f}%")
    print(f"   • Market Cap (Cr): Min = {df['Market Cap (Cr)'].min():,.0f} Cr, Max = {df['Market Cap (Cr)'].max():,.0f} Cr, Median = {df['Market Cap (Cr)'].median():,.0f} Cr")

    # 2. Viewport Capping Parameters
    pe_lower, pe_upper = 0, 80
    growth_lower, growth_upper = -20, 80

    df_filtered = df[(df['PE Ratio'] >= pe_lower) & (df['PE Ratio'] <= pe_upper)]
    df_filtered = df_filtered[(df_filtered['Revenue Growth %'] >= growth_lower) & (df_filtered['Revenue Growth %'] <= growth_upper)]
    
    print(f"\n🧹 Applied visible range filters:")
    print(f"   • P/E display window: [{pe_lower}, {pe_upper}]")
    print(f"   • Revenue Growth display window: [{growth_lower}%, {growth_upper}%]")
    print(f"✅ {len(df_filtered)} out of {len(df)} stocks ({len(df_filtered)/len(df)*100:.1f}%) fit perfectly inside this visible viewport!")

    # 3. Plotting using native Market Cap (Cr) bubble sizing
    print("\n💹 Generating standalone Plotly Express bubble chart...")
    fig = px.scatter(
        df,
        x='PE Ratio',
        y='Revenue Growth %',
        size='Market Cap (Cr)',
        color='Sector',
        hover_name='Company',
        hover_data={
            'PE Ratio': ':.2f',
            'Revenue Growth %': ':.2f',
            'Market Cap (Cr)': ':,.0f',
            'ROE %': ':.2f',
            'Combined Score': ':.1f'
        },
        size_max=60,
        title='💹 Standalone Test: PE Ratio vs Revenue Growth (Viewport Capped)'
    )

    # Set the viewport ranges on layout (panning/zooming still loaded for full data)
    fig.update_xaxes(range=[pe_lower, pe_upper], dtick=10)
    fig.update_yaxes(range=[growth_lower, growth_upper], dtick=20)

    # Add quadrant lines based on medians
    if not df['PE Ratio'].empty:
        median_pe = df['PE Ratio'].median()
        median_growth = df['Revenue Growth %'].median()
        fig.add_hline(y=median_growth, line_dash="dash", line_color="white", opacity=0.5)
        fig.add_vline(x=median_pe, line_dash="dash", line_color="white", opacity=0.5)

    # Output standalone chart
    output_html = "test_bubble_chart_standalone.html"
    fig.write_html(output_html)
    
    print("\n🎉 STANDALONE CHART GENERATED SUCCESSFULLY!")
    print(f"   👉 File: {os.path.abspath(output_html)}")
    print("   💡 Double-click the HTML file to view the fully scaled, interactive bubble chart in your browser!")
    print("======================================================================")

if __name__ == "__main__":
    main()
