"""
Advanced example: Demonstrating Markov attribution with more realistic customer journey data.

This example shows how undervalued channels can be identified and budget reallocated
for a 15% budget shift scenario.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from markov_attribution import MarkovAttribution
from visualization import create_summary_report
import matplotlib.pyplot as plt


def create_realistic_scenario():
    """
    Create a realistic marketing scenario with 6 channels where Email and Organic
    Search are undervalued but highly effective.
    """
    # Define the 6 marketing channels
    channels = ['Social Media', 'Email', 'Paid Search', 'Organic Search', 'Display Ads', 'Direct']
    
    # Realistic customer journey paths with conversions
    # These paths reflect real-world marketing scenarios where some channels
    # assist in the journey but don't get credit in last-click models
    paths_data = [
        # Direct conversions (high conversion rate)
        {'path': 'Direct', 'conversions': 450, 'non_conversions': 550},
        {'path': 'Organic Search', 'conversions': 380, 'non_conversions': 720},
        {'path': 'Email', 'conversions': 320, 'non_conversions': 580},
        {'path': 'Paid Search', 'conversions': 290, 'non_conversions': 810},
        {'path': 'Social Media', 'conversions': 180, 'non_conversions': 920},
        {'path': 'Display Ads', 'conversions': 110, 'non_conversions': 990},
        
        # Two-touch journeys (Email and Organic are great assists)
        {'path': 'Email > Direct', 'conversions': 280, 'non_conversions': 320},
        {'path': 'Organic Search > Direct', 'conversions': 320, 'non_conversions': 380},
        {'path': 'Social Media > Direct', 'conversions': 140, 'non_conversions': 360},
        {'path': 'Paid Search > Direct', 'conversions': 250, 'non_conversions': 450},
        {'path': 'Display Ads > Direct', 'conversions': 90, 'non_conversions': 410},
        
        {'path': 'Email > Organic Search', 'conversions': 190, 'non_conversions': 310},
        {'path': 'Organic Search > Email', 'conversions': 180, 'non_conversions': 320},
        {'path': 'Paid Search > Organic Search', 'conversions': 160, 'non_conversions': 440},
        {'path': 'Social Media > Organic Search', 'conversions': 120, 'non_conversions': 380},
        {'path': 'Display Ads > Organic Search', 'conversions': 100, 'non_conversions': 400},
        
        # Three-touch journeys (showing Email and Organic's role in nurturing)
        {'path': 'Social Media > Email > Direct', 'conversions': 210, 'non_conversions': 290},
        {'path': 'Display Ads > Email > Direct', 'conversions': 150, 'non_conversions': 350},
        {'path': 'Paid Search > Email > Direct', 'conversions': 180, 'non_conversions': 320},
        
        {'path': 'Social Media > Organic Search > Direct', 'conversions': 190, 'non_conversions': 310},
        {'path': 'Display Ads > Organic Search > Direct', 'conversions': 160, 'non_conversions': 340},
        {'path': 'Paid Search > Organic Search > Direct', 'conversions': 200, 'non_conversions': 300},
        
        {'path': 'Display Ads > Social Media > Email', 'conversions': 95, 'non_conversions': 305},
        {'path': 'Paid Search > Social Media > Organic Search', 'conversions': 110, 'non_conversions': 390},
        
        # Four-touch journeys (complex paths where Email/Organic assist)
        {'path': 'Display Ads > Social Media > Email > Direct', 'conversions': 140, 'non_conversions': 260},
        {'path': 'Display Ads > Paid Search > Email > Direct', 'conversions': 130, 'non_conversions': 270},
        {'path': 'Social Media > Paid Search > Organic Search > Direct', 'conversions': 145, 'non_conversions': 255},
        {'path': 'Display Ads > Social Media > Organic Search > Direct', 'conversions': 125, 'non_conversions': 275},
        
        # Five-touch journeys (showing full customer journey)
        {'path': 'Display Ads > Social Media > Email > Organic Search > Direct', 'conversions': 110, 'non_conversions': 190},
        {'path': 'Display Ads > Paid Search > Social Media > Email > Direct', 'conversions': 100, 'non_conversions': 200},
    ]
    
    paths_df = pd.DataFrame(paths_data)
    
    # Current budget allocation - typical over-investment in paid channels
    # This reflects a common scenario where companies over-invest in paid ads
    current_budget = {
        'Paid Search': 35000,     # Over-invested
        'Display Ads': 28000,     # Over-invested
        'Social Media': 17000,    # Slightly over-invested
        'Direct': 10000,          # Reasonable
        'Organic Search': 8000,   # UNDERVALUED (should be higher)
        'Email': 2000,            # SEVERELY UNDERVALUED (should be much higher)
    }
    
    return paths_df, current_budget


def main():
    print("=" * 80)
    print("ADVANCED MARKOV CHAIN ATTRIBUTION ANALYSIS")
    print("Identifying Undervalued Channels for 15% Budget Reallocation")
    print("=" * 80)
    print()
    
    # Create realistic scenario
    paths_df, current_budget = create_realistic_scenario()
    total_budget = sum(current_budget.values())
    
    print(f"Dataset Statistics:")
    print(f"  - Unique customer journey paths: {len(paths_df)}")
    print(f"  - Total conversions: {paths_df['conversions'].sum():,}")
    print(f"  - Total non-conversions: {paths_df['non_conversions'].sum():,}")
    print(f"  - Conversion rate: {paths_df['conversions'].sum() / (paths_df['conversions'].sum() + paths_df['non_conversions'].sum()) * 100:.1f}%")
    print(f"  - Total marketing budget: ${total_budget:,}")
    print()
    
    # Fit the model
    print("Fitting Markov Chain Attribution Model...")
    model = MarkovAttribution()
    model.fit(paths_df)
    print("✓ Model fitted successfully!")
    print()
    
    # Show attribution results
    print("=" * 80)
    print("CHANNEL ATTRIBUTION ANALYSIS")
    print("=" * 80)
    print()
    
    attribution_df = model.get_attribution_dataframe()
    print(attribution_df.to_string(index=False))
    print()
    
    # Show current budget
    print("=" * 80)
    print("CURRENT BUDGET ALLOCATION")
    print("=" * 80)
    print()
    
    current_df = pd.DataFrame([
        {
            'channel': channel,
            'budget': budget,
            'share': budget / total_budget,
            'attribution': model.attributions.get(channel, 0),
            'gap': model.attributions.get(channel, 0) - (budget / total_budget)
        }
        for channel, budget in current_budget.items()
    ])
    current_df = current_df.sort_values('gap', ascending=False)
    
    print(current_df.to_string(index=False))
    print()
    
    # Identify undervalued channels
    print("=" * 80)
    print("UNDERVALUED CHANNELS")
    print("=" * 80)
    print()
    
    undervalued_df = model.identify_undervalued_channels(current_budget, threshold=0.03)
    
    if len(undervalued_df) > 0:
        print(f"Found {len(undervalued_df)} significantly undervalued channels:")
        print()
        print(undervalued_df.to_string(index=False))
        print()
        
        total_underval_pct = undervalued_df['undervaluation'].sum() * 100
        print(f"Total Undervaluation: {total_underval_pct:.1f}% of total budget")
        print(f"This represents ${total_budget * undervalued_df['undervaluation'].sum():,.0f} in misallocated funds")
    else:
        print("No significantly undervalued channels detected.")
    print()
    
    # Budget recommendations
    print("=" * 80)
    print("RECOMMENDED BUDGET REALLOCATION")
    print("=" * 80)
    print()
    
    allocation_df = model.recommend_budget_allocation(total_budget, current_budget)
    allocation_df = allocation_df.sort_values('budget_change', ascending=False)
    
    print(allocation_df[['channel', 'current_budget', 'recommended_budget', 
                         'budget_change', 'budget_change_pct']].to_string(index=False))
    print()
    
    # Calculate reallocation metrics
    increase_df = allocation_df[allocation_df['budget_change'] > 0]
    decrease_df = allocation_df[allocation_df['budget_change'] < 0]
    
    total_increase = increase_df['budget_change'].sum()
    total_decrease = abs(decrease_df['budget_change'].sum())
    reallocation_pct = total_increase / total_budget * 100
    
    print(f"Total Budget Shift: ${total_increase:,.0f} ({reallocation_pct:.1f}% of total budget)")
    print()
    
    print("Channels Gaining Budget:")
    for _, row in increase_df.iterrows():
        print(f"  • {row['channel']:15s}: +${row['budget_change']:7,.0f} ({row['budget_change_pct']:+6.1f}%)")
    print()
    
    print("Channels Losing Budget:")
    for _, row in decrease_df.iterrows():
        print(f"  • {row['channel']:15s}: ${row['budget_change']:8,.0f} ({row['budget_change_pct']:+6.1f}%)")
    print()
    
    # Key findings
    print("=" * 80)
    print("KEY FINDINGS & RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    most_effective = attribution_df.iloc[0]
    most_undervalued = undervalued_df.iloc[0] if len(undervalued_df) > 0 else None
    
    print(f"1. Most Effective Channel: {most_effective['channel']}")
    print(f"   Attribution: {most_effective['attribution']:.1%}")
    print(f"   This channel contributes most significantly to conversions.")
    print()
    
    if most_undervalued is not None:
        print(f"2. Most Undervalued Channel: {most_undervalued['channel']}")
        print(f"   Current Budget Share: {most_undervalued['current_budget_share']:.1%}")
        print(f"   Should Be: {most_undervalued['attribution_weight']:.1%}")
        print(f"   Recommended Increase: {most_undervalued['recommended_increase_pct']:.1f}%")
        print()
    
    print(f"3. Recommended Budget Reallocation: {reallocation_pct:.1f}%")
    print(f"   Moving ${total_increase:,.0f} from over-invested channels to undervalued ones")
    print(f"   This aligns budget with actual channel contribution to conversions.")
    print()
    
    if reallocation_pct >= 15:
        print(f"✓ This analysis supports a {reallocation_pct:.1f}% budget reallocation,")
        print(f"  meeting the objective of identifying channels for 15% budget shift.")
    else:
        print(f"  Note: Analysis suggests {reallocation_pct:.1f}% reallocation based on data.")
    print()
    
    # Generate summary visualization
    print("=" * 80)
    print("GENERATING SUMMARY REPORT")
    print("=" * 80)
    print()
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    fig = create_summary_report(model, current_budget)
    report_path = os.path.join(output_dir, 'advanced_attribution_report.png')
    fig.savefig(report_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Summary report saved to: {report_path}")
    print()
    
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("The Markov Chain attribution model has successfully:")
    print(f"  1. Analyzed {len(paths_df)} unique customer journey patterns")
    print(f"  2. Identified {len(undervalued_df)} undervalued marketing channels")
    print(f"  3. Recommended {reallocation_pct:.1f}% budget reallocation (${total_increase:,.0f})")
    print()
    print("This data-driven approach reveals channels that contribute significantly to")
    print("conversions but are underfunded, enabling more efficient marketing spend.")
    print()


if __name__ == '__main__':
    main()
