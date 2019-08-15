import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from urllib.parse import urlparse
import requests

import sys


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # self.new_block(proof=99, previous_hash = 1)
        if len(self.chain) == 0:
            self.create_genesis_block()

    def create_genesis_block(self):
        block = {
            'index': 1,
            'timestamp': 0,
            'transactions': [],
            'proof': 5381,
            'previous': 1
        }
        self.chain.append(block)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the BLock that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_block_string, proof):
        """
        Validates the Proof:  Does hash(last_proof, proof) 
        contain 6 leading zeroes?
        """
        # build string to hash
        guess = f'{last_block_string}{proof}'.encode()
        # use hash function
        guess_hash = hashlib.sha256(guess).hexdigest()
        # check if 6 leading 0's in hash result
        beg = guess_hash[0:6]
        if beg == "000000":
            return True
        else:
            return False

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def broadcast_new_block(self, new_block):
        neighbors = self.nodes
        post_data = {'block': block}

        for node in neighbors:
            r = request.post(f'http://{node}/block/new', json = post_data)

        if response .status_code != 200:
            # TODO: Error handling

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-------------------\n")
            # Check that the hash of the block is correct
            # TODO: Return false if hash isn't correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Check that the Proof of Work is correct
            # TODO: Return false if proof isn't correct
            if not self.valid_proof(last_block["proof"], block["proof"]):
                return False

            last_block = block
            current_index += 1

        return True

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# Modify the `mine` endpoint to instead receive and validate or reject a new proof sent by a client.
# Return a message indicating success or failure. Remember, a valid proof should fail for all senders except the first.


@app.route('/mine', methods=['POST', 'GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    # proof = blockchain.proof_of_work(blockchain.last_block)

    values = request.get_json()

    required = ['proof']

    if not all(k in values for k in required):
        return "Missing values", 400

    if not blockchain.valid_proof(blockchain.last_block['previous_hash'], values['proof']):
        response = {'message': 'Proof is not valid'}

        return jsonify(response), 200

    # We must receive a reward for finding the proof.
    # TODO:
    # The sender is "0" to signify that this node has mine a new coin
    # The recipient is the current node, it did the mining!
    # The amount is 1 coin as a reward for mining the next block
    # new_transaction(self, sender, recipient, amount):
    blockchain.new_transaction(0, node_identifier, 1)

    # Forge the new Block by adding it to the chain
    # When creating a new block, the new block function is expecting to
    # receive the valid proof and the previous hash of the last block.
    block = blockchain.new_block(
        values['proof'], blockchain.hash(blockchain.last_block))
    blockchain.broadcast_new_block(block)    

    # Send a response with the new block
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'], }

    return jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return "Missing Values", 400
    # Create a new Transaction
    index = blockchain.new_transaction(
        values["sender"], values["recipient"], values["amount"])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        "currentChain": blockchain.chain,
        "length": len(blockchain.chain), }

    return jsonify(response), 200

# Add an endpoint called `last_proof` that returns the `proof` of the last block in the chain
@app.route("/last_block_string", methods=["GET"])
def last_block_string():
    response = {
        'last_block_string': blockchain.last_block
    }

    return jsonify(response), 200


@app.route('/nodes/register', method=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values['nodes']

    if nodes is None:
        return 'Error, please supply node info', 400
    for n in nodes:
        blockchain.register_node(n)

    response = {
        'message': 'New nodes added successfully!',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/block/new/': methods=['POST'])
def receive_block():
    values = request.get_json()

    # validation
    new_block = values['block']
    old_block = Blockchain.last_block

    if new_block['index'] == old_block['index'] + 1:
        if new_block['previous_hash'] == Blockchain.hash(old_block):
            block_string = json.dump(old_block, sort_keys=True).encode()
            if blockchain.valid_proof(block_string, new_block['proof'])
                print('New block added!')
                blockchain.add(new_block)
                return 'Block Accepted', 200
            else:
                # TODO: Proof of workis invalid
        else:
            # TODO: Previous hash is invalid
    else:
        # TODO: Indexes are not consecutive
        
# Run the program on port 5000
if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run(host='localhost', port=5000)
