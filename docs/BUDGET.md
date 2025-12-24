# Budget Plan - Agent League System

## Document Overview

This document outlines the budget planning, monitoring controls, and cost management strategies for the Agent League System.

**Project**: Agent League System (AIAgents3997-HW7)
**Last Updated**: December 24, 2025
**Budget Period**: Development + First Year Production

---

## Development Budget

### Actual Development Costs

| Category | Amount | Status |
|----------|--------|--------|
| LLM API Costs (Development) | $7-10 USD | ✅ Complete |
| Infrastructure (Local) | $0 | ✅ Free |
| **Total Development** | **$7-10 USD** | **✅ Under Budget** |

### Development Budget Allocation

- **Planned**: $50 USD
- **Actual**: $7-10 USD
- **Remaining**: $40-43 USD (80-86% under budget)
- **Status**: ✅ Significantly under budget

---

## Production Budget

### Base Infrastructure Costs

The Agent League System core components have **$0 ongoing LLM costs**:
- League Manager: Pure Python logic
- Referee system: Rule-based game execution
- Player framework: Strategy-based (no AI required)

**Monthly baseline**: $0 USD

### Optional AI Player Costs

If deploying AI-powered player strategies:

#### Budget Scenarios

| Scenario | Description | Monthly Games | Est. Monthly Cost |
|----------|-------------|---------------|-------------------|
| **Development/Testing** | Local testing and development | 100-500 | $0.50 - $2.50 |
| **Small Tournament** | Weekly small tournaments | 1,000 | $4.50 - $18.00 |
| **Medium Usage** | Daily tournaments or testing | 5,000 | $22.50 - $90.00 |
| **Heavy Usage** | Large-scale competitions | 10,000+ | $45.00 - $180.00 |

### Recommended Budget Allocation

| Usage Level | Monthly Budget | Annual Budget | Notes |
|-------------|----------------|---------------|-------|
| **Development** | $10 USD | $120 USD | Covers testing and experiments |
| **Production (Light)** | $25 USD | $300 USD | Small tournaments and demos |
| **Production (Medium)** | $100 USD | $1,200 USD | Regular competitive play |
| **Production (Heavy)** | $200 USD | $2,400 USD | Large-scale competitions |

---

## Cost Monitoring and Controls

### Monitoring Thresholds

Set up alerts at these thresholds:

| Alert Level | Daily Spend | Weekly Spend | Monthly Spend | Action |
|-------------|-------------|--------------|---------------|--------|
| **Info** | $1 | $5 | $20 | Log and review |
| **Warning** | $5 | $25 | $100 | Notify team, review usage |
| **Critical** | $10 | $50 | $200 | Halt AI players, investigate |
| **Emergency** | $20 | $100 | $500 | Full stop, require approval |

### Implementation

#### 1. Anthropic Console Alerts

```bash
# Set up budget alerts in Anthropic Console:
# 1. Navigate to: console.anthropic.com → Settings → Billing
# 2. Configure alerts:
#    - Warning at $25/month
#    - Critical at $100/month
#    - Email: team@example.com
```

#### 2. Application-Level Token Tracking

Add token counting to AI player strategies:

```python
# In src/player/ai_strategy.py (if implemented)
class AIPlayerStrategy:
    def __init__(self, monthly_token_budget: int = 1_000_000):
        self.token_budget = monthly_token_budget
        self.tokens_used_this_month = 0

    def make_move(self, game_state):
        if self.tokens_used_this_month >= self.token_budget:
            raise BudgetExceededError("Monthly token budget exceeded")

        # Make API call, track tokens
        response = anthropic_client.messages.create(...)
        self.tokens_used_this_month += (
            response.usage.input_tokens +
            response.usage.output_tokens
        )

        return move
```

#### 3. Cost Dashboard

Create monitoring dashboard:

```python
# scripts/cost_monitor.py
def generate_cost_report():
    """Generate daily/weekly/monthly cost reports"""
    return {
        "daily_spend": calculate_daily_cost(),
        "weekly_spend": calculate_weekly_cost(),
        "monthly_spend": calculate_monthly_cost(),
        "tokens_used": get_token_usage(),
        "budget_remaining": get_remaining_budget(),
        "projected_monthly": project_monthly_cost(),
    }
```

---

## Budget Control Mechanisms

### 1. Token Budgets per Component

Set maximum tokens per component:

| Component | Tokens/Month | Rationale |
|-----------|--------------|-----------|
| AI Player (per instance) | 100,000 | ~200 games with simple strategy |
| Tournament System | 500,000 | Large tournament analysis |
| **Total Application** | **1,000,000** | ~$3-15/month depending on model |

### 2. Rate Limiting

Implement rate limits to prevent runaway costs:

```python
# Rate limit configuration
MAX_TOKENS_PER_GAME = 10_000
MAX_TOKENS_PER_PLAYER_PER_DAY = 50_000
MAX_CONCURRENT_AI_PLAYERS = 10
```

### 3. Model Tiering

Use appropriate model for task complexity:

| Task | Recommended Model | Cost Multiplier |
|------|------------------|-----------------|
| Simple moves | Claude Haiku | 1x (baseline) |
| Strategic analysis | Claude Sonnet | 12x |
| Complex reasoning | Claude Opus | 60x |

**Budget tip**: Default to Haiku, escalate only when needed.

### 4. Caching Strategy

Leverage prompt caching to reduce costs:

```python
# Use caching for repeated context
system_prompt = """
You are playing tic-tac-toe. Rules:
[...detailed rules...]
"""  # Cache this - same for every game

# Cache key game state representations
# Reuse across similar positions
```

**Potential savings**: 50-90% for repeated contexts

---

## Cost Scenarios and Projections

### Scenario 1: Pure Development (No AI)

- **Monthly cost**: $0
- **Use case**: Development, testing with rule-based players
- **Recommendation**: Default mode for most users

### Scenario 2: AI Player Experimentation

- **Monthly cost**: $5-10
- **Games**: ~500-1000 games
- **Use case**: Experimenting with AI strategies
- **Recommendation**: Set $10/month budget

### Scenario 3: Small Tournament Series

- **Monthly cost**: $25-50
- **Games**: ~2000-4000 games
- **Use case**: Weekly tournaments with AI players
- **Recommendation**: Set $50/month budget with alerts at $25

### Scenario 4: Large-Scale Competition

- **Monthly cost**: $100-200
- **Games**: ~10,000+ games
- **Use case**: Major competitions, research
- **Recommendation**: Set $200/month budget with daily monitoring

---

## Budget Optimization Strategies

### Short-term (Immediate)

1. **Use rule-based players by default**: $0 cost
2. **Limit AI player usage to specific tournaments**: Controlled spending
3. **Implement token budgets per player**: Prevent overruns
4. **Monitor daily spend**: Catch anomalies early

### Medium-term (1-3 months)

1. **Optimize prompts**: Reduce token usage per game
2. **Implement caching**: 50%+ cost reduction for repeated context
3. **Batch API calls**: Reduce per-request overhead
4. **Use Haiku for simple strategies**: 12x cost reduction vs. Sonnet

### Long-term (3-12 months)

1. **Fine-tune smaller models**: One-time cost, then cheaper inference
2. **Hybrid strategies**: Rule-based with AI fallback
3. **Self-hosted models**: Eliminate API costs (requires infrastructure)
4. **Prompt library**: Reuse proven, efficient prompts

---

## Budget Approval Process

### Spending Authority

| Amount | Approval Required | Process |
|--------|------------------|---------|
| $0-10/month | None | Automatic |
| $10-50/month | Team lead | Email approval |
| $50-200/month | Project sponsor | Formal request |
| $200+/month | Executive | Business case required |

### Budget Increase Requests

Template for budget increase:

```markdown
## Budget Increase Request

**Current Budget**: $X/month
**Requested Budget**: $Y/month
**Increase**: $Z/month (+N%)

**Justification**:
- Use case: [Tournament series, research, etc.]
- Expected games/month: [N games]
- Cost per game: $X
- Total expected cost: $Y
- Benefit: [Learning, competition, research value]

**Cost Control Measures**:
- Token budgets per player
- Daily monitoring
- Automatic shutoff at threshold

**Approval**: [Name] - [Date]
```

---

## Contingency Planning

### If Budget Exceeded

1. **Immediate actions**:
   - Disable AI players
   - Switch to rule-based strategies
   - Investigate cause of overage

2. **Root cause analysis**:
   - Review token usage logs
   - Identify inefficient prompts
   - Check for runaway processes

3. **Prevention**:
   - Implement missing controls
   - Update monitoring thresholds
   - Optimize expensive operations

### Budget Reserves

Maintain 20% reserve for:
- Unexpected usage spikes
- Testing new features
- Bug fixes requiring LLM assistance

---

## Reporting and Review

### Weekly Reports

Generate automated reports:
- Total spend this week
- Tokens consumed
- Cost per game
- Budget utilization %
- Projected monthly cost

### Monthly Review

Conduct monthly budget review:
- Actual vs. budgeted spend
- Cost trends
- Optimization opportunities
- Budget adjustment needs

### Annual Planning

Review annually:
- Total year spend
- Cost per user/game trends
- Model pricing changes
- Infrastructure alternatives

---

## Notes

- **Budget is optional**: Core system has $0 LLM costs
- **AI costs only apply if using AI-powered players**
- **Most users will have $0 production costs**
- **Development costs already incurred (~$7-10) and complete**
- **Monitor actual usage** - estimates may vary based on:
  - Specific use patterns
  - Model selection
  - Prompt efficiency
  - Caching effectiveness

---

## References

- **Cost Analysis**: See `docs/COSTS.md` for detailed cost breakdown
- **Pricing**: Verify current rates at https://www.anthropic.com/pricing
- **Monitoring**: Anthropic Console → Usage & Billing
- **API Docs**: https://docs.anthropic.com/en/docs/

---

**Last Updated**: December 24, 2025
**Next Review**: Monthly or upon significant usage change
**Budget Owner**: Project Lead
