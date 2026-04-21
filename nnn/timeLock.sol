//SPDX-License-Identifier:MIT
pragma solidity 0.8.28;

contract timeLock{

    event Deposit(address indexed sender,uint256 amount,uint256 balance);
    event SubmitTransaction(
        address indexed owner,
        uint256 indexed txIndex,
        address indexed to,
        uint256 value,
        bytes data
    );
    event ExecuteTransaction(address indexed owner,uint256 indexed txIndex);

    struct Transaction{
        address to;
        uint256 value;
        bytes data;
        bool executed;
        uint256 timestamp;
    }

    Transaction[]public transactions;
    address public immutable owner;
    uint256 public immutable delay;

    modifier onlyOwner(){
        require(msg.sender==owner,"not owner");
        _;
    }

    modifier txExists(uint256 _txIndex){
        require(_txIndex<transactions.length,"tx does not exist");
        _;
    }

    modifier notExecuted(uint256 _txIndex){
        require(!transactions[_txIndex].executed,"tx already executed");
        _;
    }

    constructor(uint256 _delay){
        owner=msg.sender;
        delay=_delay;
    }

    receive()external payable{
        emit Deposit(msg.sender,msg.value,address(this).balance);
    }

    function submitTransaction(address _to,uint256 _value,bytes memory _data)external onlyOwner{
        uint256 txIndex=transactions.length;
        transactions.push(
            Transaction({
                to:_to,
                value:_value,
                data:_data,
                executed:false,
                timestamp:block.timestamp
            })
        );
        emit SubmitTransaction(msg.sender,txIndex,_to,_value,_data);
    }

    function executeTransaction(uint256 _txIndex)external onlyOwner txExists(_txIndex) notExecuted(_txIndex){
        Transaction storage transaction=transactions[_txIndex];
        require(block.timestamp>=transaction.timestamp+delay,"cannot execute tx");
        transaction.executed=true;
        emit ExecuteTransaction(msg.sender,_txIndex);
        (bool success,)=transaction.to.call{value:transaction.value}(transaction.data);
        require(success,"tx failed");
    }

    function getTransactionCount()external view returns(uint256){
        return transactions.length;
    }

    function getTransaction(uint256 _txIndex)external view returns(address,uint256,bytes memory,bool,uint256){
        Transaction memory transaction=transactions[_txIndex];
        return(
            transaction.to,
            transaction.value,
            transaction.data,
            transaction.executed,
            transaction.timestamp
        );
    }
    
}