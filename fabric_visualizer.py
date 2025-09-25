import graphviz

def generate_visualization(fabric, trace, filename="fabric_flow"):
    """
    Generates a visualization of the last request handled by the AgentFabric.
    
    Args:
        fabric: The AgentFabric instance (to get static structure).
        trace: The structured trace data from the last request.
        filename: The base name for the output file.
    """
    dot = graphviz.Digraph(comment='Agent Fabric Flow')
    dot.attr(rankdir='LR', splines='ortho', label=f"Query: {trace['query']}", labelloc='t', fontsize='20')

    # Define styles
    WOKEN_STYLE = {'style': 'filled', 'fillcolor': 'lightblue', 'penwidth': '2'}
    ASLEEP_STYLE = {'style': 'filled', 'fillcolor': 'whitesmoke'}
    
    # Create subgraphs for organization
    with dot.subgraph(name='cluster_agents') as c:
        c.attr(label='Agents (The Team)', style='filled', color='lightgrey')
        for agent_id, agent in fabric._agents.items():
            style = WOKEN_STYLE if agent in trace['woken_agents'] else ASLEEP_STYLE
            c.node(agent_id, f"Agent:\n{agent_id}", shape='box', **style)

    with dot.subgraph(name='cluster_vaults') as c:
        c.attr(label='Memory Vaults', style='filled', color='lightgrey')
        for vault_id, vault in fabric._vaults.items():
            c.node( vault_id, f"Vault:\n{vault_id}", shape='cylinder')

    # Show static agent-to-vault attachments
    for agent_id, agent in fabric._agents.items():
        for vault_id in agent.vault_ids:
            dot.edge(agent_id, vault_id, style='dashed', arrowhead='none', label='can access')
            
    # Add a central node for the fabric itself
    dot.node('AgentFabric', 'AgentFabric\n(Orchestrator)', shape='doublecircle', style='filled', fillcolor='gold')
    
    # --- Dynamic Flow for the current query ---
    
    if trace['woken_agents']:
        # Gatekeeper decision
        for agent in trace['woken_agents']:
            dot.edge('AgentFabric', agent.id, label='wakes', color='green', penwidth='2')

        # Slice requests and returned data
        for agent_id, slices in trace['slices_per_agent'].items():
            for vault_id, claims in slices.items():
                if claims:
                    claims_label = "Gets Slice:\n" + "\n".join([f"- {c.content[:30]}..." for c in claims])
                    dot.edge(vault_id, agent_id, label=claims_label, color='blue', fontcolor='blue', penwidth='2')

    # Render and save the file
    try:
        output_path = dot.render(filename, format='png', view=False, cleanup=True)
        print(f"✅ Visualization saved to: {output_path}")
    except Exception as e:
        print(f"❌ Failed to generate visualization. Ensure Graphviz is installed and in your system's PATH. Error: {e}")