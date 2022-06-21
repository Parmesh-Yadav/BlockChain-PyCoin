# step 1 : creating a blockchain.

import datetime
import hashlib
import json
from flask import Flask, jsonify

# part 1 : Building a Blockchain.


class BlockChain:

    def __init__(self):
        self.chain = []
        self.createBlock(1, '0')

    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys=True).encode()
        # dumps convert a json.dictionary in to a string.
        return hashlib.sha256(encodedBlock).hexdigest()

    def createBlock(self, proof, previousHash):
        block = {'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previousHash': previousHash}
        self.chain.append(block)
        return block

    def getPreviousBlock(self):  # returns the last block of the blockchain.
        return self.chain[-1]

    def proofOfWork(self, previousProof):
        newProof = 1
        checkProof = False
        while checkProof is False:
            hashOperation = hashlib.sha256(str(newProof**3 - previousProof**3).encode()).hexdigest()
            # sha256 expects the argument as a binary encoded string.
            # hexdigest will convert the output of sha256 wihch is hexadecimal into a string.
            # hashOperation is a string of 64 characters.
            if hashOperation[:4] == '0000':
                checkProof = True
            else:
                newProof += 1
        return newProof

    def isChainValid(self, chain):
        previousBlock = chain[0]  # the first block in the blockchain.
        blockIndex = 1  # index starting from the second block.
        while blockIndex < len(chain):
            block = chain[blockIndex]  # saving the current block.
            if block['previousHash'] != self.hash(previousBlock):
                return False
            # proof of the previous block.
            previousProof = previousBlock['proof']
            proof = block['proof']  # proof of the current block.
            hashOperation = hashlib.sha256(str(proof**3 - previousProof**3).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False
            previousBlock = block
            blockIndex += 1
        return True


# part 2 : Mining our Blockchain.

# Creating a web app using flask.

app = Flask(__name__)
app.debug = True

# Creating a blockchain object.

blockchain = BlockChain()

# Mining a new block


@app.route('/mine_block', methods=['GET'])
def mineBlock():
    previousBlock = blockchain.getPreviousBlock()
    previousProof = previousBlock['proof']
    proof = blockchain.proofOfWork(previousProof)
    previousHash = blockchain.hash(previousBlock)
    blockAdded = blockchain.createBlock(proof, previousHash)
    response = {'message':'Congratulations, Block successfully mined!!',
        'index':blockAdded['index'],
        'timestamp':blockAdded['timestamp'],
        'proof':blockAdded['proof'],
        'previousHash':blockAdded['previousHash']}
    return jsonify(response), 200

# Getting the full blockChain

@app.route('/get_chain', methods=['GET'])
def getChain():
    response = {'chain': blockchain.chain,
        'length': len(blockchain.chain)}
    return jsonify(response), 200

#checking if the blockchain is valid or not

@app.route('/is_chain_valid',methods=['GET'])
def isValid():
    isValid = blockchain.isChainValid(blockchain.chain)
    if isValid:
        response ={'message':'Everything is fine. BlockChain is valid.'}
    else:
        response ={'message':'Everything is not fine. BlockChain is invalid.'}
    return jsonify(response),200

# running the actual app

app.run(host='0.0.0.0', port=5000)
# this address of the host makes the app publicly available
