import hashlib
import time

class Block:
    def __init__(self, index, data, prev_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(f"{self.index}{self.timestamp}{self.data}{self.prev_hash}".encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, {"info": "Genesis Block"}, "0")

    def add_block(self, data):
        last = self.chain[-1]
        block = Block(len(self.chain), data, last.hash)
        self.chain.append(block)

    def get_product_history(self, product_id):
        return [b for b in self.chain if b.data.get("product_id") == product_id]
