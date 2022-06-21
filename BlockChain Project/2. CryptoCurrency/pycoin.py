# step 1 : creating a blockchain.

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# part 1 : Building a Blockchain.


class BlockChain:

    def __init__(self):
        self.chain = []
        self.transactions = []#similar to mempool. Transactions are saved here before going into a block.
        self.createBlock(1, '0')
        self.nodes = set()#set of network locations of all the connected nodes in the network.

    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys=True).encode()
        # dumps convert a json.dictionary in to a string.
        return hashlib.sha256(encodedBlock).hexdigest()

    def addTransactions(self,sender,reciever,amount):
        self.transactions.append({'sender':sender,'reciever':reciever,'amount':amount})
        previousBlock = self.getPreviousBlock
        return previousBlock['index'] + 1
        #return len(self.chain) + 1
    
    def addNode(self,address):
        parsedURL = urlparse(address)#divides the URL into different components.
        self.nodes.add(parsedURL.netloc)#we use only the netloc i.e. "127.0.0.1:5000".

    def createBlock(self, proof, previousHash):
        block = {'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previousHash': previousHash,
            'transactions':self.transactions}
        self.transactions = []
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

    def replaceChain(self):
        network = self.nodes
        longestChain = None
        maxLength = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain') #make a GET request to get the chain and length of every node one by one.
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > maxLength and self.isChainValid(chain):
                    maxLength = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False


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
        response ={'message':'Everything is fine. BlockChain is valid.'}
    return jsonify(response),200

# running the actual app

app.run(host='0.0.0.0', port=5000)
# this address of the host makes the app publicly available