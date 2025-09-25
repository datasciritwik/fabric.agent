import os
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable, Tuple

# --- LLM Integration (Pluggable by default) ---
import google.generativeai as genai

# Import the visualizer so the fabric can call it
from fabric_visualizer import generate_visualization

def llm_call(prompt: str) -> str:
    """
    A swappable function to call the LLM.
    Currently configured for Google Gemini.
    """
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"    [LLM Error] Call failed: {e}")
        return f"[Error: LLM call failed.]"

# --- Core Data Structures ---

@dataclass
class Claim:
    """A compact, atomic fact or assertion stored in a vault."""
    content: str
    beacons: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

# --- Core Components ---

class MemoryVault:
    """A named store for claims. Uses a simple in-memory list."""
    def __init__(self, vault_id: str):
        self.id = vault_id
        self._claims: List[Claim] = []

    def add_claim(self, claim: Claim):
        self._claims.append(claim)

    def get_slice(self, beacon_query: Dict[str, Any], max_claims: int = 5) -> List[Claim]:
        """Filters claims based on perfect beacon matching."""
        matches = [
            claim for claim in self._claims
            if all(item in claim.beacons.items() for item in beacon_query.items())
        ]
        return matches[-max_claims:] # Return the most recent N matches

class Agent:
    """A unit of logic that performs a role, powered by an LLM."""
    def __init__(self, agent_id: str, role_prompt: str, vault_ids: List[str]):
        self.id = agent_id
        self.role = role_prompt
        self.vault_ids = vault_ids

    def run(self, query: str, slices: Dict[str, List[Claim]]) -> str:
        """Formats the prompt and calls the LLM."""
        context = ""
        for vault_id, claims in slices.items():
            if claims:
                context += f"\n--- Context from {vault_id} ---\n"
                for claim in claims:
                    context += f"- {claim.content}\n"
        if not context:
            context = "\n--- No relevant information found in memory vaults. ---\n"

        prompt = f"""
Your Role: {self.role}
User's Query: "{query}"
Relevant Information:
{context}
Based on your role and the provided information, generate a concise, partial response.
"""
        return llm_call(prompt)

# --- Type Definitions for Strategy Functions ---
GatekeeperStrategy = Callable[[str, Dict[str, Agent]], List[Agent]]
BeaconStrategy = Callable[[str], Dict[str, Any]]
SliceAugmentationStrategy = Callable[[Agent, Dict[str, Any]], Dict[str, Any]]

# --- The Generalized Orchestrator ---

class AgentFabric:
    """The generalized runtime that coordinates agents and vaults."""
    def __init__(
        self,
        gatekeeper_strategy: GatekeeperStrategy,
        beacon_strategy: BeaconStrategy,
        slice_augmentation_strategy: SliceAugmentationStrategy,
    ):
        self._agents: Dict[str, Agent] = {}
        self._vaults: Dict[str, MemoryVault] = {}
        
        # Inject the use-case-specific strategies
        self.gatekeeper_strategy = gatekeeper_strategy
        self.beacon_strategy = beacon_strategy
        self.slice_augmentation_strategy = slice_augmentation_strategy
        
        # Stores data from the last request for visualization
        self.last_trace = {}

    def register_agent(self, agent: Agent):
        self._agents[agent.id] = agent

    def register_vault(self, vault: MemoryVault):
        self._vaults[vault.id] = vault

    def handle_request(self, query: str) -> Tuple[str, dict]:
        """The core, generalized query flow."""
        self.last_trace = {
            'query': query, 'woken_agents': [], 'base_beacons': {},
            'slices_per_agent': {}, 'partial_results': {},
        }

        woken_agents = self.gatekeeper_strategy(query, self._agents)
        self.last_trace['woken_agents'] = woken_agents
        if not woken_agents:
            return "No relevant agent could be found to handle this request.", self.last_trace

        base_beacons = self.beacon_strategy(query)
        self.last_trace['base_beacons'] = base_beacons
        
        partial_results_list = []
        for agent in woken_agents:
            agent_beacons = self.slice_augmentation_strategy(agent, base_beacons)
            
            slices_for_agent = {}
            for vault_id in agent.vault_ids:
                if vault_id in self._vaults:
                    vault = self._vaults[vault_id]
                    slices_for_agent[vault_id] = vault.get_slice(agent_beacons)
            self.last_trace['slices_per_agent'][agent.id] = slices_for_agent
            
            partial_result = agent.run(query, slices_for_agent)
            self.last_trace['partial_results'][agent.id] = partial_result
            partial_results_list.append(f"--- Contribution from {agent.id} ---\n{partial_result}")

        final_response = "\n\n".join(partial_results_list)
        return final_response, self.last_trace

    def visualize_last_request(self):
        """Generates a diagram of the most recent handle_request call."""
        if not self.last_trace or not self.last_trace.get('query'):
            print("No request has been handled yet. Cannot visualize.")
            return

        safe_filename = re.sub(r'[\W_]+', '_', self.last_trace['query'])[:50]
        output_filename = f"flow_{safe_filename}"
        
        generate_visualization(self, self.last_trace, output_filename)