import datetime
import hashlib                                                          # hash-function
import json
import os
from flask import Flask, jsonify
import time
import random
from Crypto.PublicKey import RSA                                        # 1. symmetric&asymmetric encrypting
from Crypto.Cipher import AES, PKCS1_OAEP
import nacl.signing                                                     # 2. simple and powerful service for encrypting
import nacl.secret
import nacl.utils
from ecdsa import SigningKey, NIST384p                                  # 3. create signatures (based on curves...) for encrypting
import brownie                                                          # for working with smart-contracts
from blake3 import blake3

#from eth_brownie import network, accounts, config
#from web3 import Web3                                                  # helps to connect python&ethereum !and it helps handle the consensuses - doesn't work somewhy


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
        hasher = blake3()
        hasher.update(guess)
        guess_hash = hasher.hexdigest() # sha256 -> BLAKE3
        return guess_hash[:4] == "0000"

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hasher = blake3()
            hasher.update(str(proof ** 2 - previous_proof ** 2).encode())
            hasher.hexdigest()
            if hasher[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def new_block(self, proof, previous_hash):  # here we have to add some conditions from LLM(from version block)!!!!!!!!!!!!!!!!!!!!!!!!!!!
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block): # creating hash-function
        hasher = blake3()
        block_string = json.dumps(block, sort_keys=True).encode()
        hasher.update(block_string)
        return hasher.hexdigest() # sha256 -> BLAKE3

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


class PoTBlockchain:
    def __init__(self, delay_time=60, complexity=1000000):
        self.delay_time = delay_time                                    # define the delay time in seconds
        self.complexity = complexity                                    # allows us to control the complexity of computation of blocks
        self.access_tracker = {}                                        # vocabulary for controlling users&their accesses

    def request_access(self, user_id):                                  # allows to have accesses to some data for users for the voc.
        if user_id in self.access_tracker:
            last_access_time, _ = self.access_tracker[user_id]
            if (time.time() - last_access_time) < self.delay_time:
                return False, "Access denied. Please wait."
        self.access_tracker[user_id] = (time.time(), self.verifiable_delay_function(user_id)) # update the  last entire (or introduce the user)
        return True, "Access granted!"

    def verifiable_delay_function(self, input_value):
        hasher = blake3()                                               # hasher-function
        current_hash = input_value.encode()
        random_seed = os.urandom(16)
        hasher.update(random_seed)                                      # make the hashing with random seed for improving condifence/secrutiry

        for _ in range(int(self.delay_time * self.complexity)):         # define the delay
            hasher.update(current_hash)
            current_hash = hasher.digest()                              # take the current hash

        final_hash = hasher.digest()
        return final_hash, time.time()

    def validate_delay(self, original_input, result_hash, expected_time):
        recreated_hash, actual_time = self.verifiable_delay_function(original_input)
        return recreated_hash == result_hash and actual_time >= expected_time           # True = validation is succeed, False = losing any rewards

    def validate_access(self, user_id):                                 # additional function (for accessibility)
        if user_id not in self.access_tracker:
            return False, "No access request found."
        last_access_time, result_hash = self.access_tracker[user_id]
        expected_time = last_access_time + self.delay_time
        if time.time() >= expected_time:
            return True, f"Access validation passed. Hash: {result_hash.hex()}"
        return False, "Time delay requirement not met yet."

'''
#test
pot = PoTBlockchain(delay_time=3, complexity=1000000)  # time:5min & complexity:1M
input_data = "Here we can write the massage!"
result_hash, time_taken = pot.verifiable_delay_function(input_data)
print(f"Hash: {result_hash.hex()}")
print(f"Time taken: {time_taken} seconds")
is_valid = pot.validate_delay(input_data, result_hash, time_taken)          # it has to output: "Failed" - cause of random.seed
print("Validation result:", "passed" if is_valid else "failed")


pot = PoTBlockchain(delay_time=3)
user_id = "user123"
access, message = pot.request_access(user_id)
print(message)

blockchain = BlockchainPoW() # or another class to add...

'''


'''


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



'''
