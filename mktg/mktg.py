import matplotlib
matplotlib.use('Agg')  # Headless mode for server rendering
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# Create scratch directory if needed
os.makedirs('./', exist_ok=True)

# 1. Initialize professional layout & theme
sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')
plt.rcParams['figure.dpi'] = 150

# 2. Complete empirical data from Marhadi et al. (2025)
# Tables 8 (Millennials) and 9 (Gen Z)
kano_data = {
    "Attribute": [
        "Range anxiety (Ra)", "Charging infrastructure (Ci)", "Charging time (Ct)", 
        "Battery durability (Bd)", "Affordability (Aff)", "Government incentives (Gi)", 
        "Resale value (Rv)", "Performance (Pf)", "Vehicle design (Vd)", 
        "Brand reputation (Br)", "Environmental impact (Ei)", "Reliability (Re)", 
        "Battery charging options (Bco)", "Upgradability (Up)"
    ],
    "Abbreviation": ["Ra", "Ci", "Ct", "Bd", "Aff", "Gi", "Rv", "Pf", "Vd", "Br", "Ei", "Re", "Bco", "Up"],
    # Millennials: Table 8
    "Mill_SI": [0.40, 0.38, 0.44, 0.72, 0.45, 0.66, 0.68, 0.82, 0.78, 0.62, 0.72, 0.64, 0.58, 0.69],
    "Mill_DI": [-0.68, -0.82, -0.66, -0.76, -0.69, -0.60, -0.58, -0.65, -0.49, -0.43, -0.55, -0.71, -0.28, -0.48],
    # Gen Z: Table 9
    "GenZ_SI": [0.40, 0.29, 0.33, 0.42, 0.42, 0.39, 0.37, 0.87, 0.78, 0.46, 0.29, 0.72, 0.70, 0.74],
    "GenZ_DI": [-0.83, -0.82, -0.87, -0.84, -0.71, -0.68, -0.21, -0.60, -0.70, -0.85, -0.74, -0.70, -0.81, -0.43]
}

df = pd.DataFrame(kano_data)

# 3. Plot Setup (expanded width for annotation panel on the right)
fig, ax = plt.subplots(figsize=(13, 11))

# Set axis limits with comfortable padding
ax.set_xlim(-1.10, 0.10)
ax.set_ylim(-0.05, 1.05)

# Add clear quadrant boundaries at SI = 0.5 and DI = -0.5
ax.axhline(0.5, color='black', linestyle='-', linewidth=1.2, zorder=1)
ax.axvline(-0.5, color='black', linestyle='-', linewidth=1.2, zorder=1)

# 4. Color Quadrants slightly for elegant visualization
ax.fill_between([-1.10, -0.5], 0.5, 1.05, color='#3498db', alpha=0.03)  # One-dimensional (Blue)
ax.fill_between([-0.5, 0.10], 0.5, 1.05, color='#2ecc71', alpha=0.03)   # Attractive (Green)
ax.fill_between([-1.10, -0.5], -0.05, 0.5, color='#e74c3c', alpha=0.03)  # Must-be (Red)
ax.fill_between([-0.5, 0.10], -0.05, 0.5, color='#9b59b6', alpha=0.03)   # Indifferent (Purple)

# 5. Plot the coordinates and connect with a vector arrow to represent the shift
for i, row in df.iterrows():
    # Plot Millennials (Circle, Orange)
    ax.scatter(row['Mill_DI'], row['Mill_SI'], color='#e67e22', marker='o', s=110, edgecolors='black', label='Millennials (M)' if i == 0 else "", zorder=4)
    # Plot Gen Z (Square, Dark Slate Blue)
    ax.scatter(row['GenZ_DI'], row['GenZ_SI'], color='#2c3e50', marker='s', s=110, edgecolors='black', label='Generation Z (Z)' if i == 0 else "", zorder=4)
    
    # Draw vector arrow showing cohort evolution (Millennial -> Gen Z)
    ax.annotate(
        "", 
        xy=(row['GenZ_DI'], row['GenZ_SI']), 
        xytext=(row['Mill_DI'], row['Mill_SI']),
        arrowprops=dict(arrowstyle="->", color='#7f8c8d', lw=1.5, linestyle='--', alpha=0.8),
        zorder=3
    )
    
    # Text adjustments to prevent visual overlays
    offset_x = 0.015
    offset_y = 0.015
    if row['Abbreviation'] in ['Br', 'Up']:
        offset_y = -0.03
    elif row['Abbreviation'] in ['Vd']:
        offset_x = -0.04
    elif row['Abbreviation'] in ['Ei']:
        offset_y = 0.02
        offset_x = -0.02
        
    ax.text(row['Mill_DI'] + offset_x, row['Mill_SI'] + offset_y, f"{row['Abbreviation']} (M)", fontsize=8, color='#d35400', fontweight='bold', alpha=0.85, zorder=5)
    ax.text(row['GenZ_DI'] + offset_x, row['GenZ_SI'] + offset_y, f"{row['Abbreviation']} (Z)", fontsize=8, color='#2c3e50', fontweight='bold', zorder=5)

# 6. Callout circles & annotations to indicate preferences and attributes
# Halo 1: Gen Z Ethical & Brand Anchor (Br & Ei shift into Must-be)
circle_ei = plt.Circle((-0.74, 0.29), 0.06, color='#c0392b', fill=False, linestyle='-', lw=1.5, alpha=0.7, zorder=2)
circle_br = plt.Circle((-0.85, 0.46), 0.06, color='#c0392b', fill=False, linestyle='-', lw=1.5, alpha=0.7, zorder=2)
ax.add_patch(circle_ei)
ax.add_patch(circle_br)

ax.annotate(
    "Gen Z Ethical Anchors\n(Brand Ethics & Eco-credentials\nshift into Must-Be category)", 
    xy=(-0.80, 0.38), 
    xytext=(-1.05, 0.15),
    arrowprops=dict(facecolor='black', shrink=0.08, width=0.5, headwidth=4, headlength=4),
    fontsize=9.5, fontweight='bold', color='#c0392b', bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#e74c3c", alpha=0.9),
    zorder=6
)

# Halo 2: Resale Value (Rv) Divergence
ax.annotate(
    "Resale Value Divergence\n(Millennials track performance,\nGen Z is completely Indifferent)", 
    xy=(-0.21, 0.37), 
    xytext=(-0.45, 0.15),
    arrowprops=dict(facecolor='black', shrink=0.08, width=0.5, headwidth=4, headlength=4),
    fontsize=9.5, fontweight='bold', color='#8e44ad', bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#9b59b6", alpha=0.9),
    zorder=6
)

# Halo 3: High Design Sensitivity for Gen Z (Vd)
ax.annotate(
    "Design Sensitivity\n(Aesthetic is a performance\ndriver for Gen Z; unmet design\nactively hurts sales)", 
    xy=(-0.70, 0.78), 
    xytext=(-1.05, 0.82),
    arrowprops=dict(facecolor='black', shrink=0.08, width=0.5, headwidth=4, headlength=4),
    fontsize=9.5, fontweight='bold', color='#2980b9', bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#3498db", alpha=0.9),
    zorder=6
)

# Halo 4: Upgradability (Up) - Shared Attractive Delighter
ax.annotate(
    "Modular Upgradability\n(Shared delighter for both cohorts,\noffering solid brand-switching leverage)", 
    xy=(-0.45, 0.71), 
    xytext=(0.02, 0.60),
    arrowprops=dict(facecolor='black', shrink=0.08, width=0.5, headwidth=4, headlength=4),
    fontsize=9.5, fontweight='bold', color='#27ae60', bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#2ecc71", alpha=0.9),
    zorder=6
)

# 7. Add Bold Quadrant Text Labels
ax.text(-0.82, 1.02, "ONE-DIMENSIONAL (O)\nSatisfaction scales linearly", fontsize=11, fontweight='bold', color='#2980b9', ha='center', alpha=0.85)
ax.text(-0.20, 1.02, "ATTRACTIVE (A)\nUnexpected premium delighters", fontsize=11, fontweight='bold', color='#27ae60', ha='center', alpha=0.85)
ax.text(-0.82, -0.03, "MUST-BE (M)\nBaseline table stakes (Rejection if missing)", fontsize=11, fontweight='bold', color='#c0392b', ha='center', alpha=0.85)
ax.text(-0.20, -0.03, "INDIFFERENT (I)\nFeatures buyers do not prioritize", fontsize=11, fontweight='bold', color='#8e44ad', ha='center', alpha=0.85)

# 8. Axes Labels and Story-Driven Title (Data-Craft Compliant)
ax.set_title("Gen Z Drags Brand & Environment Into 'Must-Be' Baselines, While Millennials Prioritize Convenience", fontsize=14, fontweight='bold', pad=25)
ax.set_xlabel("Dissatisfaction Index (DI)  [Higher absolute score = More critical baseline]", fontsize=11, fontweight='bold', labelpad=12)
ax.set_ylabel("Satisfaction Index (SI)  [Higher score = Greater delight potential]", fontsize=11, fontweight='bold', labelpad=12)

# Set grid style and legend position
ax.grid(True, linestyle=':', alpha=0.5)
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=True, shadow=True, fontsize=11)

# 9. Source Credit annotation
plt.figtext(0.02, 0.01, "Source: Marhadi et al. (2025) - Kano-Model EV Purchase Priorities and Cohort Perceptions", fontsize=8, style='italic', color='gray')

# Fit plot elements properly
plt.tight_layout()

# Save output
output_img_path = './kano_millennials_genz_enhanced.png'
plt.savefig(output_img_path, dpi=150, bbox_inches='tight')
plt.close()
print("Saved kano_millennials_genz_enhanced.png successfully.")
