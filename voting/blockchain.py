# blockchain.py

from .models import Block as BlockModel, Transaction as TransactionModel
import hashlib
import datetime

class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = str(self.index) + self.previous_hash + str(self.timestamp) + str(self.transactions) + str(self.nonce)
        return hashlib.sha256(data.encode()).hexdigest()

    def save_to_db(self):
        block_model = BlockModel.objects.create(
            index=self.index,
            previous_hash=self.previous_hash,
            timestamp=self.timestamp,
            nonce=self.nonce,
            hash=self.hash
        )
        for transaction in self.transactions:
            TransactionModel.objects.create(
                block=block_model,
                voter=transaction['voter'],
                candidate=transaction['candidate']
            )

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "0", datetime.datetime.now(), "Genesis Block")

    def add_block(self, new_block):
        new_block.previous_hash = self.chain[-1].hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)
        new_block.save_to_db()

    def proof_of_work(self, block):
        while block.hash[:4] != "0000":
            block.nonce += 1
            block.hash = block.calculate_hash()
        return block.hash

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True
