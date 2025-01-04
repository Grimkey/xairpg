from __future__ import annotations

import json
from pydantic import BaseModel
from enum import Enum
from typing import Optional

from src.ai_call import AIModel, Message

# Define enums for limited choice fields
class AttitudeTowardPlayer(str, Enum):
    friendly = "Friendly"
    neutral = "Neutral"
    suspicious = "Suspicious"
    hostile = "Hostile"

class Disposition(str, Enum):
    optimistic = "Optimistic"
    cynical = "Cynical"
    mischievous = "Mischievous"
    stoic = "Stoic"

class Motivation(str, Enum):
    self_serving = "Self-serving"
    altruistic = "Altruistic"
    revenge_driven = "Revenge-driven"
    curious = "Curious"

class Intelligence(str, Enum):
    low = "Low"
    average = "Average"
    high = "High"
    genius = "Genius"

class CombatAbility(str, Enum):
    strong = "Strong"
    weak = "Weak"
    specialist = "Specialist"

class Presence(str, Enum):
    subtle = "Subtle"
    commanding = "Commanding"
    mysterious = "Mysterious"

# Define the Pydantic models
class Personality(BaseModel):
    attitudeTowardPlayer: AttitudeTowardPlayer
    disposition: Disposition
    motivations: Motivation

class CognitiveAttributes(BaseModel):
    intelligence: Intelligence
    knowledgeAreas: list[str]

class Communication(BaseModel):
    speechAccent: Optional[str]
    mannerisms: Optional[str]
    pacing: Optional[str]
    tone: Optional[str]
    keyPhrases: Optional[list[str]]

class Relationships(BaseModel):
    connections: Optional[list[str]]
    alignment: Optional[str]

class RoleSpecificTraits(BaseModel):
    combatAbility: CombatAbility
    powersOrSkills: Optional[list[str]]
    questUtility: Optional[list[str]]

class Appearance(BaseModel):
    uniqueFeatures: Optional[list[str]]
    wardrobe: Optional[str]
    bodyLanguage: Optional[str]

class PhysicalTraits(BaseModel):
    appearance: Appearance
    presence: Presence

class BehaviorTrigger(BaseModel):
    trigger: str
    reaction: str

class Interactivity(BaseModel):
    behaviorTriggers: Optional[list[BehaviorTrigger]]
    hintsAndClues: Optional[list[str]]
    progression: Optional[dict]

class NPC(BaseModel):
    name: str
    description: str
    personality: Personality
    cognitiveAttributes: CognitiveAttributes
    communication: Communication
    relationships: Relationships
    roleSpecificTraits: RoleSpecificTraits
    physicalTraits: PhysicalTraits
    interactivity: Interactivity

    @staticmethod
    def from_file(file_path: str):
        with open(file_path, 'r') as file:
            npc_data = json.load(file)
        return NPC(**npc_data)

    def to_file(self, file_path: str):
        with open(file_path, 'w') as file:
            json.dump(self.model_dump(), file, indent=2)

    @staticmethod
    def create(prompt: str, ai_model: AIModel) -> NPC:
        system_message = Message(
            role='system',
            content=prompt
        )

        user_message = Message(
            role='user',
            content=""
        )

        npc_data = ai_model.response([system_message, user_message])
        content = npc_data['message']['content']
        print(content)
        npc_dict = json.loads(content)
        return NPC(**npc_dict)
        