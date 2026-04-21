//SPDX-License-Identifier:GPL-3.0-or-later
pragma solidity 0.8.28;

interface iNnn{
    function transfer(address to, uint256 value)external returns(bool);
    function transferFrom(address from,address to, uint256 value)external returns(bool);
	function totalSupply()external view returns(uint256);
}

contract wnnn{

	event Transfer(address indexed _from,address indexed _to,uint256 _value);
	event Approval(address indexed _owner,address indexed _spender,uint256 _value);

	address public immutable nnn;
    string constant public symbol='wNNN';
    string constant public name='wrapped Nine Ninety Nine';
	string constant private exceedsBalance='exceeds balance';
	uint8 constant public decimals=9;
    mapping(address=>uint256)public balanceOf;
	uint256 public constant maxSupplyWnnn=10**7*10**decimals;
    uint256 public totalSupply;
    mapping(address=>mapping(address=>uint256))public allowance;

    modifier nonContract(){
		require(msg.sender==tx.origin);
		_;
	}

    constructor(address _nnn){
		require(_nnn!=address(0),'address0');
		nnn=_nnn;
    }

	function ensureTransfer(bool result)internal pure{
		require(result,'NNN transfer failed');
	}

	function nnnTs()internal view returns(uint256){
		return iNnn(nnn).totalSupply();
	}

	function wrap(uint256 amountNnn)external nonContract{
		uint256 amountWnnn=amountNnn*maxSupplyWnnn/nnnTs();
		totalSupply+=amountWnnn;
		balanceOf[msg.sender]+=amountWnnn;
		ensureTransfer(iNnn(nnn).transferFrom(msg.sender,address(this),amountNnn));
	}

	function unwrap(uint256 amountWnnn)external nonContract{
		require(balanceOf[msg.sender]>=amountWnnn,exceedsBalance);
		uint256 amountNnn=amountWnnn*nnnTs()/maxSupplyWnnn;
		balanceOf[msg.sender]-=amountWnnn;
		totalSupply-=amountWnnn;
		ensureTransfer(iNnn(nnn).transfer(msg.sender,amountNnn));
	}

	function _transfer(address from,address to,uint256 amount)internal{
		require(balanceOf[from]>=amount,exceedsBalance);
		balanceOf[from]-=amount;
		balanceOf[to]+=amount;
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

}