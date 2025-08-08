from ecdsa import SigningKey, SECP256k1

class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    def sign_transaction(self, tx):
        tx.sign(self.private_key)

    def get_address(self):
        return self.public_key.to_string().hex()