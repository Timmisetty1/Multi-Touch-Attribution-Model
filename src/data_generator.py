"""
Data generation utilities for creating sample marketing attribution data.
"""

import numpy as np
import pandas as pd
from itertools import combinations, permutations


def generate_sample_data(num_paths=1000, channels=None, seed=42):
    """
    Generate sample customer journey data for attribution modeling.
    
    Args:
        num_paths: Number of unique path patterns to generate
        channels: List of channel names (default: 6 channels)
        seed: Random seed for reproducibility
    
    Returns:
        DataFrame with columns: path, conversions, non_conversions
    """
    np.random.seed(seed)
    
    if channels is None:
        channels = [
            'Social Media',
            'Email',
            'Paid Search',
            'Organic Search',
            'Display Ads',
            'Direct'
        ]
    
    paths = []
    
    # Generate various path patterns
    for _ in range(num_paths):
        # Random path length between 1 and 5
        path_length = np.random.randint(1, 6)
        
        # Select random channels with replacement
        selected_channels = np.random.choice(channels, size=path_length, replace=True)
        
        # Create path string
        path = ' > '.join(selected_channels)
        
        # Simulate conversions and non-conversions
        # Some channels are more effective (simulated)
        effectiveness = {
            'Social Media': 0.12,
            'Email': 0.18,
            'Paid Search': 0.15,
            'Organic Search': 0.20,
            'Display Ads': 0.08,
            'Direct': 0.25
        }
        
        # Calculate path conversion probability based on channels
        base_prob = 0.05
        for channel in selected_channels:
            base_prob += effectiveness.get(channel, 0.1) / path_length
        
        base_prob = min(base_prob, 0.9)  # Cap at 90%
        
        # Number of times this path was observed
        occurrences = np.random.randint(10, 200)
        
        # Split into conversions and non-conversions
        conversions = int(occurrences * base_prob)
        non_conversions = occurrences - conversions
        
        paths.append({
            'path': path,
            'conversions': conversions,
            'non_conversions': non_conversions
        })
    
    # Create DataFrame and aggregate duplicate paths
    df = pd.DataFrame(paths)
    df = df.groupby('path').agg({
        'conversions': 'sum',
        'non_conversions': 'sum'
    }).reset_index()
    
    return df


def generate_realistic_journeys(num_journeys=5000, channels=None, seed=42):
    """
    Generate more realistic customer journey data with common patterns.
    
    Args:
        num_journeys: Number of customer journeys to generate
        channels: List of channel names
        seed: Random seed
    
    Returns:
        DataFrame with path data
    """
    np.random.seed(seed)
    
    if channels is None:
        channels = [
            'Social Media',
            'Email',
            'Paid Search',
            'Organic Search',
            'Display Ads',
            'Direct'
        ]
    
    # Common journey patterns with weights
    patterns = [
        (['Organic Search'], 0.15),
        (['Direct'], 0.12),
        (['Social Media', 'Organic Search'], 0.10),
        (['Paid Search', 'Direct'], 0.08),
        (['Display Ads', 'Social Media', 'Organic Search'], 0.07),
        (['Email', 'Direct'], 0.06),
        (['Organic Search', 'Direct'], 0.08),
        (['Paid Search', 'Organic Search', 'Direct'], 0.06),
        (['Social Media', 'Email', 'Direct'], 0.05),
        (['Display Ads', 'Paid Search'], 0.04),
        (['Email'], 0.05),
        (['Social Media'], 0.04),
        (['Paid Search'], 0.05),
        (['Display Ads'], 0.03),
    ]
    
    # Conversion rates for patterns ending with specific channels
    conversion_boosts = {
        'Direct': 0.15,
        'Email': 0.12,
        'Organic Search': 0.10,
        'Paid Search': 0.08,
        'Social Media': 0.06,
        'Display Ads': 0.05
    }
    
    journeys = []
    
    for _ in range(num_journeys):
        # Select a pattern
        pattern_weights = [w for _, w in patterns]
        pattern_idx = np.random.choice(len(patterns), p=np.array(pattern_weights) / sum(pattern_weights))
        pattern, _ = patterns[pattern_idx]
        
        # Create path
        path = ' > '.join(pattern)
        
        # Calculate conversion probability
        base_conversion = 0.05
        last_channel = pattern[-1]
        base_conversion += conversion_boosts.get(last_channel, 0.05)
        base_conversion += len(pattern) * 0.02  # Longer journeys have slightly higher conversion
        base_conversion = min(base_conversion, 0.95)
        
        # Determine if conversion
        converted = np.random.random() < base_conversion
        
        journeys.append({
            'path': path,
            'conversions': 1 if converted else 0,
            'non_conversions': 0 if converted else 1
        })
    
    # Aggregate
    df = pd.DataFrame(journeys)
    df = df.groupby('path').agg({
        'conversions': 'sum',
        'non_conversions': 'sum'
    }).reset_index()
    
    return df


def create_scenario_with_undervalued_channel(seed=42):
    """
    Create a scenario where specific channels are undervalued.
    
    This simulates a situation where certain channels (like Email and Organic Search)
    are highly effective but receive less budget.
    
    Returns:
        tuple: (paths_df, current_budget_allocation)
    """
    np.random.seed(seed)
    
    channels = ['Social Media', 'Email', 'Paid Search', 'Organic Search', 'Display Ads', 'Direct']
    
    # Generate data where Email and Organic Search are highly effective
    paths_df = generate_realistic_journeys(num_journeys=8000, channels=channels, seed=seed)
    
    # Current budget allocation (reflecting typical over-investment in paid channels)
    current_budget = {
        'Social Media': 15000,
        'Email': 8000,  # Undervalued
        'Paid Search': 30000,  # Over-invested
        'Organic Search': 12000,  # Undervalued
        'Display Ads': 25000,  # Over-invested
        'Direct': 10000
    }
    
    return paths_df, current_budget
