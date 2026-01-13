import matplotlib.pyplot as plt
from datetime import datetime

def plot_weight_history(history):
    """
    history: list of dicts with keys: date, weight_kg, bmi
    """
    if not history:
        print("No data to plot.")
        return

    # Convert date strings to datetime objects
    dates = [row['date'] for row in history]  # already datetime.date objects
    weights = [row['weight_kg'] for row in history]
    bmis = [row['bmi'] for row in history]

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Weight line
    ax1.plot(dates, weights, color='blue', marker='o', label='Weight (kg)')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Weight (kg)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # BMI line on second axis
    ax2 = ax1.twinx()
    ax2.plot(dates, bmis, color='green', marker='x', linestyle='--', label='BMI')
    ax2.set_ylabel('BMI', color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    plt.title('Weight and BMI Over Time')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
