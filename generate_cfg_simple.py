"""Generate CFG as PNG using matplotlib."""
import sys
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

if not HAS_MATPLOTLIB:
    print("ERROR: matplotlib not available")
    sys.exit(1)

# CFG data
nodes = {
    'N1': {'pos': (5, 20), 'type': 'start', 'label': 'START'},
    'N2': {'pos': (5, 18), 'type': 'decision', 'label': 'dues < 0?'},
    'N3': {'pos': (2, 16), 'type': 'process', 'label': 'raise\nValueError'},
    'N4': {'pos': (5, 16), 'type': 'decision', 'label': 'invalid\nrol/cap?'},
    'N5': {'pos': (8, 14), 'type': 'process', 'label': 'raise\nValueError'},
    'N6': {'pos': (5, 14), 'type': 'decision', 'label': 'dues\n> 1000?'},
    'N7': {'pos': (2, 12), 'type': 'return', 'label': 'DUES_BLOCK'},
    'N8': {'pos': (5, 12), 'type': 'decision', 'label': 'already\nreg?'},
    'N9': {'pos': (2, 10), 'type': 'return', 'label': 'ALREADY_\nREGISTERED'},
    'N10': {'pos': (5, 10), 'type': 'decision', 'label': 'not\nprereq?'},
    'N11': {'pos': (2, 8), 'type': 'return', 'label': 'PREREQ_\nMISSING'},
    'N12': {'pos': (5, 8), 'type': 'decision', 'label': 'not\ncredit?'},
    'N13': {'pos': (2, 6), 'type': 'return', 'label': 'CREDIT_\nLIMIT'},
    'N14': {'pos': (5, 6), 'type': 'decision', 'label': 'enrolled\n> cap?'},
    'N15': {'pos': (2, 4), 'type': 'return', 'label': 'WAITLISTED'},
    'N16': {'pos': (5, 4), 'type': 'return', 'label': 'REGISTERED'},
    'N17': {'pos': (5, 0), 'type': 'end', 'label': 'EXIT'},
}

edges = [
    ('N1', 'N2', ''),
    ('N2', 'N3', 'T'),
    ('N2', 'N4', 'F'),
    ('N3', 'N17', ''),
    ('N4', 'N5', 'T'),
    ('N4', 'N6', 'F'),
    ('N5', 'N17', ''),
    ('N6', 'N7', 'T'),
    ('N6', 'N8', 'F'),
    ('N7', 'N17', ''),
    ('N8', 'N9', 'T'),
    ('N8', 'N10', 'F'),
    ('N9', 'N17', ''),
    ('N10', 'N11', 'T'),
    ('N10', 'N12', 'F'),
    ('N11', 'N17', ''),
    ('N12', 'N13', 'T'),
    ('N12', 'N14', 'F'),
    ('N13', 'N17', ''),
    ('N14', 'N15', 'T'),
    ('N14', 'N16', 'F'),
    ('N15', 'N17', ''),
    ('N16', 'N17', ''),
]

fig, ax = plt.subplots(figsize=(14, 18), dpi=150)

# Draw edges first (so they appear behind nodes)
for src, dst, label in edges:
    x1, y1 = nodes[src]['pos']
    x2, y2 = nodes[dst]['pos']

    color = 'red' if label == '' and nodes[src]['type'] == 'process' else 'black'
    style = 'dashed' if label == '' and nodes[src]['type'] == 'process' else 'solid'

    arrow = FancyArrowPatch(
        (x1, y1-0.4), (x2, y2+0.4),
        arrowstyle='->', mutation_scale=20, linewidth=1.5,
        color=color, linestyle=style
    )
    ax.add_patch(arrow)

    # Add edge label
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=9, fontweight='bold')

# Draw nodes
for node_id, node_data in nodes.items():
    x, y = node_data['pos']
    node_type = node_data['type']
    label = node_data['label']

    if node_type == 'start' or node_type == 'end':
        # Ellipse
        circle = mpatches.Ellipse((x, y), 1.2, 0.6, color='lightblue', ec='black', linewidth=2)
        ax.add_patch(circle)
        color = 'lightcoral' if node_type == 'end' else 'lightblue'
        circle = mpatches.Ellipse((x, y), 1.2, 0.6, color=color, ec='black', linewidth=2)
        ax.add_patch(circle)
    elif node_type == 'decision':
        # Diamond
        diamond = mpatches.FancyBboxPatch(
            (x-0.5, y-0.4), 1.0, 0.8,
            boxstyle="round,pad=0.05", color='lightyellow', ec='black', linewidth=2
        )
        ax.add_patch(diamond)
    else:  # process or return
        # Rectangle
        rect = FancyBboxPatch(
            (x-0.6, y-0.4), 1.2, 0.8,
            boxstyle="round,pad=0.05",
            color='lightgreen' if node_type == 'return' else 'lightgray',
            ec='black', linewidth=2
        )
        ax.add_patch(rect)

    ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold')
    ax.text(x-0.8, y, node_id, ha='right', va='center', fontsize=7, style='italic')

ax.set_xlim(0, 10)
ax.set_ylim(-1, 21)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Control Flow Graph: registration_decision()\nV(G)=8, 7 Decisions, 8 Basis Paths',
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(r'C:\Users\Ahmad Kazmi\Downloads\SQE_Assignment2_Student_Starter\SQE_Assignment2_Registration_Student\docs\cfg.png',
            dpi=150, bbox_inches='tight', facecolor='white')
print("Success: Generated docs/cfg.png")
