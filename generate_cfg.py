"""Generate CFG for registration_decision() using graphviz or networkx."""
import subprocess
import sys

try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

# CFG definition: nodes and edges for registration_decision()
cfg_nodes = {
    'N1': ('start', 'START', ''),
    'N2': ('decision', 'dues < 0?', '46'),
    'N3': ('process', 'raise ValueError', '47'),
    'N4': ('decision', 'enrollment/capacity invalid?', '48'),
    'N5': ('process', 'raise ValueError', '49'),
    'N6': ('decision', 'dues > 1000?', '50'),
    'N7': ('return', 'DUES_BLOCK', '51'),
    'N8': ('decision', 'already registered?', '52'),
    'N9': ('return', 'ALREADY_REGISTERED', '53'),
    'N10': ('decision', 'not prerequisites?', '54'),
    'N11': ('return', 'PREREQUISITES_MISSING', '55'),
    'N12': ('decision', 'not credit_limit?', '56'),
    'N13': ('return', 'CREDIT_LIMIT', '57'),
    'N14': ('decision', 'enrolled > capacity?', '58'),
    'N15': ('return', 'WAITLISTED', '59'),
    'N16': ('return', 'REGISTERED', '60'),
    'N17': ('end', 'EXIT', ''),
}

# CFG edges: (from, to, label)
cfg_edges = [
    ('N1', 'N2', ''),
    ('N2', 'N3', 'T'),
    ('N2', 'N4', 'F'),
    ('N3', 'N17', 'exception'),
    ('N4', 'N5', 'T'),
    ('N4', 'N6', 'F'),
    ('N5', 'N17', 'exception'),
    ('N6', 'N7', 'T'),
    ('N6', 'N8', 'F'),
    ('N7', 'N17', 'return'),
    ('N8', 'N9', 'T'),
    ('N8', 'N10', 'F'),
    ('N9', 'N17', 'return'),
    ('N10', 'N11', 'T'),
    ('N10', 'N12', 'F'),
    ('N11', 'N17', 'return'),
    ('N12', 'N13', 'T'),
    ('N12', 'N14', 'F'),
    ('N13', 'N17', 'return'),
    ('N14', 'N15', 'T'),
    ('N14', 'N16', 'F'),
    ('N15', 'N17', 'return'),
    ('N16', 'N17', 'return'),
]

def generate_graphviz_cfg():
    """Generate CFG using graphviz (dot)."""
    try:
        dot = graphviz.Digraph(comment='registration_decision CFG', format='png')
        dot.attr(rankdir='TB', size='12,16')
        dot.attr('node', shape='box')

        # Add nodes
        for node_id, (node_type, label, line) in cfg_nodes.items():
            if node_type == 'start':
                shape = 'ellipse'
                color = 'lightblue'
                full_label = label
            elif node_type == 'end':
                shape = 'ellipse'
                color = 'lightcoral'
                full_label = label
            elif node_type == 'decision':
                shape = 'diamond'
                color = 'lightyellow'
                full_label = f"{label}\n(line {line})"
            elif node_type == 'return':
                shape = 'box'
                color = 'lightgreen'
                full_label = f"{label}\n(line {line})"
            else:  # process
                shape = 'box'
                color = 'lightgray'
                full_label = f"{label}\n(line {line})"

            dot.node(node_id, full_label, shape=shape, fillcolor=color, style='filled')

        # Add edges
        for src, dst, label in cfg_edges:
            if label == 'exception':
                dot.edge(src, dst, label, color='red', style='dashed')
            elif label == 'return':
                dot.edge(src, dst, label, color='green')
            elif label in ['T', 'F']:
                dot.edge(src, dst, label, color='black')
            else:
                dot.edge(src, dst, label, color='black')

        # Save
        output_path = r'C:\Users\Ahmad Kazmi\Downloads\SQE_Assignment2_Student_Starter\SQE_Assignment2_Registration_Student\docs\cfg'
        dot.render(output_path, cleanup=True)
        print(f"✓ Generated: docs/cfg.png (graphviz)")
        return True
    except Exception as e:
        print(f"✗ Graphviz failed: {e}")
        return False

def generate_networkx_cfg():
    """Generate CFG using networkx and matplotlib."""
    if not HAS_NETWORKX:
        print("✗ NetworkX not available")
        return False

    G = nx.DiGraph()

    # Add nodes with attributes
    for node_id, (node_type, label, line) in cfg_nodes.items():
        G.add_node(node_id, node_type=node_type, label=label, line=line)

    # Add edges
    for src, dst, label in cfg_edges:
        G.add_edge(src, dst, label=label)

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Draw
    fig, ax = plt.subplots(figsize=(16, 20))

    # Draw nodes by type
    node_colors = []
    node_shapes = []
    for node in G.nodes():
        node_type = G.nodes[node]['node_type']
        if node_type == 'start':
            node_colors.append('lightblue')
        elif node_type == 'end':
            node_colors.append('lightcoral')
        elif node_type == 'decision':
            node_colors.append('lightyellow')
        elif node_type == 'return':
            node_colors.append('lightgreen')
        else:
            node_colors.append('lightgray')

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000, ax=ax)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='black', arrows=True, arrowsize=20, ax=ax)

    # Draw labels
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold', ax=ax)

    # Draw edge labels
    edge_labels = {(src, dst): label for src, dst, label in cfg_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax)

    ax.set_title('Control Flow Graph: registration_decision()', fontsize=16, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()

    output_path = r'C:\Users\Ahmad Kazmi\Downloads\SQE_Assignment2_Student_Starter\SQE_Assignment2_Registration_Student\docs\cfg.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Generated: docs/cfg.png (networkx)")
    return True

if __name__ == '__main__':
    if HAS_GRAPHVIZ:
        if generate_graphviz_cfg():
            sys.exit(0)

    if HAS_NETWORKX:
        if generate_networkx_cfg():
            sys.exit(0)

    print("✗ No graphing library available (install graphviz or matplotlib/networkx)")
    sys.exit(1)
