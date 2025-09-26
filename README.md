# Neural-Agent Concept: A Declarative Multi-Agent Fabric 🤖

This repository contains the core implementation of the "Neural-Agent Concept," a self-managing, cost-conscious framework for building sophisticated multi-agent AI systems.

The framework is designed to let developers focus on agent logic rather than the complex plumbing of memory management and inter-agent coordination.

## Core Concepts

*   **AgentFabric:** The central orchestrator. It receives requests and manages the entire workflow, from waking the correct agents to assembling their final responses.
*   **Agent:** A specialized unit of logic with a defined role (e.g., `coder`, `planner`, `critic`). Each agent is powered by a language model.
*   **MemoryVault:** A named data store for facts, knowledge, or transcripts.
*   **Claim:** An atomic piece of information stored within a `MemoryVault`, tagged with `beacons` for fast retrieval.
*   **The Strategy Pattern:** The fabric is "dumb" by design. You inject your use-case-specific logic into it through three key strategy functions, making the core engine completely reusable.
    1.  `Gatekeeper Strategy`: The rules for which agents to wake up for a given query.
    2.  `Beacon Strategy`: The rules for extracting key context (like a user ID or topic) from a query.
    3.  `Slice Augmentation Strategy`: The rules for refining the context for each specific agent.

## How It Works

1.  **Receive Request:** A user query arrives at the `AgentFabric`.
2.  **Gatekeeper:** The fabric uses your `gatekeeper_strategy` to decide which agents are relevant, keeping all others dormant to save costs.
3.  **Beacon Extraction:** The fabric uses your `beacon_strategy` to pull a primary key or topic from the query (e.g., `ticket_id: 'T-123'`).
4.  **Slice Request:** For each woken agent, the fabric fetches a small, relevant "slice" of `Claims` from their attached `MemoryVaults` using the extracted beacons.
5.  **Agent Execution:** Each woken agent runs its logic with the user query and its unique slice of context, producing a partial result.
6.  **Response Assembly:** The fabric combines the partial results into a final response.

## Getting Started

### Prerequisites

*   Python 3.8+
*   Graphviz (for visualization).
    *   **macOS:** `brew install graphviz`
    *   **Ubuntu/Debian:** `sudo apt-get install graphviz`
    *   **Windows:** Download from the official site.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/datasciritwik/fabric.agent.git
    cd fabric.agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variable:**
    This framework uses Google's Gemini by default. Set your API key in your terminal.
    ```bash
    export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

## How to Use

The framework is designed to be used by importing the core engine and providing your own configuration.

1.  **Do not modify `fabric_core.py` or `fabric_visualizer.py`.** These are the reusable engine.
2.  **Create a new file** for your specific use case (e.g., `my_travel_app.py`).
3.  **In your new file, implement your custom strategies and define your agents.**

### Use-Case Template (`my_application.py`)

```python
# 1. Import the core components
from fabric_core import Agent, AgentFabric, MemoryVault, Claim

# 2. Define your custom strategies
def my_gatekeeper_strategy(query: str, all_agents: dict) -> list:
    # TODO: Add your logic to decide which agents to wake
    # Example: if "code" in query: return [all_agents['coder']]
    pass

def my_beacon_strategy(query: str) -> dict:
    # TODO: Add your logic to extract context from the query
    # Example: return {'topic': 'some_topic'}
    pass

def my_slice_augmentation_strategy(agent: Agent, base_beacons: dict) -> dict:
    # TODO: Add your logic to refine beacons for each agent
    return base_beacons.copy()

# 3. In your main execution block, build and run the fabric
if __name__ == "__main__":
    # --- Setup ---
    # (LLM API key configuration)

    # --- Instantiate the Fabric with YOUR strategies ---
    my_fabric = AgentFabric(
        gatekeeper_strategy=my_gatekeeper_strategy,
        beacon_strategy=my_beacon_strategy,
        slice_augmentation_strategy=my_slice_augmentation_strategy,
    )

    # --- Register your vaults and agents ---
    my_vault = MemoryVault(vault_id="my_knowledge_base")
    my_fabric.register_vault(my_vault)
    
    my_agent = Agent(
        agent_id="specialist_agent",
        role_prompt="You are an expert at...",
        vault_ids=["my_knowledge_base"]
    )
    my_fabric.register_agent(my_agent)
    
    # --- Populate vaults with data ---
    my_vault.add_claim(Claim("Some fact.", {'topic': 'some_topic'}))

    # --- Run a request ---
    query = "Ask a question that triggers your agents."
    final_answer, _ = my_fabric.handle_request(query)

    print(final_answer)

    # --- Visualize the flow ---
    my_fabric.visualize_last_request()