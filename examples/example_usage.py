"""
Example usage of the Markov Chain Attribution Model.

This script demonstrates how to:
1. Generate sample customer journey data
2. Fit the Markov attribution model
3. Analyze channel effectiveness
4. Identify undervalued channels
5. Recommend budget reallocation
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import matplotlib.pyplot as plt
from markov_attribution import MarkovAttribution
from data_generator import create_scenario_with_undervalued_channel
from visualization import (
    plot_attribution_comparison,
    plot_budget_allocation,
    plot_undervalued_channels,
    create_summary_report
)


def main():
    """Run the complete attribution analysis."""
    
    print("=" * 80)
    print("MULTI-TOUCH ATTRIBUTION MODEL - MARKOV CHAIN ANALYSIS")
    print("=" * 80)
    print()
    
    # Step 1: Generate sample data
    print("Step 1: Generating sample customer journey data...")
    paths_df, current_budget = create_scenario_with_undervalued_channel()
    print(f"Generated {len(paths_df)} unique customer journey paths")
    print(f"Total conversions: {paths_df['conversions'].sum()}")
    print(f"Total non-conversions: {paths_df['non_conversions'].sum()}")
    print()
    
    # Display sample paths
    print("Sample customer journey paths:")
    print(paths_df.head(10).to_string(index=False))
    print()
    
    # Step 2: Fit the Markov model
    print("Step 2: Fitting Markov Chain Attribution Model...")
    model = MarkovAttribution()
    model.fit(paths_df)
    print("Model fitted successfully!")
    print()
    
    # Step 3: Get attribution results
    print("=" * 80)
    print("ATTRIBUTION RESULTS")
    print("=" * 80)
    print()
    
    attribution_df = model.get_attribution_dataframe()
    print("Channel Attribution Weights and Removal Effects:")
    print(attribution_df.to_string(index=False))
    print()
    
    # Step 4: Analyze current budget allocation
    print("=" * 80)
    print("CURRENT BUDGET ALLOCATION")
    print("=" * 80)
    print()
    
    total_budget = sum(current_budget.values())
    print(f"Total Budget: ${total_budget:,.0f}")
    print()
    
    current_budget_df = pd.DataFrame([
        {'channel': channel, 'budget': budget, 'share': budget / total_budget}
        for channel, budget in current_budget.items()
    ]).sort_values('budget', ascending=False)
    
    print("Current Budget Distribution:")
    print(current_budget_df.to_string(index=False))
    print()
    
    # Step 5: Identify undervalued channels
    print("=" * 80)
    print("UNDERVALUED CHANNELS ANALYSIS")
    print("=" * 80)
    print()
    
    undervalued_df = model.identify_undervalued_channels(current_budget, threshold=0.03)
    
    if len(undervalued_df) > 0:
        print(f"Found {len(undervalued_df)} undervalued channels:")
        print()
        print(undervalued_df.to_string(index=False))
        print()
        
        # Calculate potential budget reallocation
        total_undervaluation = undervalued_df['undervaluation'].sum()
        print(f"Total undervaluation: {total_undervaluation:.1%}")
        print(f"This represents approximately ${total_budget * total_undervaluation:,.0f} in misallocated budget")
        print()
    else:
        print("No significantly undervalued channels identified.")
        print()
    
    # Step 6: Recommend budget reallocation
    print("=" * 80)
    print("RECOMMENDED BUDGET ALLOCATION")
    print("=" * 80)
    print()
    
    allocation_df = model.recommend_budget_allocation(total_budget, current_budget)
    print("Recommended Budget Changes:")
    print(allocation_df[['channel', 'current_budget', 'recommended_budget', 
                        'budget_change', 'budget_change_pct']].to_string(index=False))
    print()
    
    # Calculate total budget shift
    total_increase = allocation_df[allocation_df['budget_change'] > 0]['budget_change'].sum()
    total_decrease = abs(allocation_df[allocation_df['budget_change'] < 0]['budget_change'].sum())
    
    print(f"Total budget to reallocate: ${total_increase:,.0f} ({total_increase/total_budget:.1%} of total budget)")
    print()
    
    # Step 7: Key insights
    print("=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    print()
    
    # Most valuable channel
    top_channel = attribution_df.iloc[0]
    print(f"1. Most Valuable Channel: {top_channel['channel']}")
    print(f"   - Attribution Weight: {top_channel['attribution']:.1%}")
    print(f"   - Removal Effect: {top_channel['removal_effect']:.4f}")
    print()
    
    # Most undervalued
    if len(undervalued_df) > 0:
        most_undervalued = undervalued_df.iloc[0]
        print(f"2. Most Undervalued Channel: {most_undervalued['channel']}")
        print(f"   - Attribution Weight: {most_undervalued['attribution_weight']:.1%}")
        print(f"   - Current Budget Share: {most_undervalued['current_budget_share']:.1%}")
        print(f"   - Undervaluation: {most_undervalued['undervaluation']:.1%}")
        print()
    
    # Channels needing increase
    increase_channels = allocation_df[allocation_df['budget_change'] > 0]
    if len(increase_channels) > 0:
        print(f"3. Channels Needing Budget Increase:")
        for _, row in increase_channels.iterrows():
            print(f"   - {row['channel']}: {row['budget_change_pct']:+.1f}% "
                  f"(${row['budget_change']:+,.0f})")
        print()
    
    # Channels needing decrease
    decrease_channels = allocation_df[allocation_df['budget_change'] < 0]
    if len(decrease_channels) > 0:
        print(f"4. Channels Needing Budget Decrease:")
        for _, row in decrease_channels.iterrows():
            print(f"   - {row['channel']}: {row['budget_change_pct']:+.1f}% "
                  f"(${row['budget_change']:+,.0f})")
        print()
    
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print(f"The Markov Chain attribution model has identified {len(undervalued_df)} undervalued channels")
    print(f"that contributed to a recommended reallocation of {total_increase/total_budget:.1%} of the marketing budget.")
    print()
    print("This data-driven approach enables more efficient budget allocation based on")
    print("actual channel contribution to conversions rather than traditional last-click attribution.")
    print()
    
    # Step 8: Generate visualizations
    print("=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    print()
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Attribution comparison
    print("Creating attribution comparison plot...")
    fig1 = plot_attribution_comparison(attribution_df)
    fig1.savefig(os.path.join(output_dir, 'attribution_comparison.png'), 
                dpi=300, bbox_inches='tight')
    plt.close(fig1)
    
    # Budget allocation
    print("Creating budget allocation plot...")
    fig2 = plot_budget_allocation(allocation_df)
    fig2.savefig(os.path.join(output_dir, 'budget_allocation.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig2)
    
    # Undervalued channels
    if len(undervalued_df) > 0:
        print("Creating undervalued channels plot...")
        fig3 = plot_undervalued_channels(undervalued_df)
        fig3.savefig(os.path.join(output_dir, 'undervalued_channels.png'),
                    dpi=300, bbox_inches='tight')
        plt.close(fig3)
    
    # Summary report
    print("Creating comprehensive summary report...")
    fig4 = create_summary_report(model, current_budget)
    fig4.savefig(os.path.join(output_dir, 'summary_report.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig4)
    
    print()
    print(f"All visualizations saved to: {output_dir}/")
    print()
    
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
