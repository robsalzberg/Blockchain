import hashlib
import requests

import sys


# TODO: Implement functionality to search for a proof 
def proof_of_work(last_proof):
    # Proof of Work Algorithm
    # Find a number p such that hash(last_block_string, p) contains 6 leading zeros
    print("Starting work on a new proof...")
    proof = 0

    while valid_proof(last_proof, proof) is False:
        proof += 1
    
    print("Attempting to mine")    

    return proof


def valid_proof(last_block_string, proof):
    """
    Does hash(last_proof_string, proof) contain 6 leading zeroes?
    """
    # build string to hash
    guess = f"{last_block_string}{proof}".encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    # use hash function
    beg = guess_hash[0:6]

    # check if 6 leading 0's in hash result
    if beg == "000000":
        return True
    else:
        return False
    

if __name__ == '__main__':
    # What node are we interacting with?
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    coins_mined = 0
    # Run forever until interrupted
    while True:
        #Get the last proof from the server

        # TODO: Generate request with /last_block_string
        # HINT: check out "Making a GET request" at
        # https://www.geeksforgeeks.org/get-post-requests-using-python
        r = requests.get(url = node + '/last_block_string')
        data = r.json()
        last_block_string = data["last_block_string"]['previous_hash']

        # Look for next proof based on results from above request
        print(last_block_string)
        new_proof = proof_of_work(last_block_string)
        
# When next proof found, POST it to the server {'proof': new_proof}

# The server will validate our results, ensuring this proof was not

# already submitted.  If valid, it will create a new block & reward
        # us with a coin.
         
        # We're going to have to research how to do a POST in Python
        # HINT: Research `requests` and remember we're sending our data as JSON
        proof_data = {'proof': new_proof}
        r = requests.post(url = node + '/mine', json=proof_data)
        data = r.json()
        # Also send ID so miner gets credit for their work.

        # If the server responds with 'New Block Forged'
        # add 1 to the number of coins mined (for THIS client)
        # and print it.  Otherwise,  the message from the server.
        if data.get('message') == 'New Block Forged':
            coins_mined += 1
            print('You have:' + str(coins_mined) + 'coins')
        print(data.get('message'))
