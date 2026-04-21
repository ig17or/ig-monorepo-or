//SPDX-License-Identifier:GPL-3.0-or-later
pragma solidity 0.8.28;

interface iNnn{
	function rebase(uint256)external returns(bool);
	function totalSupply()external view returns(uint256);
}

interface iOracleManifold{
	function getPriceEstimated()external view returns(uint256,bool);
}

interface iPoolUniswap{
	function sync()external;
}

interface iPoolBalancer{
	function gulp(address)external;
}

contract foreshadow{

	event rebased(uint256 price,uint256 totalSupply);
	event newOwner(address owner);
	event newWeightScaler(uint256 weight,uint256 scaler);
	event newPriceThreshold(uint256 threshold);

	address public owner;
	address public nnn;
	address public oracleManifold;
	address[]public poolsUniswap;
	address[]public poolsBalancer;
	uint256 public rebasePrevious;
	uint256 public rebaseSpacer;
	uint128 constant private uint128max=type(uint128).max;
	uint8 constant private decimals=9;
	uint256 constant private one=10**decimals;
	uint256 constant public priceTarget=9990000000;
	uint256 public counterWeight;
	uint256 public volumeScaler;
	uint256 public priceThreshold;
	uint256 public rebasesBehind=0;

	modifier onlyOwner(){
		require(msg.sender==owner);
		_;
	}

	modifier nonContract(){
		require(msg.sender==tx.origin,'non contract only');
		_;
	}

    constructor(address _oracleManifold,uint256 spacer,uint256 weight,uint256 scaler,uint256 threshold){
		owner=msg.sender;
		oracleManifold=_oracleManifold;
		rebaseSpacer=spacer;
		counterWeight=weight;
		volumeScaler=scaler;
		priceThreshold=threshold;
    }

	function syncPools()public nonContract{
		uint256 poolsUniswapLen=poolsUniswap.length;
		if(poolsUniswapLen>0){
			for(uint256 i=0;i<poolsUniswapLen;i++){
				iPoolUniswap(poolsUniswap[i]).sync();
			}
		}
		uint256 poolsBalancerLen=poolsBalancer.length;
		if(poolsBalancerLen>0){
			for(uint256 i=0;i<poolsBalancerLen;i++){
				iPoolBalancer(poolsBalancer[i]).gulp(nnn);
			}
		}
	}

	function getTsDelta(uint256 nnnTotalSupply,uint256 priceDelta)internal view returns(uint256){
		require(priceDelta>=priceThreshold,'too minor price change');
		return nnnTotalSupply*priceDelta/priceTarget;
	}

	function volumeScale(uint256 tsDelta)internal view returns(uint256){
		return tsDelta*volumeScaler/one;
	}

	function getAdjustedSupply()internal view returns(uint256,uint256){
		(uint256 priceEstimated,bool correct)=iOracleManifold(oracleManifold).getPriceEstimated();
		require(correct,'incorrect oracle output');
		uint256 nnnTotalSupply=iNnn(nnn).totalSupply();
		uint256 adjustedSupply=0;
		if(priceEstimated>priceTarget){
			uint256 priceDelta=priceEstimated-priceTarget;
			uint256 tsDelta=getTsDelta(nnnTotalSupply,priceDelta);
			adjustedSupply=nnnTotalSupply+volumeScale(tsDelta);
		}else if(priceTarget>priceEstimated){
			uint256 priceDelta=priceTarget-priceEstimated;
			uint256 tsDelta=getTsDelta(nnnTotalSupply,priceDelta);
			tsDelta=tsDelta*counterWeight/one;
			adjustedSupply=nnnTotalSupply-volumeScale(tsDelta);
		}else{
			revert('price is target');
		}
		if(adjustedSupply>uint128max){
			adjustedSupply=uint128max;
		}
		return(priceEstimated,adjustedSupply);
	}

	function rebase(bool sync)external nonContract{
		require(block.number>=rebasePrevious+rebaseSpacer,'too soon');
		rebasePrevious=block.number;
		rebasesBehind+=1;
		(uint256 priceEstimated,uint256 adjustedSupply)=getAdjustedSupply();
		emit rebased(priceEstimated,adjustedSupply);
		require(iNnn(nnn).rebase(adjustedSupply),'rebase error');
		if(sync){
			syncPools();
		}
	}

	function editPoolsUniswap(bool add,address pool,uint256 poolI)external onlyOwner{
		if(add){
			poolsUniswap.push(pool);
		}else{
			poolsUniswap[poolI]=poolsUniswap[poolsUniswap.length-1];
			poolsUniswap.pop();
		}
	}

	function editPoolsBalancer(bool add,address pool,uint256 poolI)external onlyOwner{
		if(add){
			poolsBalancer.push(pool);
		}else{
			poolsBalancer[poolI]=poolsBalancer[poolsBalancer.length-1];
			poolsBalancer.pop();
		}
	}

	function setRebaseSpacer(uint256 spacer)external onlyOwner{
		rebaseSpacer=spacer;
	}

	function setWeightScaler(uint256 weight,uint256 scaler)external onlyOwner{
		counterWeight=weight;
		volumeScaler=scaler;
		emit newWeightScaler(weight,scaler);
	}

	function setPriceThreshold(uint256 threshold)external onlyOwner{
		priceThreshold=threshold;
		emit newPriceThreshold(threshold);
	}

	function setNnn(address _nnn)external onlyOwner{
		nnn=_nnn;
	}

	function setOracleManifold(address _oracleManifold)external onlyOwner{
		oracleManifold=_oracleManifold;
	}

	function setOwner(address _owner)external onlyOwner{
		require(_owner!=address(0),'address0');
		owner=_owner;
		emit newOwner(owner);
	}

}