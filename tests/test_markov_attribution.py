"""
Unit tests for Markov Chain Attribution Model.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import pandas as pd
import numpy as np
from markov_attribution import MarkovAttribution


class TestMarkovAttribution(unittest.TestCase):
    """Test cases for MarkovAttribution class."""
    
    def setUp(self):
        """Set up test data."""
        # Simple test data with 3 channels
        self.simple_data = pd.DataFrame([
            {'path': 'Channel A', 'conversions': 100, 'non_conversions': 100},
            {'path': 'Channel B', 'conversions': 50, 'non_conversions': 150},
            {'path': 'Channel C', 'conversions': 150, 'non_conversions': 50},
            {'path': 'Channel A > Channel B', 'conversions': 80, 'non_conversions': 120},
            {'path': 'Channel A > Channel C', 'conversions': 120, 'non_conversions': 80},
            {'path': 'Channel B > Channel C', 'conversions': 60, 'non_conversions': 140},
        ])
        
        self.model = MarkovAttribution()
    
    def test_model_initialization(self):
        """Test model initializes correctly."""
        self.assertIsInstance(self.model, MarkovAttribution)
        self.assertEqual(self.model.transition_matrix, {})
        self.assertEqual(self.model.removal_effects, {})
        self.assertEqual(self.model.attributions, {})
    
    def test_fit_method(self):
        """Test model fitting."""
        self.model.fit(self.simple_data)
        
        # Check that channels were extracted
        self.assertEqual(len(self.model.channels), 3)
        self.assertIn('Channel A', self.model.channels)
        self.assertIn('Channel B', self.model.channels)
        self.assertIn('Channel C', self.model.channels)
        
        # Check that transition matrix was built
        self.assertGreater(len(self.model.transition_matrix), 0)
        self.assertIn('start', self.model.transition_matrix)
        
        # Check that attributions were calculated
        self.assertEqual(len(self.model.attributions), 3)
    
    def test_attribution_sum_to_one(self):
        """Test that attribution weights sum to 1."""
        self.model.fit(self.simple_data)
        total_attribution = sum(self.model.attributions.values())
        self.assertAlmostEqual(total_attribution, 1.0, places=5)
    
    def test_get_attribution_dataframe(self):
        """Test getting attribution results as DataFrame."""
        self.model.fit(self.simple_data)
        df = self.model.get_attribution_dataframe()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertIn('channel', df.columns)
        self.assertIn('attribution', df.columns)
        self.assertIn('removal_effect', df.columns)
    
    def test_budget_allocation(self):
        """Test budget allocation recommendations."""
        self.model.fit(self.simple_data)
        
        total_budget = 10000
        current_allocation = {
            'Channel A': 5000,
            'Channel B': 3000,
            'Channel C': 2000
        }
        
        allocation_df = self.model.recommend_budget_allocation(
            total_budget, current_allocation
        )
        
        self.assertIsInstance(allocation_df, pd.DataFrame)
        self.assertEqual(len(allocation_df), 3)
        self.assertIn('recommended_budget', allocation_df.columns)
        
        # Check that total recommended budget equals input budget
        total_recommended = allocation_df['recommended_budget'].sum()
        self.assertAlmostEqual(total_recommended, total_budget, places=2)
    
    def test_identify_undervalued_channels(self):
        """Test identifying undervalued channels."""
        self.model.fit(self.simple_data)
        
        # Create allocation where Channel C is undervalued
        current_allocation = {
            'Channel A': 5000,
            'Channel B': 4000,
            'Channel C': 1000  # Likely undervalued given higher conversions
        }
        
        undervalued_df = self.model.identify_undervalued_channels(
            current_allocation, threshold=0.05
        )
        
        self.assertIsInstance(undervalued_df, pd.DataFrame)
        # At least check the structure is correct
        if len(undervalued_df) > 0:
            self.assertIn('channel', undervalued_df.columns)
            self.assertIn('undervaluation', undervalued_df.columns)
    
    def test_with_six_channels(self):
        """Test model with 6 channels as required."""
        channels = ['Social Media', 'Email', 'Paid Search', 
                   'Organic Search', 'Display Ads', 'Direct']
        
        # Create sample data with 6 channels
        data = []
        for i, channel in enumerate(channels):
            data.append({
                'path': channel,
                'conversions': 100 + i * 10,
                'non_conversions': 200 - i * 10
            })
        
        # Add some multi-touch paths
        data.append({
            'path': 'Social Media > Email > Direct',
            'conversions': 80,
            'non_conversions': 120
        })
        data.append({
            'path': 'Paid Search > Organic Search',
            'conversions': 90,
            'non_conversions': 110
        })
        
        df = pd.DataFrame(data)
        self.model.fit(df)
        
        # Verify all 6 channels are present
        self.assertEqual(len(self.model.channels), 6)
        for channel in channels:
            self.assertIn(channel, self.model.channels)
        
        # Verify attributions sum to 1
        total_attribution = sum(self.model.attributions.values())
        self.assertAlmostEqual(total_attribution, 1.0, places=5)
    
    def test_removal_effects(self):
        """Test that removal effects are calculated."""
        self.model.fit(self.simple_data)
        
        removal_effects = self.model.get_removal_effects()
        self.assertEqual(len(removal_effects), 3)
        
        # All channels should have removal effects
        for channel in self.model.channels:
            self.assertIn(channel, removal_effects)


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and edge cases."""
    
    def test_empty_data(self):
        """Test handling of edge cases."""
        model = MarkovAttribution()
        
        # Empty DataFrame
        empty_df = pd.DataFrame(columns=['path', 'conversions', 'non_conversions'])
        model.fit(empty_df)
        
        # Should handle gracefully
        self.assertEqual(len(model.channels), 0)
    
    def test_single_channel_data(self):
        """Test with single channel data."""
        model = MarkovAttribution()
        
        single_channel_df = pd.DataFrame([
            {'path': 'Only Channel', 'conversions': 100, 'non_conversions': 100}
        ])
        
        model.fit(single_channel_df)
        
        self.assertEqual(len(model.channels), 1)
        # Single channel should get all attribution
        self.assertAlmostEqual(
            model.attributions.get('Only Channel', 0), 1.0, places=5
        )


if __name__ == '__main__':
    unittest.main()
