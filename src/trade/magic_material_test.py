import pytest
from datetime import date
from src.trade.magic_material import (
    MagicalMaterialsManager,
    MagicalMaterial,
    TransactionType,
    Transaction
)


@pytest.fixture
def manager():
    """
    Fixture to initialize the MagicalMaterialsManager for testing.
    """
    return MagicalMaterialsManager()


def test_assign_material(manager):
    """
    Test assigning magical materials to a player's inventory.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 500)
    assert manager.get_inventory(1) == {MagicalMaterial.EBONSTONE: 500}


def test_assign_material_multiple_times(manager):
    """
    Test assigning the same material multiple times adds to the quantity.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 300)
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 200)
    assert manager.get_inventory(1) == {MagicalMaterial.EBONSTONE: 500}


def test_remove_material(manager):
    """
    Test removing a magical material from a player's inventory.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 500)
    manager.remove_material(1, MagicalMaterial.EBONSTONE, 200)
    assert manager.get_inventory(1) == {MagicalMaterial.EBONSTONE: 300}


def test_remove_material_entire_quantity(manager):
    """
    Test removing the entire quantity of a magical material.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 500)
    manager.remove_material(1, MagicalMaterial.EBONSTONE, 500)
    assert manager.get_inventory(1) == {}


def test_remove_material_insufficient_quantity(manager):
    """
    Test removing more quantity than available raises an error.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 300)
    with pytest.raises(ValueError, match="Player 1 does not have enough Ebonstone to remove."):
        manager.remove_material(1, MagicalMaterial.EBONSTONE, 400)


def test_trade_material(manager):
    """
    Test trading magical materials between players.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 500)
    manager.trade_material(
        seller_id=1,
        buyer_id=2,
        material=MagicalMaterial.EBONSTONE,
        quantity=200,
        transaction_type=TransactionType.TRADE,
        date=date(2025, 1, 4),
        details="A friendly trade."
    )

    assert manager.get_inventory(1) == {MagicalMaterial.EBONSTONE: 300}
    assert manager.get_inventory(2) == {MagicalMaterial.EBONSTONE: 200}
    assert len(manager.get_transaction_history()) == 1


def test_trade_material_insufficient_quantity(manager):
    """
    Test trading a material when the seller has insufficient quantity raises an error.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 100)
    with pytest.raises(ValueError, match="Seller 1 does not have enough Ebonstone to trade."):
        manager.trade_material(
            seller_id=1,
            buyer_id=2,
            material=MagicalMaterial.EBONSTONE,
            quantity=200,
            transaction_type=TransactionType.TRADE,
            date=date(2025, 1, 4)
        )


def test_trade_material_no_seller(manager):
    """
    Test trading a material without a seller (e.g., barter).
    """
    manager.trade_material(
        seller_id=None,
        buyer_id=2,
        material=MagicalMaterial.EBONSTONE,
        quantity=300,
        transaction_type=TransactionType.BARTER,
        date=date(2025, 1, 4),
        details="Inherited from a fallen hero."
    )

    assert manager.get_inventory(2) == {MagicalMaterial.EBONSTONE: 300}
    assert len(manager.get_transaction_history()) == 1


def test_transaction_log(manager):
    """
    Test transaction log contains all transactions with correct details.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 500)
    manager.trade_material(
        seller_id=1,
        buyer_id=2,
        material=MagicalMaterial.EBONSTONE,
        quantity=200,
        transaction_type=TransactionType.TRADE,
        date=date(2025, 1, 4),
        details="A trade in the market."
    )
    manager.trade_material(
        seller_id=None,
        buyer_id=3,
        material=MagicalMaterial.MOONSHARD_SILVER,
        quantity=100,
        transaction_type=TransactionType.GIFT,
        date=date(2025, 1, 5),
        details="A gift from the goddess."
    )

    transactions = manager.get_transaction_history()
    assert len(transactions) == 2

    assert transactions[0] == Transaction(
        seller_id=1,
        buyer_id=2,
        material=MagicalMaterial.EBONSTONE,
        quantity=200,
        transaction_type=TransactionType.TRADE,
        date=date(2025, 1, 4),
        details="A trade in the market."
    )

    assert transactions[1] == Transaction(
        seller_id=None,
        buyer_id=3,
        material=MagicalMaterial.MOONSHARD_SILVER,
        quantity=100,
        transaction_type=TransactionType.GIFT,
        date=date(2025, 1, 5),
        details="A gift from the goddess."
    )


def test_query_transactions_by_player(manager):
    """
    Test querying transactions by a specific player.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 500)
    manager.trade_material(
        seller_id=1,
        buyer_id=2,
        material=MagicalMaterial.EBONSTONE,
        quantity=200,
        transaction_type=TransactionType.TRADE,
        date=date(2025, 1, 4),
        details="A trade in the market."
    )
    manager.trade_material(
        seller_id=None,
        buyer_id=2,
        material=MagicalMaterial.SHADOWGLASS,
        quantity=100,
        transaction_type=TransactionType.GIFT,
        date=date(2025, 1, 5),
        details="A divine gift."
    )

    transactions = manager.get_transactions_for_player(2)
    assert len(transactions) == 2
    assert transactions[0].buyer_id == 2
    assert transactions[1].buyer_id == 2


def test_query_transactions_by_material(manager):
    """
    Test querying transactions by a specific magical material.
    """
    manager.assign_material(1, MagicalMaterial.EBONSTONE, 500)
    manager.trade_material(
        seller_id=1,
        buyer_id=2,
        material=MagicalMaterial.EBONSTONE,
        quantity=200,
        transaction_type=TransactionType.TRADE,
        date=date(2025, 1, 4),
        details="A trade in the market."
    )
    manager.trade_material(
        seller_id=None,
        buyer_id=3,
        material=MagicalMaterial.MOONSHARD_SILVER,
        quantity=100,
        transaction_type=TransactionType.GIFT,
        date=date(2025, 1, 5),
        details="A gift from the goddess."
    )

    transactions = manager.get_transactions_for_material(MagicalMaterial.EBONSTONE)
    assert len(transactions) == 1
    assert transactions[0].material == MagicalMaterial.EBONSTONE