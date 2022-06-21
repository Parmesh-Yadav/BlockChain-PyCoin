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

    def addTransactions(self,sender,receiver,amount):
        self.transactions.append({'sender':sender,'receiver':receiver,'amount':amount})
        #previousBlock = self.getPreviousBlock
        #return previousBlock['index'] + 1
        return len(self.chain) + 1
    
    def addNode(self,address):
        parsedURL = urlparse(address)#divides the URL into different components.
        self.nodes.add(parsedURL.netloc)#we use only the netloc i.e. "127.0.0.1:5000".

    def createBlock(self, proof, previousHash):
        block = {'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previousHash': previousHash,
            'transactions':self.transactions}
        self.transactions = []#clear the mempool
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
#app.debug = True

# Creating an address for the node on Port 5000

nodeAddress = str(uuid4()).replace('-','')

# Creating a blockchain object.

blockchain = BlockChain()

# Mining a new block

@app.route('/mine_block', methods=['GET'])
def mineBlock():
    previousBlock = blockchain.getPreviousBlock()
    previousProof = previousBlock['proof']
    proof = blockchain.proofOfWork(previousProof)
    previousHash = blockchain.hash(previousBlock)
    blockchain.addTransactions(nodeAddress,'Vaasu',100)
    #reward given to the miner when they succesfully mine a block is also a transaction.
    blockAdded = blockchain.createBlock(proof, previousHash)
    response = {'message':'Congratulations, Block successfully mined!!',
        'index':blockAdded['index'],
        'timestamp':blockAdded['timestamp'],
        'proof':blockAdded['proof'],
        'previousHash':blockAdded['previousHash'],
        'transactions':blockAdded['transactions']}
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

# Adding a new transaction to the blockchain.

@app.route('/add_transaction',methods=['POST'])
def addTransaction():
    json = request.get_json()
    transactionKeys = ['sender','receiver','amount']
    if not all(key in json for key in transactionKeys):#just to check if the transactions are in correct form.
        return 'Transaction elements missing',400#bad request
    index = blockchain.addTransactions(json['sender'],json['receiver'],json['amount'])
    response = {'message':f'This transaction will be added to block {index}'}
    return jsonify(response), 201#for creation

#part 3 Decentralizing our blockcchain.

#connecting new nodes

@app.route('/connect_node',methods=['POST'])
def connectNodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No Nodes',400
    for node in nodes:
        blockchain.addNode(node)
    response = {'message':'All nodes successfully connected','totalNodes':list(blockchain.nodes)}
    return jsonify(response),201

#replacing the chain by the longest chain if needed

@app.route('/replace_chain',methods=['GET'])
def replaceChain():
    isChainReplaced = blockchain.replaceChain()
    if isChainReplaced:
        response = {'message':'Nodes had different chains. Existing chain was replaced by the longest one in the network','newChain':blockchain.chain}
    else:
        response = {'message':'Everything is fine. Existing chain is the longest chain in the network.','ExistingChain':blockchain.chain}
    return jsonify(response),200

# running the actual app

app.run(host='0.0.0.0', port=5002)
# this address of the host makes the app publicly available
