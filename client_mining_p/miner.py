import hashlib
import requests

import sys


# TODO: Implement functionality to search for a proof 
def proof_of_work(self, last_proof):
    """
    Proof of Work Algorithm
    Find a number p such that hash(last_block_string, p) contains 6 leading
    zeroes
    """

    proof = 0

    while self.valid_proof(last_proof, proof) is False:
        proof += 1

    return proof


def valid_proof(last_proof, proof):
    """
    Does hash(block_string, proof) contain 6 leading zeroes?
    """
    # build string to hash
    guess = f"{last_proof}{proof}".encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    # use hash function
    beginning = guess_hash[:6]

    # check if 6 leading 0's in hash result
    if beginning == "000000":
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
        # TODO: Get the last proof from the server and look for a new one
        r = requests.get(url=node + "/last_proof")
        # TODO: When found, POST it to the server {"proof": new_proof}
        # the data is extracted in JSON format
        data = r.json()

        last_proof = data["last_proof"]

        new_proof = proof_of_work(last_proof)
        # TODO: We're going to have to research how to do a POST in Python
        # HINT: Research `requests` and remember we're sending our data as JSON
        proof_request = {"proof": new_proof}
        r = requests.post(url=node + "/mine", json=proof_request)
        print(r.json()["message"])
        # TODO: If the server responds with 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        if r.json()["message"] == "New Block Forged":
            mined += 1
            print("The total number of Lambda Coins mined is: ", mined)
