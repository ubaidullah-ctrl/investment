"""
Visualization tools for blockchain analysis.
"""

import matplotlib.pyplot as plt
from typing import List, Dict
from datetime import datetime
import networkx as nx
from blockchain.consensus.pow import Block, ProofOfWork

class BlockchainVisualizer:
    @staticmethod
    def plot_chain_structure(pow: ProofOfWork):
        """
        Create a visual representation of the blockchain structure
        using networkx.
        """
        G = nx.DiGraph()
        
        # Add nodes and edges
        for block in pow.chain:
            G.add_node(block.hash[:8], 
                      timestamp=block.timestamp,
                      transactions=len(block.transactions))
            if block.index > 0:
                G.add_edge(block.previous_hash[:8], block.hash[:8])
        
        # Create the plot
        plt.figure(figsize=(15, 8))
        pos = nx.spring_layout(G)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                             node_size=1000, alpha=0.6)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                             arrows=True, arrowsize=20)
        
        # Add labels
        labels = {node: f"Block {idx}\n{node}" 
                 for idx, node in enumerate(G.nodes())}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title("Blockchain Structure")
        plt.axis('off')
        return plt

    @staticmethod
    def plot_mining_metrics(pow: ProofOfWork):
        """
        Plot metrics about block mining times and transaction counts.
        """
        blocks = pow.chain[1:]  # Skip genesis block
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Block Mining Times
        mining_times = []
        for i in range(1, len(blocks)):
            time_diff = (blocks[i].timestamp - blocks[i-1].timestamp).total_seconds()
            mining_times.append(time_diff)
        
        ax1.plot(range(1, len(blocks)), mining_times, marker='o')
        ax1.set_title('Block Mining Times')
        ax1.set_xlabel('Block Number')
        ax1.set_ylabel('Time (seconds)')
        ax1.grid(True)
        
        # Plot 2: Transactions per Block
        tx_counts = [len(block.transactions) for block in blocks]
        ax2.bar(range(1, len(blocks) + 1), tx_counts)
        ax2.set_title('Transactions per Block')
        ax2.set_xlabel('Block Number')
        ax2.set_ylabel('Transaction Count')
        ax2.grid(True)
        
        plt.tight_layout()
        return plt

    @staticmethod
    def plot_chain_metrics(pow: ProofOfWork):
        """
        Plot various blockchain metrics over time.
        """
        metrics = pow.get_chain_metrics()
        
        plt.figure(figsize=(10, 6))
        plt.bar(['Chain Length', 'Total Transactions', 'Pending Transactions'],
                [metrics['length'], metrics['total_transactions'], 
                 metrics['pending_transactions']])
        
        plt.title('Blockchain Metrics')
        plt.ylabel('Count')
        plt.grid(True)
        return plt
