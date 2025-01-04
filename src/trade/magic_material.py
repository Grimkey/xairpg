from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class MagicalMaterial(str, Enum):
    EBONSTONE = "Ebonstone"
    MOONSHARD_SILVER = "Moonshard Silver"
    ASHVINE_ESSENCE = "Ashvine Essence"
    SANGUINE_CRYSTAL = "Sanguine Crystal"
    SHADOWGLASS = "Shadowglass"


class TransactionType(str, Enum):
    FRIENDLY = "Friendly"
    BLACKMAIL = "Blackmail"
    STOLEN = "Stolen"
    PURCHASED = "Purchased"
    TRADE = "Trade"
    BARTER = "Barter"
    GIFT = "Gift"
    DEBT_REPAYMENT = "Debt Repayment"
    EXTORTION = "Extortion"
    BRIBERY = "Bribery"
    CHARITY = "Charity"
    SEIZED = "Seized"


class Transaction(BaseModel):
    seller_id: Optional[int]  # None if there is no seller (e.g., charity or inheritance)
    buyer_id: Optional[int]  # None if there is no buyer (e.g., confiscated materials)
    material: MagicalMaterial
    quantity: float
    transaction_type: TransactionType
    details: Optional[str]
    date: date


class TransactionLog(BaseModel):
    transactions: List[Transaction] = Field(default_factory=list)

    def add_transaction(self, transaction: Transaction):
        """
        Add a transaction to the log.
        """
        self.transactions.append(transaction)

    def query_by_player(self, player_id: int) -> List[Transaction]:
        """
        Get all transactions involving a specific player.
        """
        return [
            transaction for transaction in self.transactions
            if transaction.seller_id == player_id or transaction.buyer_id == player_id
        ]

    def query_by_material(self, material: MagicalMaterial) -> List[Transaction]:
        """
        Get all transactions involving a specific magical material.
        """
        return [
            transaction for transaction in self.transactions
            if transaction.material == material
        ]


class MagicalMaterialsManager:
    def __init__(self):
        # Dictionary to track player inventories, with material quantities (grams)
        self.inventory: dict[int, dict[MagicalMaterial, float]] = {}
        # Transaction log to record all transactions
        self.transaction_log = TransactionLog()

    def assign_material(self, player_id: int, material: MagicalMaterial, quantity: float):
        """
        Assign a specific quantity of a magical material to a player's inventory.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if player_id not in self.inventory:
            self.inventory[player_id] = {}
        self.inventory[player_id][material] = self.inventory[player_id].get(material, 0) + quantity

    def remove_material(self, player_id: int, material: MagicalMaterial, quantity: float):
        """
        Remove a specific quantity of a magical material from a player's inventory.
        """
        if player_id not in self.inventory or material not in self.inventory[player_id]:
            raise ValueError(f"Player {player_id} does not have {material.value}.")
        if self.inventory[player_id][material] < quantity:
            raise ValueError(f"Player {player_id} does not have enough {material.value} to remove.")
        self.inventory[player_id][material] -= quantity
        if self.inventory[player_id][material] == 0:
            del self.inventory[player_id][material]

    def trade_material(
        self,
        seller_id: Optional[int],
        buyer_id: Optional[int],
        material: MagicalMaterial,
        quantity: float,
        transaction_type: TransactionType,
        date: date,
        details: Optional[str] = None
    ):
        """
        Handle trading of a specific quantity of magical materials between two players and record the transaction.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        # Handle seller's inventory
        if seller_id is not None:
            if seller_id not in self.inventory or material not in self.inventory[seller_id]:
                raise ValueError(f"Seller {seller_id} does not have {material.value}.")
            if self.inventory[seller_id][material] < quantity:
                raise ValueError(f"Seller {seller_id} does not have enough {material.value} to trade.")
            self.remove_material(seller_id, material, quantity)

        # Handle buyer's inventory
        if buyer_id is not None:
            self.assign_material(buyer_id, material, quantity)

        # Record the transaction
        transaction = Transaction(
            seller_id=seller_id,
            buyer_id=buyer_id,
            material=material,
            quantity=quantity,
            transaction_type=transaction_type,
            details=details,
            date=date
        )
        self.transaction_log.add_transaction(transaction)

    def get_inventory(self, player_id: int) -> dict[MagicalMaterial, float]:
        """
        Get the inventory of magical materials and their quantities for a specific player.
        """
        return self.inventory.get(player_id, {})

    def get_transaction_history(self) -> List[Transaction]:
        """
        Get the full transaction history.
        """
        return self.transaction_log.transactions

    def get_transactions_for_player(self, player_id: int) -> List[Transaction]:
        """
        Get the transaction history for a specific player.
        """
        return self.transaction_log.query_by_player(player_id)

    def get_transactions_for_material(self, material: MagicalMaterial) -> List[Transaction]:
        """
        Get the transaction history for a specific magical material.
        """
        return self.transaction_log.query_by_material(material)


# Example Usage
if __name__ == "__main__":
    manager = MagicalMaterialsManager()

    # Assign materials to players
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 500)
    manager.assign_material(2, MagicalMaterial.MOONSHARD_SILVER, 300)

    # Print initial inventories
    print("Player 1 Inventory:", manager.get_inventory(1))
    print("Player 2 Inventory:", manager.get_inventory(2))

    # Trade materials with date
    manager.trade_material(
        seller_id=1,
        buyer_id=2,
        material=MagicalMaterial.EBONSTONE,
        quantity=200,
        transaction_type=TransactionType.TRADE,
        date=date(2025, 1, 4),
        details="Traded for a magical charm."
    )

    # Print inventories after trade
    print("Player 1 Inventory After Trade:", manager.get_inventory(1))
    print("Player 2 Inventory After Trade:", manager.get_inventory(2))

    # Query transactions
    print("Transaction History:", manager.get_transaction_history())
    print("Transactions for Player 2:", manager.get_transactions_for_player(2))
    print("Transactions for Ebonstone:", manager.get_transactions_for_material(MagicalMaterial.EBONSTONE))