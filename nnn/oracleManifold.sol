//SPDX-License-Identifier:GPL-3.0-or-later
pragma solidity 0.8.28;

contract oracleManifold{

	event newOwner(address owner);
	event newDelays(uint256 min,uint256 max);

	struct Observation{
		uint256 price;
		uint256 Block;
	}

    mapping(address=>Observation)public oracleObservation;
	mapping(address=>bool)public oracleApproved;
	address[]public oracleList;
	address public owner;
	uint256 public delayMin;
	uint256 public delayMax;

	modifier onlyOwner(){
		require(msg.sender==owner,'not owner');
		_;
	}

	constructor(uint256 min,uint256 max){
		owner=msg.sender;
		delayMin=min;
		delayMax=max;
	}

	function getPriceAvg(uint256 a,uint256 b)internal pure returns(uint256){
		return (a+b)/2;
	}

	function getPriceMedian(uint256[]memory prices,uint256 len)internal pure returns(uint256){
		uint256 key=0;
		int256 j=0;
		for(uint256 i=1;i<len;i++){
			key=prices[i];
			j=int256(i)-1;
			while(j>=0&&key<prices[uint256(j)]){
				prices[uint256(j+1)]=prices[uint256(j)];
				j-=1;
			}
			prices[uint256(j+1)]=key;
		}
		uint256 middlePos=len/2;
		if(len%2==1){
			return prices[middlePos];
		}else{
			return getPriceAvg(prices[middlePos-1],prices[middlePos]);
		}
	}

	function getPriceEstimated()external view returns(uint256,bool){
		uint256 oracleListLen=oracleList.length;
		uint256[]memory prices=new uint256[](oracleListLen);
		uint256 len=0;
		uint256 blockNumber=block.number;
		for(uint256 i=0;i<oracleListLen;i++){
			Observation memory observation=oracleObservation[oracleList[i]];
			bool conditionLow=blockNumber>=observation.Block+delayMin;
			bool conditionHigh=blockNumber<=observation.Block+delayMax;
			if(conditionLow&&conditionHigh){
				prices[len]=observation.price;
				len+=1;
			}
		}
		if(len==0){
			return(0,false);
		}else if(len==1){
			return(prices[0],true);
		}else if(len==2){
			return(getPriceAvg(prices[0],prices[1]),true);
		}else{
			return(getPriceMedian(prices,len),true);
		}
	}

	function uploadPrice(uint256 price)external{
		require(oracleApproved[msg.sender],'not approved oracle');
		oracleObservation[msg.sender]=Observation(price,block.number);
	}

	function oracleManage(bool add,address oracle,uint256 oracleI)external onlyOwner{
		if(add){
			require(!oracleApproved[oracle],'already approved');
			oracleList.push(oracle);
			oracleApproved[oracle]=true;
		}else{
			oracleApproved[oracleList[oracleI]]=false;
			oracleList[oracleI]=oracleList[oracleList.length-1];
			oracleList.pop();
		}
	}

	function setDelays(uint256 min,uint256 max)external onlyOwner{
		delayMin=min;
		delayMax=max;
		emit newDelays(delayMin,delayMax);
	}

	function setOwner(address _owner)external onlyOwner{
		require(_owner!=address(0),'address0');
		owner=_owner;
		emit newOwner(owner);
	}

}