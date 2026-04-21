//SPDX-License-Identifier:GPL-3.0-or-later
pragma solidity 0.8.28;

contract nnn{

	event newOwner(address owner);
	event rebased(uint256 totalSupply,uint256 atomsInUnit);
	event Transfer(address indexed _from,address indexed _to,uint256 _value);
	event Approval(address indexed _owner,address indexed _spender,uint256 _value);

    string constant public symbol='NNN';
    string constant public name='Nine Ninety Nine';
	uint8 constant public decimals=9;
	uint256 public totalSupply;
    mapping(address=>mapping(address=>uint256))public allowance;
	address public owner;
	address public foreshadow;
    mapping(address=>uint256)public atomBalances;
	uint256 constant private initSupply=10**6*10**decimals;
	uint128 constant private uint128max=type(uint128).max;
	uint256 constant private totalAtoms=type(uint256).max-(type(uint256).max%initSupply);
	uint256 public atomsInUnit;

	modifier onlyOwner(){
		require(msg.sender==owner);
		_;
	}

    constructor(address _foreshadow){
		owner=msg.sender;
		totalSupply=initSupply;
		atomBalances[owner]=totalAtoms;
		atomsInUnit=totalAtoms/totalSupply;
		foreshadow=_foreshadow;
    }

    function balanceOf(address user)external view returns(uint256){
        return atomBalances[user]/atomsInUnit;
    }

	function rebase(uint256 _totalSupply)external returns(bool){
		require(msg.sender==foreshadow,'not foreshadow');
		require(_totalSupply<=uint128max,'uint128 overflow');
		totalSupply=_totalSupply;
		atomsInUnit=totalAtoms/totalSupply;
		emit rebased(totalSupply,atomsInUnit);
		return true;
	}

	function approve(address spender,uint256 amount)external returns(bool){
		allowance[msg.sender][spender]=amount;
		emit Approval(msg.sender,spender,amount);
		return true;
	}

	function increaseAllowance(address spender,uint256 amount)external returns(bool){
		allowance[msg.sender][spender]+=amount;
		emit Approval(msg.sender,spender,allowance[msg.sender][spender]);
        return true;
    }

	function decreaseAllowance(address spender,uint256 amount)external returns(bool){
		if(allowance[msg.sender][spender]>amount){
			allowance[msg.sender][spender]-=amount;
		}else{
			allowance[msg.sender][spender]=0;
		}
		emit Approval(msg.sender,spender,allowance[msg.sender][spender]);
        return true;
	}

	function _transfer(address from,address to,uint256 amount)internal{
		uint256 atomAmount=amount*atomsInUnit;
		require(atomBalances[from]>=atomAmount,'exceeds balance');
		atomBalances[from]-=atomAmount;
		atomBalances[to]+=atomAmount;
	}

	function transfer(address to,uint256 amount)external returns(bool){
		_transfer(msg.sender,to,amount);
		emit Transfer(msg.sender,to,amount);
		return true;
	}

	function transferFrom(address from,address to,uint256 amount)external returns(bool){
		require(allowance[from][msg.sender]>=amount,'exceeds allowance');
		_transfer(from,to,amount);
		allowance[from][msg.sender]-=amount;
		emit Transfer(from,to,amount);
		return true;
	}

	function setOwner(address _owner)external onlyOwner{
		require(_owner!=address(0),'address0');
		owner=_owner;
		emit newOwner(owner);
	}

	function setForeshadow(address _foreshadow)external onlyOwner{
		foreshadow=_foreshadow;
	}

}