#!/usr/bin/env python3
"""
Generate token consumption visualization for Agent League System development.

This script creates a bar chart showing estimated token usage across development phases.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Development phase token estimates (from docs/COSTS.md)
phases = {
    'PreProject': {
        'input': 50000,
        'output': 30000,
        'agents': ['repo-scaffolder', 'prd-author', 'architecture-author',
                   'readme-author', 'config-security-baseline', 'prompt-log-initializer', 'git-workflow']
    },
    'TaskLoop': {
        'input': 400000,
        'output': 250000,
        'agents': ['implementer', 'quality-commenter', 'unit-test-writer',
                   'edge-case-defender', 'expected-results-recorder', 'readme-updater', 'prompt-log-updater']
    },
    'ResearchLoop': {
        'input': 0,
        'output': 0,
        'agents': []  # Not applicable for this project
    },
    'ReleaseGate': {
        'input': 100000,
        'output': 60000,
        'agents': ['python-packager', 'building-block-reviewer', 'extensibility-planner',
                   'quality-standard-mapper', 'final-checklist-gate', 'cost-analyzer']
    }
}

def create_token_consumption_chart():
    """Create and save token consumption visualization."""

    # Prepare data
    phase_names = list(phases.keys())
    input_tokens = [phases[p]['input'] for p in phase_names]
    output_tokens = [phases[p]['output'] for p in phase_names]
    total_tokens = [phases[p]['input'] + phases[p]['output'] for p in phase_names]

    # Create figure with larger size for readability
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Agent League System - Development Token Consumption Analysis',
                 fontsize=16, fontweight='bold')

    # Chart 1: Stacked bar chart by phase
    x_pos = range(len(phase_names))
    bars1 = ax1.bar(x_pos, input_tokens, label='Input Tokens', color='#3498db', alpha=0.8)
    bars2 = ax1.bar(x_pos, output_tokens, bottom=input_tokens, label='Output Tokens',
                    color='#e74c3c', alpha=0.8)

    ax1.set_xlabel('Development Phase', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Tokens', fontsize=12, fontweight='bold')
    ax1.set_title('Token Consumption by Development Phase', fontsize=14, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(phase_names, rotation=0)
    ax1.legend(loc='upper left', frameon=True, shadow=True)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels on bars
    for i, (p, input_val, output_val, total) in enumerate(zip(phase_names, input_tokens, output_tokens, total_tokens)):
        if total > 0:  # Only label non-zero phases
            ax1.text(i, total + 10000, f'{total:,}', ha='center', va='bottom',
                    fontweight='bold', fontsize=10)

    # Chart 2: Pie chart of total distribution
    # Filter out zero-value phases
    non_zero_phases = [(name, total) for name, total in zip(phase_names, total_tokens) if total > 0]
    if non_zero_phases:
        pie_labels = [name for name, _ in non_zero_phases]
        pie_values = [total for _, total in non_zero_phases]

        colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
        explode = [0.05 if val == max(pie_values) else 0 for val in pie_values]

        wedges, texts, autotexts = ax2.pie(pie_values, labels=pie_labels, autopct='%1.1f%%',
                                            startangle=90, colors=colors[:len(pie_labels)],
                                            explode=explode, shadow=True)

        # Enhance text
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        ax2.set_title('Token Distribution Across Phases', fontsize=14, fontweight='bold')

    # Add summary text
    total_input = sum(input_tokens)
    total_output = sum(output_tokens)
    grand_total = sum(total_tokens)

    summary_text = f"""
    Total Development Tokens: {grand_total:,}
    Input Tokens: {total_input:,} ({total_input/grand_total*100:.1f}%)
    Output Tokens: {total_output:,} ({total_output/grand_total*100:.1f}%)

    Estimated Cost (Claude Sonnet 4.5):
    Input: ${total_input/1_000_000 * 3:.2f}
    Output: ${total_output/1_000_000 * 15:.2f}
    Total: ${(total_input/1_000_000 * 3) + (total_output/1_000_000 * 15):.2f}
    """

    fig.text(0.5, 0.02, summary_text, ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout(rect=[0, 0.1, 1, 0.96])

    # Save figure
    output_path = Path(__file__).parent.parent / 'results' / 'token_consumption.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Visualization saved to: {output_path}")

    # Also create a timeline view
    create_timeline_chart()

    return output_path


def create_timeline_chart():
    """Create a timeline view of development phases."""

    fig, ax = plt.subplots(figsize=(14, 6))

    # Phase data with approximate time allocation
    phase_data = [
        ('PreProject', 80000, 7, '#3498db'),
        ('TaskLoop', 650000, 120, '#2ecc71'),
        ('ResearchLoop', 0, 0, '#f39c12'),
        ('ReleaseGate', 160000, 9, '#e74c3c'),
    ]

    # Filter out zero phases
    phase_data = [(name, tokens, count, color) for name, tokens, count, color in phase_data if tokens > 0]

    y_positions = range(len(phase_data))

    for i, (phase, tokens, agent_count, color) in enumerate(phase_data):
        # Draw phase bar
        ax.barh(i, tokens, height=0.5, color=color, alpha=0.7, edgecolor='black', linewidth=1.5)

        # Add labels
        ax.text(tokens/2, i, f'{phase}\n{tokens:,} tokens\n{agent_count} invocations',
                ha='center', va='center', fontweight='bold', fontsize=10, color='white',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.8, edgecolor='black'))

    ax.set_yticks(y_positions)
    ax.set_yticklabels([p[0] for p in phase_data])
    ax.set_xlabel('Total Tokens', fontsize=12, fontweight='bold')
    ax.set_title('Development Timeline - Token Consumption by Phase',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Add total
    total = sum(p[1] for p in phase_data)
    ax.text(total * 0.95, len(phase_data) - 0.5, f'Total: {total:,} tokens',
            ha='right', va='top', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

    plt.tight_layout()

    output_path = Path(__file__).parent.parent / 'results' / 'token_timeline.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Timeline visualization saved to: {output_path}")


if __name__ == '__main__':
    print("Generating token consumption visualizations...")
    print()

    try:
        output = create_token_consumption_chart()
        print()
        print("✓ Visualization generation complete!")
        print(f"  - Token consumption chart: results/token_consumption.png")
        print(f"  - Timeline chart: results/token_timeline.png")
        print()
        print("View the charts:")
        print(f"  $ open results/token_consumption.png")
        print(f"  $ open results/token_timeline.png")
    except Exception as e:
        print(f"✗ Error generating visualization: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
