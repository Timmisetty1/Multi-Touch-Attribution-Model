"""
Visualization utilities for attribution analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def plot_attribution_comparison(attributions_df, figsize=(12, 6)):
    """
    Plot attribution weights and removal effects for all channels.
    
    Args:
        attributions_df: DataFrame from MarkovAttribution.get_attribution_dataframe()
        figsize: Figure size tuple
    
    Returns:
        matplotlib figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Plot attribution weights
    sns.barplot(data=attributions_df, x='attribution', y='channel', 
                hue='channel', palette='viridis', ax=ax1, legend=False)
    ax1.set_title('Channel Attribution Weights', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Attribution Weight', fontsize=12)
    ax1.set_ylabel('Channel', fontsize=12)
    
    # Add percentage labels
    for i, row in attributions_df.iterrows():
        ax1.text(row['attribution'], i, f" {row['attribution']:.1%}", 
                va='center', fontsize=10)
    
    # Plot removal effects
    sns.barplot(data=attributions_df, x='removal_effect', y='channel',
                hue='channel', palette='magma', ax=ax2, legend=False)
    ax2.set_title('Channel Removal Effects', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Removal Effect', fontsize=12)
    ax2.set_ylabel('', fontsize=12)
    
    # Add value labels
    for i, row in attributions_df.iterrows():
        ax2.text(row['removal_effect'], i, f" {row['removal_effect']:.4f}",
                va='center', fontsize=10)
    
    plt.tight_layout()
    return fig


def plot_budget_allocation(allocation_df, figsize=(14, 6)):
    """
    Plot current vs recommended budget allocation.
    
    Args:
        allocation_df: DataFrame from MarkovAttribution.recommend_budget_allocation()
        figsize: Figure size tuple
    
    Returns:
        matplotlib figure
    """
    if 'current_budget' not in allocation_df.columns:
        # Only recommended budget available
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=allocation_df, x='recommended_budget', y='channel',
                   hue='channel', palette='viridis', ax=ax, legend=False)
        ax.set_title('Recommended Budget Allocation', fontsize=14, fontweight='bold')
        ax.set_xlabel('Recommended Budget ($)', fontsize=12)
        ax.set_ylabel('Channel', fontsize=12)
        
        for i, row in allocation_df.iterrows():
            ax.text(row['recommended_budget'], i, 
                   f" ${row['recommended_budget']:,.0f}",
                   va='center', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    # Comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Current vs Recommended
    comparison_df = allocation_df[['channel', 'current_budget', 'recommended_budget']].copy()
    comparison_df = comparison_df.melt(id_vars='channel', var_name='Budget Type', 
                                       value_name='Budget')
    
    sns.barplot(data=comparison_df, x='Budget', y='channel', hue='Budget Type',
               palette={'current_budget': 'lightcoral', 'recommended_budget': 'lightgreen'},
               ax=ax1)
    ax1.set_title('Current vs Recommended Budget', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Budget ($)', fontsize=12)
    ax1.set_ylabel('Channel', fontsize=12)
    ax1.legend(title='Budget Type', labels=['Current', 'Recommended'])
    
    # Budget change percentage
    change_df = allocation_df[allocation_df['budget_change_pct'] != 0].copy()
    colors = ['green' if x > 0 else 'red' for x in change_df['budget_change_pct']]
    
    sns.barplot(data=change_df, x='budget_change_pct', y='channel',
               hue='channel', palette=colors, ax=ax2, legend=False)
    ax2.set_title('Recommended Budget Change', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Change (%)', fontsize=12)
    ax2.set_ylabel('', fontsize=12)
    ax2.axvline(x=0, color='black', linestyle='--', linewidth=1)
    
    # Add percentage labels
    for i, row in change_df.iterrows():
        ax2.text(row['budget_change_pct'], i, 
                f" {row['budget_change_pct']:+.1f}%",
                va='center', fontsize=10)
    
    plt.tight_layout()
    return fig


def plot_undervalued_channels(undervalued_df, figsize=(12, 6)):
    """
    Plot undervalued channels analysis.
    
    Args:
        undervalued_df: DataFrame from MarkovAttribution.identify_undervalued_channels()
        figsize: Figure size tuple
    
    Returns:
        matplotlib figure
    """
    if len(undervalued_df) == 0:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, 'No undervalued channels identified',
               ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Attribution vs Current Budget Share
    x = np.arange(len(undervalued_df))
    width = 0.35
    
    ax1.bar(x - width/2, undervalued_df['current_budget_share'], width,
           label='Current Budget Share', color='lightcoral')
    ax1.bar(x + width/2, undervalued_df['attribution_weight'], width,
           label='Attribution Weight', color='lightgreen')
    
    ax1.set_xlabel('Channel', fontsize=12)
    ax1.set_ylabel('Share/Weight', fontsize=12)
    ax1.set_title('Undervalued Channels: Attribution vs Budget', 
                 fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(undervalued_df['channel'], rotation=45, ha='right')
    ax1.legend()
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    
    # Undervaluation magnitude
    sns.barplot(data=undervalued_df, x='undervaluation', y='channel',
               hue='channel', palette='Reds_r', ax=ax2, legend=False)
    ax2.set_title('Undervaluation Magnitude', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Undervaluation (Attribution - Budget Share)', fontsize=12)
    ax2.set_ylabel('', fontsize=12)
    
    # Add labels
    for i, row in undervalued_df.iterrows():
        ax2.text(row['undervaluation'], i, f" {row['undervaluation']:.1%}",
                va='center', fontsize=10)
    
    plt.tight_layout()
    return fig


def create_summary_report(model, current_budget=None, save_path=None):
    """
    Create a comprehensive summary report with all key visualizations.
    
    Args:
        model: Fitted MarkovAttribution model
        current_budget: Optional dict of current budget allocation
        save_path: Optional path to save the report figure
    
    Returns:
        matplotlib figure
    """
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Get data
    attr_df = model.get_attribution_dataframe()
    
    # Plot 1: Attribution weights
    ax1 = fig.add_subplot(gs[0, 0])
    sns.barplot(data=attr_df, x='attribution', y='channel', 
                hue='channel', palette='viridis', ax=ax1, legend=False)
    ax1.set_title('Channel Attribution Weights', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Attribution Weight')
    for i, row in attr_df.iterrows():
        ax1.text(row['attribution'], i, f" {row['attribution']:.1%}", 
                va='center', fontsize=9)
    
    # Plot 2: Removal effects
    ax2 = fig.add_subplot(gs[0, 1])
    sns.barplot(data=attr_df, x='removal_effect', y='channel',
                hue='channel', palette='magma', ax=ax2, legend=False)
    ax2.set_title('Channel Removal Effects', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Removal Effect')
    ax2.set_ylabel('')
    
    # Plot 3 & 4: Budget allocation if available
    if current_budget is not None:
        total_budget = sum(current_budget.values())
        alloc_df = model.recommend_budget_allocation(total_budget, current_budget)
        
        ax3 = fig.add_subplot(gs[1, :])
        comparison_df = alloc_df[['channel', 'current_budget', 'recommended_budget']].copy()
        comparison_df = comparison_df.melt(id_vars='channel', var_name='Budget Type', 
                                          value_name='Budget')
        
        sns.barplot(data=comparison_df, x='Budget', y='channel', hue='Budget Type',
                   palette={'current_budget': 'lightcoral', 'recommended_budget': 'lightgreen'},
                   ax=ax3)
        ax3.set_title('Current vs Recommended Budget Allocation', fontsize=12, fontweight='bold')
        ax3.legend(title='', labels=['Current', 'Recommended'])
        
        # Plot 5: Undervalued channels
        undervalued_df = model.identify_undervalued_channels(current_budget)
        if len(undervalued_df) > 0:
            ax4 = fig.add_subplot(gs[2, :])
            sns.barplot(data=undervalued_df, x='undervaluation', y='channel',
                       hue='channel', palette='Reds_r', ax=ax4, legend=False)
            ax4.set_title('Undervalued Channels (Need Budget Increase)', 
                         fontsize=12, fontweight='bold')
            ax4.set_xlabel('Undervaluation (Attribution - Budget Share)')
            
            for i, row in undervalued_df.iterrows():
                ax4.text(row['undervaluation'], i, f" {row['undervaluation']:.1%}",
                        va='center', fontsize=9)
    
    fig.suptitle('Multi-Touch Attribution Model - Markov Chain Analysis', 
                fontsize=16, fontweight='bold', y=0.995)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig
