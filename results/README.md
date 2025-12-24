# Results Directory

This directory contains visualizations and analysis outputs generated during the development of the Agent League System.

## Token Consumption Visualizations

### token_consumption.png
Comprehensive token usage analysis showing:
- **Left Chart**: Stacked bar chart of input vs output tokens by development phase
- **Right Chart**: Pie chart showing token distribution across phases
- **Summary**: Total tokens, costs, and breakdown

**Key Findings**:
- Total Development Tokens: ~890,000
- Estimated Cost: $7-10 USD
- TaskLoop phase consumed 73% of tokens (650K tokens, 120 agent invocations)
- PreProject and ReleaseGate phases: 9% and 18% respectively

### token_timeline.png
Timeline view showing:
- Token consumption by phase in chronological order
- Agent invocation counts per phase
- Relative effort distribution across development lifecycle

## Generation

To regenerate these visualizations:

```bash
python scripts/generate_token_visualization.py
```

## Data Sources

Token estimates based on:
- Development activity logged in `docs/development/PROMPT_LOG.md`
- Agent invocation counts from orchestration workflow
- Estimated context window sizes per phase
- Output/input ratio of approximately 60%

## Cost Assumptions

Pricing based on Claude Sonnet 4.5 (verify current rates):
- Input tokens: $3.00 per 1M tokens
- Output tokens: $15.00 per 1M tokens

See `docs/COSTS.md` for detailed cost analysis.

## Notes

- Visualizations are high-resolution (300 DPI) for publication quality
- Generated using matplotlib
- Token estimates are approximations based on typical usage patterns
- Actual costs may vary based on specific usage and caching effectiveness
