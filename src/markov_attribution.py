"""
Markov Chain Attribution Model for Multi-Touch Marketing Attribution.

This module implements a Markov chain-based approach to calculate the contribution
of each marketing channel in customer conversion journeys.
"""

import numpy as np
import pandas as pd
from collections import defaultdict, Counter
from itertools import chain


class MarkovAttribution:
    """
    Markov Chain Attribution Model.
    
    This class implements a probabilistic attribution model that assigns credit
    to marketing channels based on their impact on conversion probability.
    """
    
    def __init__(self, conversion_rate_threshold=0.01):
        """
        Initialize the Markov Attribution Model.
        
        Args:
            conversion_rate_threshold: Minimum conversion rate difference to consider
        """
        self.conversion_rate_threshold = conversion_rate_threshold
        self.transition_matrix = {}
        self.removal_effects = {}
        self.attributions = {}
        self.channels = set()
        
    def fit(self, paths_df):
        """
        Fit the Markov model to customer journey data.
        
        Args:
            paths_df: DataFrame with columns ['path', 'conversions', 'non_conversions']
                     where 'path' is a string of channel sequence (e.g., "Channel1 > Channel2")
        
        Returns:
            self
        """
        # Parse paths and extract channels
        self.paths_df = paths_df.copy()
        self._extract_channels(paths_df)
        
        # Build transition matrix
        self._build_transition_matrix(paths_df)
        
        # Calculate removal effects
        self._calculate_removal_effects()
        
        # Calculate attributions
        self._calculate_attributions()
        
        return self
    
    def _extract_channels(self, paths_df):
        """Extract unique channels from all paths."""
        all_channels = set()
        for path in paths_df['path']:
            channels = [ch.strip() for ch in path.split('>')]
            all_channels.update(channels)
        
        # Remove special states
        self.channels = all_channels - {'start', 'conversion', 'null'}
        
    def _build_transition_matrix(self, paths_df):
        """
        Build transition probability matrix from paths.
        
        The matrix includes transitions between channels, from start to channels,
        and from channels to conversion/null states.
        """
        transitions = defaultdict(lambda: defaultdict(int))
        
        for _, row in paths_df.iterrows():
            path = row['path']
            conversions = row['conversions']
            non_conversions = row.get('non_conversions', 0)
            total_occurrences = conversions + non_conversions
            
            channels = [ch.strip() for ch in path.split('>')]
            
            # Add start state
            full_path = ['start'] + channels
            
            # For conversions, add conversion state
            if conversions > 0:
                conversion_path = full_path + ['conversion']
                for i in range(len(conversion_path) - 1):
                    transitions[conversion_path[i]][conversion_path[i + 1]] += conversions
            
            # For non-conversions, add null state
            if non_conversions > 0:
                non_conversion_path = full_path + ['null']
                for i in range(len(non_conversion_path) - 1):
                    transitions[non_conversion_path[i]][non_conversion_path[i + 1]] += non_conversions
        
        # Convert to probabilities
        self.transition_matrix = {}
        for from_state, to_states in transitions.items():
            total = sum(to_states.values())
            self.transition_matrix[from_state] = {
                to_state: count / total 
                for to_state, count in to_states.items()
            }
    
    def _calculate_conversion_probability(self, transition_matrix=None):
        """
        Calculate the probability of conversion given a transition matrix.
        
        Uses iterative approach to calculate probability of reaching conversion
        state from start state.
        """
        if transition_matrix is None:
            transition_matrix = self.transition_matrix
        
        # States that can still convert (excluding conversion and null)
        active_states = [s for s in transition_matrix.keys() 
                        if s not in ['conversion', 'null']]
        
        # Initialize probabilities
        prob = {'start': 1.0}
        for state in active_states:
            if state != 'start':
                prob[state] = 0.0
        
        conversion_prob = 0.0
        
        # Iterate until convergence
        max_iterations = 10000
        for iteration in range(max_iterations):
            new_prob = prob.copy()
            new_conversion_prob = conversion_prob
            
            for from_state in active_states:
                if prob[from_state] > 1e-10:  # Only process states with non-zero probability
                    if from_state in transition_matrix:
                        for to_state, trans_prob in transition_matrix[from_state].items():
                            contribution = prob[from_state] * trans_prob
                            
                            if to_state == 'conversion':
                                new_conversion_prob += contribution
                                new_prob[from_state] -= contribution
                            elif to_state == 'null':
                                new_prob[from_state] -= contribution
                            elif to_state in new_prob:
                                new_prob[to_state] += contribution
                                new_prob[from_state] -= contribution
            
            # Check convergence
            if abs(new_conversion_prob - conversion_prob) < 1e-10:
                break
            
            prob = new_prob
            conversion_prob = new_conversion_prob
        
        return conversion_prob
    
    def _calculate_removal_effects(self):
        """
        Calculate the removal effect for each channel.
        
        The removal effect is the difference in conversion probability when
        a channel is removed from the model.
        """
        # Calculate base conversion probability
        base_conversion_prob = self._calculate_conversion_probability()
        
        self.removal_effects = {}
        
        for channel in self.channels:
            # Create transition matrix with channel removed
            removed_matrix = self._remove_channel(channel)
            
            # Calculate conversion probability without this channel
            removed_conversion_prob = self._calculate_conversion_probability(removed_matrix)
            
            # Removal effect is the difference
            self.removal_effects[channel] = base_conversion_prob - removed_conversion_prob
    
    def _remove_channel(self, channel_to_remove):
        """
        Create a new transition matrix with a specific channel removed.
        
        When a channel is removed, we redistribute its incoming transitions
        to its outgoing transitions.
        """
        removed_matrix = defaultdict(dict)
        
        # Copy all transitions except those involving the removed channel
        for from_state, transitions in self.transition_matrix.items():
            if from_state == channel_to_remove:
                continue
            
            for to_state, prob in transitions.items():
                if to_state == channel_to_remove:
                    # Redistribute this transition through the removed channel
                    if channel_to_remove in self.transition_matrix:
                        for next_state, next_prob in self.transition_matrix[channel_to_remove].items():
                            if next_state != channel_to_remove:
                                if from_state not in removed_matrix:
                                    removed_matrix[from_state] = {}
                                removed_matrix[from_state][next_state] = (
                                    removed_matrix[from_state].get(next_state, 0) + prob * next_prob
                                )
                else:
                    if from_state not in removed_matrix:
                        removed_matrix[from_state] = {}
                    removed_matrix[from_state][to_state] = (
                        removed_matrix[from_state].get(to_state, 0) + prob
                    )
        
        # Normalize probabilities
        for from_state in removed_matrix:
            total = sum(removed_matrix[from_state].values())
            if total > 0:
                for to_state in removed_matrix[from_state]:
                    removed_matrix[from_state][to_state] /= total
        
        return dict(removed_matrix)
    
    def _calculate_attributions(self):
        """
        Calculate attribution weights for each channel.
        
        Attribution is normalized removal effect (ensures sum to 1).
        """
        total_removal_effect = sum(max(0, effect) for effect in self.removal_effects.values())
        
        if total_removal_effect > 0:
            self.attributions = {
                channel: max(0, effect) / total_removal_effect
                for channel, effect in self.removal_effects.items()
            }
        else:
            # If no positive effects, distribute equally
            self.attributions = {
                channel: 1.0 / len(self.channels)
                for channel in self.channels
            }
    
    def get_attributions(self):
        """
        Get attribution weights for each channel.
        
        Returns:
            dict: Channel names mapped to their attribution weights (sum to 1)
        """
        return self.attributions
    
    def get_removal_effects(self):
        """
        Get removal effects for each channel.
        
        Returns:
            dict: Channel names mapped to their removal effects
        """
        return self.removal_effects
    
    def get_attribution_dataframe(self):
        """
        Get attribution results as a pandas DataFrame.
        
        Returns:
            DataFrame with columns: channel, attribution, removal_effect
        """
        df = pd.DataFrame([
            {
                'channel': channel,
                'attribution': self.attributions.get(channel, 0),
                'removal_effect': self.removal_effects.get(channel, 0)
            }
            for channel in self.channels
        ])
        
        return df.sort_values('attribution', ascending=False).reset_index(drop=True)
    
    def recommend_budget_allocation(self, total_budget, current_allocation=None):
        """
        Recommend budget allocation based on attribution weights.
        
        Args:
            total_budget: Total marketing budget to allocate
            current_allocation: Optional dict of current budget allocation by channel
        
        Returns:
            DataFrame with recommended allocation and comparison to current
        """
        recommended = {}
        for channel, attribution in self.attributions.items():
            recommended[channel] = total_budget * attribution
        
        results = []
        for channel in self.channels:
            row = {
                'channel': channel,
                'attribution_weight': self.attributions.get(channel, 0),
                'recommended_budget': recommended.get(channel, 0)
            }
            
            if current_allocation and channel in current_allocation:
                row['current_budget'] = current_allocation[channel]
                row['budget_change'] = recommended[channel] - current_allocation[channel]
                row['budget_change_pct'] = (
                    (recommended[channel] - current_allocation[channel]) / 
                    current_allocation[channel] * 100
                    if current_allocation[channel] > 0 else 0
                )
            
            results.append(row)
        
        df = pd.DataFrame(results)
        return df.sort_values('recommended_budget', ascending=False).reset_index(drop=True)
    
    def identify_undervalued_channels(self, current_allocation, threshold=0.05):
        """
        Identify channels that are undervalued based on current budget allocation.
        
        Args:
            current_allocation: Dict of current budget allocation by channel
            threshold: Minimum difference between attribution and budget share to flag
        
        Returns:
            DataFrame of undervalued channels
        """
        total_current = sum(current_allocation.values())
        undervalued = []
        
        for channel in self.channels:
            attribution = self.attributions.get(channel, 0)
            current_share = current_allocation.get(channel, 0) / total_current
            
            # Channel is undervalued if attribution > current budget share
            if attribution - current_share > threshold:
                undervalued.append({
                    'channel': channel,
                    'attribution_weight': attribution,
                    'current_budget_share': current_share,
                    'undervaluation': attribution - current_share,
                    'recommended_increase_pct': (attribution - current_share) / current_share * 100
                        if current_share > 0 else float('inf')
                })
        
        df = pd.DataFrame(undervalued)
        if len(df) > 0:
            return df.sort_values('undervaluation', ascending=False).reset_index(drop=True)
        return df
