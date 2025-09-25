# The Agent Builder's Manual

Welcome to the Neural-Agent Fabric! This guide will teach you everything you need to know about creating "Agents" within this system.

Our goal is to make the process intuitive. If you can describe a job to a person, you can build an agent to do it.

## Part 1: The Philosophy - What *is* an Agent?

Before we write any code, let's understand the core idea.

Think of the `AgentFabric` as a project manager for a team of highly specialized, but very literal-minded, experts.

*   The **Project Manager** (`AgentFabric`) doesn't do the work itself. It reads an incoming request and decides which expert is needed.
*   The **Experts** (`Agents`) are waiting in their offices. They only do one thing, but they do it well. There's a `Writer`, a `Coder`, a `Researcher`, etc.
*   The **Company Library** (`MemoryVaults`) is a room full of filing cabinets. Each expert has a key to the specific cabinets they're allowed to read.

An **Agent** in our system is one of these experts. It's not just a prompt; it's a complete "job description" that defines **who it is**, **what it knows**, and **when it should work**.

Building an agent means defining these three things.

---

## Part 2: The Three Pillars of an Agent

Every agent you build is defined by three fundamental components.

### Pillar 1: Identity & Role (`Agent` class)

This is the agent's core personality and skill set. It's defined when you create an instance of the `Agent` class.

*   `agent_id`: A unique, simple name for your agent (e.g., `'coder_agent'`, `'critic_agent'`). This is its name tag.
*   `role_prompt`: **This is the most important part.** It is the agent's soul. It's the set of instructions you give it, defining its personality, its skills, its tone, and what it should *never* do.

**Example:**
```python
# An agent whose only job is to be extremely enthusiastic.
cheerleader_agent = Agent(
    agent_id="cheerleader_agent",
    role_prompt="You are a super enthusiastic cheerleader. Your job is to rephrase any information you are given in an exciting, positive, and encouraging way. You do not add any new information.",
    vault_ids=[] # This agent doesn't need to read any files.
)
```

### Pillar 2: Knowledge Access (`vault_ids`)

This defines which filing cabinets (Memory Vaults) the agent has a key to. By listing `vault_ids`, you give an agent the *permission* to access information from those specific vaults.

If a vault's ID is not in this list, the agent will never be able to see the information inside, even if it's relevant.

**Example:**
```python
# A writer agent that can access project plans and the style guide.
writer_agent = Agent(
    agent_id="writer_agent",
    role_prompt="You are a technical writer responsible for creating clear documentation.",
    vault_ids=["project_plans_vault", "style_guide_vault"] # Has two keys
)

# A security agent that can only see the codebase.
security_agent = Agent(
    agent_id="security_agent",
    role_prompt="You are a security expert who audits code for vulnerabilities.",
    vault_ids=["codebase_vault"] # Has only one key
)
```

### Pillar 3: Activation Rules (`gatekeeper_strategy`)

This is the logic that tells the Project Manager (`AgentFabric`) when to call your agent out of its office. This is not part of the `Agent` class itself, but it's the most critical part of making your agent *work*.

You define this in the `gatekeeper_strategy` function. It's a simple set of `if` statements that looks for keywords in the user's query.

**Example:**
```python
# This function tells the fabric when to wake up our writer and security agents.
def my_gatekeeper_strategy(query: str, all_agents: dict) -> list:
    woken = []
    q_lower = query.lower()

    # Rule for the writer
    if "write" in q_lower or "document" in q_lower:
        if "writer_agent" in all_agents:
            woken.append(all_agents["writer_agent"])

    # Rule for the security expert
    if "security" in q_lower or "vulnerability" in q_lower:
        if "security_agent" in all_agents:
            woken.append(all_agents["security_agent"])
            
    return woken
```

---

## Part 3: A Step-by-Step Guide to Building Your First Agent

Let's build a simple but functional agent: a `Summarizer_Agent`.

**Goal:** This agent will take any text and summarize it. It's a simple tool.

### Step 1: Create Your Use-Case File

Create a new Python file in your repository, like `my_first_agent.py`.

### Step 2: Set Up the Boilerplate

Copy and paste this starter code into your new file. It imports the fabric and sets up the LLM.

```python
# my_first_agent.py

# 1. Import the core components
from fabric_core import Agent, AgentFabric, MemoryVault, Claim

# 2. Setup the LLM
try:
    import os
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: raise ValueError("GOOGLE_API_KEY not set.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error: {e}. Please set your GOOGLE_API_KEY environment variable.")
    exit()

# We will add our custom code below this line...
```

### Step 3: Define the Agent's Identity and Role (Pillar 1)

Let's define our agent. It has a clear role and doesn't need access to any memory vaults for now.

```python
# Add this to your file:

summarizer_agent = Agent(
    agent_id="summarizer_agent",
    role_prompt="You are a highly skilled summarizer. Your only job is to take the user's query and provide a concise, easy-to-read summary of it.",
    vault_ids=[] # This agent doesn't need to read from memory.
)
```

### Step 4: Define the Agent's Activation Rules (Pillar 3)

Now, let's write the `gatekeeper_strategy` that tells the fabric when to use our summarizer.

```python
# Add these strategy functions to your file:

def summarizer_gatekeeper_strategy(query: str, all_agents: dict) -> list:
    """Wakes the summarizer if specific keywords are present."""
    woken = []
    # If the user asks to "summarize" or "tl;dr", wake our agent.
    if "summarize" in query.lower() or "tl;dr" in query.lower():
        if "summarizer_agent" in all_agents:
            woken.append(all_agents["summarizer_agent"])
    return woken

# For this simple agent, the other strategies can be empty.
def summarizer_beacon_strategy(query: str) -> dict:
    return {}

def summarizer_slice_augmentation_strategy(agent: Agent, base_beacons: dict) -> dict:
    return {}
```

### Step 5: Assemble and Run the Fabric

Finally, add the main execution block to create the fabric, register your agent, and run a query.

```python
# Add this to the end of your file:

if __name__ == "__main__":
    print("--- Initializing Summarizer Fabric ---")

    # Instantiate the Fabric with YOUR strategies
    fabric = AgentFabric(
        gatekeeper_strategy=summarizer_gatekeeper_strategy,
        beacon_strategy=summarizer_beacon_strategy,
        slice_augmentation_strategy=summarizer_slice_augmentation_strategy,
    )

    # Register your agent
    fabric.register_agent(summarizer_agent)

    # --- Run a test query ---
    long_text = """
    The Neural-Agent Concept is a self-managing, cost-conscious framework for multi-agent systems. 
    It uses a central orchestrator called the AgentFabric to manage a team of specialized agents. 
    The fabric decides which agents to wake up for a given task, provides them with relevant context from MemoryVaults, 
    and assembles their partial outputs into a final response. This design minimizes costs and improves system predictability.
    """
    
    query = f"summarize this for me: {long_text}"
    
    final_answer, _ = fabric.handle_request(query)

    print("\n======================================")
    print(f"USER QUERY:\n{query}\n")
    print("--- FINAL RESPONSE ---")
    print(final_answer)
    print("======================================")

    # Visualize the flow
    fabric.visualize_last_request()
```

### Step 6: Run and Observe!

Run your file from the terminal: `python my_first_agent.py`

You will see the `summarizer_agent` activate and provide a concise summary. The generated PNG diagram will visually confirm that only your `summarizer_agent` was woken up.

**Congratulations, you have successfully built and deployed your first agent!**

---

## Part 4: Best Practices for Building Great Agents

*   **Be a Specialist, Not a Generalist.** The most effective systems have many small, specialized agents rather than a few large, complex ones. An agent's role should be describable in a single sentence.
*   **Constrain Your Agents.** The most powerful part of a `role_prompt` is telling the agent what *not* to do. Use phrases like:
    *   "You do not make creative suggestions."
    *   "Your response must be in JSON format."
    *   "Never mention your own opinions."
*   **Think Like a Manager.** When writing your `gatekeeper_strategy`, ask yourself, "If I were a manager with this team, who would I tap on the shoulder for this request?" Your keywords should be the words that trigger that decision.
*   **Iterate and Test.** Building agents is an experimental science. Write an agent, test it with a few queries, look at the visualization, then refine its `role_prompt` or `gatekeeper` rules. Small changes can have a big impact.