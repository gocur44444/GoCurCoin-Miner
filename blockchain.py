import hashlib
import time
import json
from ecdsa import SigningKey, VerifyingKey, SECP256k1

MINING_REWARD = 50
DIFFICULTY = 3  # number of leading zeros required in hash

class Transaction:
    def __init__(self, sender_pubkey, recipient_pubkey, amount, signature=None):
        self.sender = sender_pubkey
        self.recipient = recipient_pubkey
        self.amount = amount
        self.signature = signature

    def to_dict(self):
        return {
            'sender': self.sender.to_string().hex() if self.sender else None,
            'recipient': self.recipient.to_string().hex(),
            'amount': self.amount,
            'signature': self.signature.hex() if self.signature else None
        }

    def sign(self, private_key):
        message = f"{self.sender.to_string().hex() if self.sender else None}{self.recipient.to_string().hex()}{self.amount}".encode()
        self.signature = private_key.sign(message)

    def verify(self):
        if self.sender is None:  # mining reward tx
            return True
        message = f"{self.sender.to_string().hex()}{self.recipient.to_string().hex()}{self.amount}".encode()
        try:
            return self.sender.verify(self.signature, message)
        except:
            return False

class Block:
    def __init__(self, index, transactions, prev_hash, nonce=0, timestamp=None):
        self.index = index
        self.transactions = transactions  # list of Transaction objects
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.timestamp = timestamp or time.time()

    def compute_hash(self):
        tx_data = json.dumps([tx.to_dict() for tx in self.transactions], sort_keys=True)
        block_string = f"{self.index}{self.prev_hash}{self.nonce}{self.timestamp}{tx_data}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []  # list of pending transactions
        self.utxos = {}  # maps pubkey_hex -> balance
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_tx = Transaction(None, VerifyingKey.generate(curve=SECP256k1), 1000)
        genesis_block = Block(0, [genesis_tx], "0")
        genesis_hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        self.utxos[genesis_tx.recipient.to_string().hex()] = genesis_tx.amount

    def add_transaction(self, tx):
        if not tx.verify():
            print("Invalid transaction signature.")
            return False
        sender_hex = tx.sender.to_string().hex() if tx.sender else None
        if sender_hex:
            sender_balance = self.utxos.get(sender_hex, 0)
            if sender_balance < tx.amount:
                print("Insufficient balance.")
                return False
        self.mempool.append(tx)
        return True

    def mine_block(self, miner_pubkey):
        # Add mining reward tx
        reward_tx = Transaction(None, miner_pubkey, MINING_REWARD)
        block_txs = self.mempool + [reward_tx]

        last_block = self.chain[-1]
        new_block = Block(last_block.index + 1, block_txs, last_block.compute_hash())
        
        # Proof of work
        while not new_block.compute_hash().startswith('0' * DIFFICULTY):
            new_block.nonce += 1

        # Add block to chain
        self.chain.append(new_block)

        # Update UTXOs
        for tx in block_txs:
            sender = tx.sender.to_string().hex() if tx.sender else None
            recipient = tx.recipient.to_string().hex()

            if sender:
                self.utxos[sender] = self.utxos.get(sender, 0) - tx.amount
            self.utxos[recipient] = self.utxos.get(recipient, 0) + tx.amount

        # Clear mempool
        self.mempool = []

        print(f"Block #{new_block.index} mined with nonce {new_block.nonce}")
        print(f"Block hash: {new_block.compute_hash()}")
        print(f"Miner rewarded {MINING_REWARD} coins")

    def get_balance(self, pubkey):
        key_hex = pubkey.to_string().hex()
        return self.utxos.get(key_hex, 0)