//pycoin ICO

//compiler version
pragma solidity ^0.4.11;

contract pycoinICO {
    uint public maxPyCoin = 10000000; //Max pycoins available for sale.
    uint public USDtoPyCoin =  1000; //USD to pyCoin conversion rate.
    uint public PyCoinBought = 0; //PyCoins bought by the investors.

    mapping(address => uint) PyCoinEquity;
    mapping(address => uint) USDEquity;

    //to check if investor can buy certain amount of PyCoin.
    modifier canBuyPyCoin(uint USD){
        require(USD * USDtoPyCoin + PyCoinBought <= maxPyCoin);
        _;
    }

    //PyCoinEquity of a investor.
    function equityPyCoin(address investor) external constant returns(uint){
        return PyCoinEquity[investor];
    }

    //USDEquity of a investor
    function equityUSD(address investor) external constant returns(uint){
        return USDEquity[investor];
    }

    //Ivestor Buy PyCoin
    function buyPyCoin(address investor,uint USD) external
    canBuyPyCoin(USD){
        uint PyCoins = USD * USDtoPyCoin;
        PyCoinEquity[investor] += PyCoins;
        USDEquity[investor] += PyCoinEquity[investor]/1000;
        PyCoinBought += PyCoins;
    }

    //Investor Selling PyCoin
    function sellPyCoin(address investor,uint PyCoinToSell) external{
        PyCoinEquity[investor] -= PyCoinToSell;
        USDEquity[investor] -= PyCoinEquity[investor]/1000;
        PyCoinBought -= PyCoinToSell;
    }
}