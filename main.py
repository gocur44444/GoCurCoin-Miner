from blockchain import Blockchain, Transaction
from wallet import Wallet

bc = Blockchain()

# Create wallets
alice = Wallet()
bob = Wallet()
miner = Wallet()

print("Alice address:", alice.get_address())
print("Bob address:", bob.get_address())
print("Miner address:", miner.get_address())

print(f"Alice initial balance: {bc.get_balance(alice.public_key)}")
print(f"Bob initial balance: {bc.get_balance(bob.public_key)}")

# Create and sign a transaction: Alice sends 200 coins to Bob
tx1 = Transaction(alice.public_key, bob.public_key, 200)
alice.sign_transaction(tx1)

if bc.add_transaction(tx1):
    print("Transaction added to mempool")

# Miner mines a block and gets reward
bc.mine_block(miner.public_key)

print(f"Alice balance after mining: {bc.get_balance(alice.public_key)}")
print(f"Bob balance after mining: {bc.get_balance(bob.public_key)}")
print(f"Miner balance after mining: {bc.get_balance(miner.public_key)}")