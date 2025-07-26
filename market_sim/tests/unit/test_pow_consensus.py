"""
Tests for the Proof of Work consensus mechanism.
"""

import pytest
from datetime import datetime, timedelta
from market_sim.blockchain.consensus.pow import ProofOfWork, Block

def test_genesis_block_creation():
    pow = ProofOfWork(difficulty=2)
    genesis = pow.chain[0]
    
    assert genesis.index == 0
    assert genesis.previous_hash == "0" * 64
    assert len(genesis.hash) == 64
    assert genesis.hash.startswith("0" * pow.difficulty)

def test_mining_block():
    pow = ProofOfWork(difficulty=2)
    
    # Add some test transactions
    test_transactions = [
        {"type": "trade", "amount": 100, "price": 50},
        {"type": "trade", "amount": 200, "price": 51}
    ]
    
    for tx in test_transactions:
        pow.add_transaction(tx)
    
    # Mine the block
    new_block = pow.mine_block()
    
    assert new_block is not None
    assert new_block.index == 1
    assert new_block.previous_hash == pow.chain[0].hash
    assert new_block.hash.startswith("0" * pow.difficulty)
    assert new_block.transactions == test_transactions
    
def test_chain_validation():
    pow = ProofOfWork(difficulty=2)
    
    # Add and mine some blocks
    for i in range(3):
        pow.add_transaction({"data": f"Transaction {i}"})
        pow.mine_block()
    
    assert pow.is_valid_chain()
    
    # Tamper with a transaction
    pow.chain[1].transactions[0]["data"] = "Tampered"
    assert not pow.is_valid_chain()

def test_chain_metrics():
    pow = ProofOfWork(difficulty=2)
    
    # Add some transactions and mine blocks
    for i in range(3):
        pow.add_transaction({"data": f"Transaction {i}"})
        pow.mine_block()
    
    # Add pending transactions
    pow.add_transaction({"data": "Pending 1"})
    pow.add_transaction({"data": "Pending 2"})
    
    metrics = pow.get_chain_metrics()
    
    assert metrics["length"] == 4  # Genesis + 3 mined blocks
    assert metrics["total_transactions"] == 4  # Genesis tx + 3 mined tx
    assert metrics["pending_transactions"] == 2
