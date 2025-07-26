"""
Complex market simulation with blockchain integration demo.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict
import random
from blockchain.consensus.pow import ProofOfWork
from analysis.visualization.blockchain_viz import BlockchainVisualizer
from core.models.base import Order, Trade, OrderSide, OrderType
from market.exchange.matching_engine import MatchingEngine
import matplotlib.pyplot as plt

class MarketSimulator:
    def __init__(self, symbol: str, blockchain_difficulty: int = 3):
        self.symbol = symbol
        self.matching_engine = MatchingEngine(symbol)
        self.blockchain = ProofOfWork(difficulty=blockchain_difficulty)
        self.price_history: List[Dict] = []
        
    def initialize_order_book(self, base_price: Decimal, num_orders: int = 5):
        """Initialize order book with some limit orders around base price."""
        spread = Decimal('0.001')  # 0.1% spread
        
        # Add ask orders above base price
        for i in range(num_orders):
            price = base_price * (1 + spread * (i + 1))
            quantity = Decimal(str(random.uniform(1.0, 5.0)))
            order = Order.create_limit_order(
                self.symbol, OrderSide.SELL, quantity, price, "market_maker_1"
            )
            self.matching_engine.process_order(order)
            
        # Add bid orders below base price
        for i in range(num_orders):
            price = base_price * (1 - spread * (i + 1))
            quantity = Decimal(str(random.uniform(1.0, 5.0)))
            order = Order.create_limit_order(
                self.symbol, OrderSide.BUY, quantity, price, "market_maker_1"
            )
            self.matching_engine.process_order(order)
        
    def generate_hft_orders(self, base_price: Decimal, volatility: float, num_orders: int) -> List[Order]:
        """Generate HFT-style orders with small price variations."""
        orders = []
        for _ in range(num_orders):
            # Random price variation within volatility range
            price_change = random.uniform(-volatility, volatility)
            price = base_price * (1 + Decimal(str(price_change)))
            
            # Alternate between buy and sell orders
            side = OrderSide.BUY if random.random() > 0.5 else OrderSide.SELL
            
            # Small order sizes typical of HFT
            quantity = Decimal(str(random.uniform(0.1, 1.0)))
            
            # Mix of limit and market orders
            order_type = OrderType.LIMIT if random.random() > 0.3 else OrderType.MARKET
            
            order = Order.create_market_order(
                self.symbol, side, quantity, "hft_agent_1"
            ) if order_type == OrderType.MARKET else Order.create_limit_order(
                self.symbol, side, quantity, price, "hft_agent_1"
            )
            
            orders.append(order)
        return orders
        
    def generate_institutional_orders(self, base_price: Decimal, num_orders: int) -> List[Order]:
        """Generate large institutional-style orders."""
        orders = []
        for _ in range(num_orders):
            # Larger price variations for institutional orders
            price_change = random.uniform(-0.02, 0.02)
            price = base_price * (1 + Decimal(str(price_change)))
            
            # Large order sizes
            quantity = Decimal(str(random.uniform(10.0, 100.0)))
            
            # Mostly limit orders for institutional trades
            side = OrderSide.BUY if random.random() > 0.5 else OrderSide.SELL
            
            order = Order.create_limit_order(
                self.symbol, side, quantity, price, "institutional_agent_1"
            )
            
            orders.append(order)
        return orders
        
    def process_orders_and_record(self, orders: List[Order]):
        """Process orders and record trades in blockchain."""
        for order in orders:
            # Process the order through matching engine
            trades = self.matching_engine.process_order(order)
            
            # Record trades in blockchain
            for trade in trades:
                trade_data = {
                    "type": "trade",
                    "symbol": trade.symbol,
                    "price": float(trade.price),
                    "quantity": float(trade.quantity),
                    "agent_id": order.agent_id,
                    "side": order.side.value,
                    "timestamp": trade.timestamp.isoformat()
                }
                self.blockchain.add_transaction(trade_data)
                
                # Record price for history
                self.price_history.append({
                    "timestamp": trade.timestamp,
                    "price": float(trade.price),
                    "quantity": float(trade.quantity)
                })
            
            # Mine a new block after every few trades
            if len(self.blockchain.pending_transactions) >= 3:
                self.blockchain.mine_block()

def main():
    # Initialize simulation
    print("Initializing market simulation...")
    sim = MarketSimulator("BTC/USD", blockchain_difficulty=3)
    base_price = Decimal("45000")
    
    # Initialize order book with some liquidity
    print("\nInitializing order book with liquidity...")
    sim.initialize_order_book(base_price)
    
    # Generate and process HFT orders
    print("\nGenerating and processing HFT orders...")
    hft_orders = sim.generate_hft_orders(base_price, 0.001, 10)  # 0.1% volatility
    sim.process_orders_and_record(hft_orders)
    
    # Generate and process institutional orders
    print("\nGenerating and processing institutional orders...")
    inst_orders = sim.generate_institutional_orders(base_price, 5)
    sim.process_orders_and_record(inst_orders)
    
    # Create visualizations
    print("\nGenerating visualizations...")
    
    # 1. Blockchain Structure
    print("1. Blockchain Structure Visualization")
    BlockchainVisualizer.plot_chain_structure(sim.blockchain)
    plt.savefig('complex_blockchain_structure.png')
    plt.close()
    
    # 2. Price History
    print("2. Price History Visualization")
    plt.figure(figsize=(12, 6))
    prices = [p['price'] for p in sim.price_history]
    plt.plot(range(len(prices)), prices, marker='o')
    plt.title('Price History with Mixed HFT and Institutional Trading')
    plt.xlabel('Trade Number')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.savefig('price_history.png')
    plt.close()
    
    # 3. Trade Size Distribution
    print("3. Trade Size Distribution Visualization")
    plt.figure(figsize=(10, 6))
    quantities = [p['quantity'] for p in sim.price_history]
    plt.hist(quantities, bins=20)
    plt.title('Trade Size Distribution')
    plt.xlabel('Trade Size')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig('trade_size_distribution.png')
    plt.close()
    
    # Print simulation statistics
    print("\nSimulation Statistics:")
    print(f"Total trades executed: {len(sim.price_history)}")
    print(f"Total blocks mined: {len(sim.blockchain.chain)}")
    print(f"Average trade size: {sum(quantities) / len(quantities):.2f}")
    
    print("\nVisualizations have been saved as PNG files.")

if __name__ == "__main__":
    main()
