from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

# Define the magical materials as an Enum
class MagicalMaterial(str, Enum):
    EBONSTONE = "Ebonstone"
    MOONSHARD_SILVER = "Moonshard Silver"
    ASHVINE_ESSENCE = "Ashvine Essence"
    SANGUINE_CRYSTAL = "Sanguine Crystal"
    SHADOWGLASS = "Shadowglass"

# Define the inventory for each agent
class Inventory(BaseModel):
    money: int = Field(0, description="Amount of money the agent has.")
    magical_materials: Dict[MagicalMaterial, int] = Field(
        default_factory=lambda: {material: 0 for material in MagicalMaterial},
        description="Quantities of each magical material in grams."
    )

# Define the agent's plan
class AgentPlan(BaseModel):
    action: str = Field(..., description="The intended action (buy, barter, steal, inquire, sell).")
    target_item: Optional[MagicalMaterial] = Field(
        None, description="The magical material that the action is targeting, if applicable."
    )
    target_agent: Optional[str] = Field(
        None, description="The ID of the agent or NPC involved in the action, if applicable."
    )
    amount: Optional[int] = Field(
        None, description="The amount of magical material or money involved in the action."
    )

# Function to seed agents with initial inventory
def seed_agents(num_agents: int) -> Dict[str, Inventory]:
    from random import randint, choice

    agents = {}
    for i in range(1, num_agents + 1):
        agent_id = f"Agent_{i}"
        inventory = Inventory(
            money=randint(50, 500),  # Seed random money between 50 and 500
            magical_materials={
                material: randint(0, 50) for material in MagicalMaterial  # Seed random quantities between 0 and 50 grams
            }
        )
        agents[agent_id] = inventory
    return agents

# Example usage
if __name__ == "__main__":
    # Seed 10 agents with random inventory
    agents = seed_agents(10)
    for agent_id, inventory in agents.items():
        print(f"{agent_id}: {inventory.model_dump_json()}")

    # Example plan for an agent
    plan = AgentPlan(
        action="buy",
        target_item=MagicalMaterial.EBONSTONE,
        target_agent="Agent_2",
        amount=10
    )
    print("\nAgent Plan:")
    print(plan.model_dump_json())