# Multi-Touch Attribution Model

A sophisticated **Markov Chain-based attribution model** for measuring marketing channel effectiveness across multiple touchpoints. This model identifies undervalued channels and provides data-driven recommendations for optimal budget allocation.

## Overview

Traditional last-click attribution models fail to capture the true contribution of all marketing channels in a customer's journey. This project implements a **Markov Chain attribution model** that:

- Measures the true effectiveness of each marketing channel
- Identifies undervalued channels receiving insufficient budget
- Recommends optimal budget reallocation based on channel contribution
- Supports analysis across 6 marketing channels (customizable)
- Uses probabilistic modeling to calculate channel removal effects

## Key Features

- **Markov Chain Attribution**: Probabilistic model that calculates each channel's contribution to conversions
- **Removal Effect Analysis**: Measures the impact of removing each channel from the customer journey
- **Undervalued Channel Identification**: Automatically identifies channels that deserve more budget
- **Budget Reallocation Recommendations**: Data-driven suggestions for reallocating marketing spend
- **Comprehensive Visualizations**: Professional charts and reports for stakeholder communication
- **Flexible Data Input**: Works with various customer journey data formats

## Installation 

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Timmisetty1/Multi-Touch-Attribution-Model.git
cd Multi-Touch-Attribution-Model
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Running the Examples

#### 1. Basic Example
The easiest way to get started is to run the basic example script:

```bash
python examples/example_usage.py
```

This will:
1. Generate sample customer journey data with 6 marketing channels
2. Fit the Markov Chain attribution model
3. Analyze channel effectiveness
4. Identify undervalued channels
5. Recommend budget reallocation
6. Generate comprehensive visualizations

#### 2. Advanced Example (Realistic Scenario)
For a more realistic scenario demonstrating 15%+ budget reallocation:

```bash
python examples/advanced_example.py
```

This uses realistic customer journey data showing how undervalued channels like Email and Organic Search can be identified for significant budget increases.

#### 3. Interactive Jupyter Notebook
For an interactive analysis experience:

```bash
jupyter notebook examples/attribution_analysis.ipynb
```

The notebook provides step-by-step guidance through the entire attribution analysis process.

### Using the Model with Your Data

```python
from src.markov_attribution import MarkovAttribution
import pandas as pd

# Prepare your data in the required format
# Each row represents a unique customer journey path
data = pd.DataFrame({
    'path': [
        'Social Media > Email > Direct',
        'Paid Search > Direct',
        'Organic Search',
        'Display Ads > Social Media > Organic Search > Direct'
    ],
    'conversions': [45, 120, 200, 30],
    'non_conversions': [105, 80, 150, 70]
})

# Initialize and fit the model
model = MarkovAttribution()
model.fit(data)

# Get attribution results
attribution_df = model.get_attribution_dataframe()
print(attribution_df)

# Identify undervalued channels
current_budget = {
    'Social Media': 15000,
    'Email': 8000,
    'Paid Search': 30000,
    'Organic Search': 12000,
    'Display Ads': 25000,
    'Direct': 10000
}

undervalued = model.identify_undervalued_channels(current_budget, threshold=0.03)
print(undervalued)

# Get budget recommendations
total_budget = sum(current_budget.values())
recommendations = model.recommend_budget_allocation(total_budget, current_budget)
print(recommendations)
```

## Data Format

The model expects customer journey data in the following format:

| path | conversions | non_conversions |
|------|-------------|-----------------|
| Channel A > Channel B > Channel C | 45 | 105 |
| Channel B > Channel C | 120 | 80 |
| Channel A | 200 | 150 |

- **path**: String representing the sequence of marketing channels, separated by " > "
- **conversions**: Number of conversions that followed this path
- **non_conversions**: Number of times this path occurred without conversion

## Project Structure

```
Multi-Touch-Attribution-Model/
├── src/
│   ├── __init__.py
│   ├── markov_attribution.py    # Core Markov Chain model
│   ├── data_generator.py        # Sample data generation utilities
│   └── visualization.py         # Plotting and reporting functions
├── examples/
│   ├── example_usage.py         # Basic example workflow
│   ├── advanced_example.py      # Advanced realistic scenario
│   └── attribution_analysis.ipynb  # Interactive Jupyter notebook
├── tests/
│   ├── __init__.py
│   └── test_markov_attribution.py  # Unit tests
├── data/
│   └── (your data files)
├── output/
│   └── (generated visualizations)
├── requirements.txt
└── README.md
```

## Testing

Run the test suite to validate the implementation:

```bash
python -m unittest discover tests/ -v
```

All tests should pass, covering:
- Model initialization and fitting
- Attribution weight calculations
- Budget allocation recommendations
- Undervalued channel identification
- Edge cases and data integrity

## Methodology

### Markov Chain Attribution

The Markov Chain attribution model works by:

1. **Building a Transition Matrix**: Analyzes customer journeys to calculate probabilities of moving from one channel to another
2. **Calculating Removal Effects**: For each channel, calculates the change in conversion probability when that channel is removed
3. **Computing Attribution Weights**: Normalizes removal effects to create attribution weights that sum to 1
4. **Identifying Undervalued Channels**: Compares attribution weights to current budget allocation

### Key Metrics

- **Attribution Weight**: The proportion of credit a channel receives (sums to 1 across all channels)
- **Removal Effect**: The decrease in conversion probability when a channel is removed
- **Undervaluation**: The difference between attribution weight and current budget share

## Example Results

When running the example script, you'll get:

### Attribution Analysis
```
Channel Attribution Weights and Removal Effects:
         channel  attribution  removal_effect
  Organic Search       0.2845          0.0421
          Direct       0.2234          0.0330
           Email       0.1923          0.0284
    Paid Search        0.1456          0.0215
   Social Media        0.1098          0.0162
    Display Ads        0.0444          0.0066
```

### Undervalued Channels
```
Found 2 undervalued channels:

         channel  attribution_weight  current_budget_share  undervaluation
           Email              0.1923                0.0800          0.1123
  Organic Search              0.2845                0.1200          0.1645
```

### Budget Recommendations
```
Total budget to reallocate: $15,000 (15.0% of total budget)

Channels Needing Budget Increase:
   - Email: +140.4% (+$11,233)
   - Organic Search: +137.1% (+$16,453)

Channels Needing Budget Decrease:
   - Paid Search: -51.5% (-$15,437)
   - Display Ads: -82.2% (-$20,549)
```

## Visualizations

The model generates several visualizations:

1. **Attribution Comparison**: Bar charts showing attribution weights and removal effects
2. **Budget Allocation**: Comparison of current vs. recommended budget
3. **Undervalued Channels**: Analysis of channels needing budget increases
4. **Summary Report**: Comprehensive dashboard with all key metrics

All visualizations are saved to the `output/` directory.

## Use Cases

This model is ideal for:

- **Marketing Teams**: Optimize budget allocation across channels
- **Data Analysts**: Understand multi-touch customer journeys
- **CMOs/Marketing Directors**: Make data-driven investment decisions
- **Performance Marketers**: Identify high-ROI channels
- **Digital Agencies**: Provide attribution analysis to clients

## Advantages Over Other Models

| Model Type | Limitations | Markov Chain Advantages |
|------------|-------------|------------------------|
| Last-Click | Only credits final touchpoint | Credits all touchpoints proportionally |
| First-Click | Ignores nurturing channels | Considers entire customer journey |
| Linear | Equal credit to all channels | Weighs channels by actual impact |
| Time-Decay | Arbitrary decay function | Data-driven probability model |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Contact

For questions or feedback, please open an issue on GitHub.

## Acknowledgments

This implementation is based on research in probabilistic attribution modeling and Markov chain analysis applied to marketing analytics.
