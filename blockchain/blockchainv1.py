import datetime
import hashlib                          # hash-function
import json
from flask import Flask, jsonify
import time
import random
from Crypto.PublicKey import RSA        # 1. symmetric&asymmetric encrypting
from Crypto.Cipher import AES, PKCS1_OAEP
import nacl.signing                     # 2. simple and powerful service for encrypting
import nacl.secret
import nacl.utils
from ecdsa import SigningKey, NIST384p  # 3. create signatures (based on curves...) for encrypting
import brownie                          # for working with smart-contracts

import blake2b
#from eth_brownie import network, accounts, config
#from web3 import Web3                   # helps to connect python&ethereum !and it helps handle the consensuses - doesn't work somewhy




class BlockchainPoW:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash="1", proof=100) # defined with initial number and amount of proofs for transactions

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest() # sha256 -> BLAKE2/3
        return guess_hash[:4] == "0000"

    def new_block(self, proof, previous_hash):  # here we have to add some conditions from LLM(from version block)!!!!!!!!!!!!!!!!!!!!!!!!!!!
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block): # creating hash-function
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest() # sha256 -> BLAKE2/3

class PoSBlockchain:
    def __init__(self):
        super().__init__()
        self.stake = {"address1": 100, "address2": 200}  # key=who, value= how many

    def proof_of_stake(self):                       # 1. introduce handling&LLM here
        total_stake = sum(self.stake.values())
        choice = random.randint(1, total_stake)
        current = 0
        for address, stake in self.stake.items():
            current += stake
            if current >= choice:
                return address

    def new_block(self, proof, previous_hash):      # 2. introduce handling&LLM here
        miner_address = self.proof_of_stake()
        super().new_block(proof, previous_hash) # reward miner based on stake
        print(f"Block mined by: {miner_address}")

class DPoSBlockchain:
    def __init__(self):
        super().__init__()
        self.delegates = ["address1", "address2"]  # elected to delegate for creating blocks

    def proof_of_stake(self): # they will be chosen randomly (or, maybe for the future we can define them somehow else, like reputation)
        delegate = random.choice(self.delegates)
        return delegate

class PoRBlockchain:
    def __init__(self):
        super().__init__()
        self.reputation = {"address1": 50, "address2": 75} # the same idea as staking

    def proof_of_reputation(self):
        total_reputation = sum(self.reputation.values())
        choice = random.randint(1, total_reputation)
        current = 0
        for address, rep in self.reputation.items():
            current += rep
            if current >= choice:
                return address

    def new_block(self, proof, previous_hash):
        miner_address = self.proof_of_reputation()
        super().new_block(proof, previous_hash)     # rewarding
        print(f"Block mined by: {miner_address}")





# take the core idea from the blockchain_course code and remove..
'''
class Blockchain_General:

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_block(proof=100, previous_hash='1')

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
'''

blockchain = BlockchainPoW() # or another class to add...


def blake2b_hash(data): # BLAKE2-hashing
    hasher = hashlib.blake2b(digest_size=32)  # You can specify the digest size
    hasher.update(data.encode('utf-8'))
    return hasher.hexdigest()


####################I was not doing anything with this part of code###########################################

# Creating a Web App
app = Flask(__name__)


@app.route('/mine_block', methods=['GET'])
def mine_block(): # mining a new block
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain(): # Getting the full Blockchain
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200



@app.route('/is_valid', methods=['GET'])
def is_valid(): # Checking if the Blockchain is valid
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


# Running the app
app.run(host='0.0.0.0', port=5000)
