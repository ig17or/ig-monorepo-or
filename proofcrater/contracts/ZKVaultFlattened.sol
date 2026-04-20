// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity =0.8.30 >=0.4.16 ^0.8.20;

// openzeppelin/contracts/utils/Context.sol

// OpenZeppelin Contracts (last updated v5.0.1) (utils/Context.sol)

/**
 * @dev Provides information about the current execution context, including the
 * sender of the transaction and its data. While these are generally available
 * via msg.sender and msg.data, they should not be accessed in such a direct
 * manner, since when dealing with meta-transactions the account sending and
 * paying for execution may not be the actual sender (as far as an application
 * is concerned).
 *
 * This contract is only required for intermediate, library-like contracts.
 */
abstract contract Context {
    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }

    function _msgData() internal view virtual returns (bytes calldata) {
        return msg.data;
    }

    function _contextSuffixLength() internal view virtual returns (uint256) {
        return 0;
    }
}

// openzeppelin/contracts/token/ERC20/IERC20.sol

// OpenZeppelin Contracts (last updated v5.4.0) (token/ERC20/IERC20.sol)

/**
 * @dev Interface of the ERC-20 standard as defined in the ERC.
 */
interface IERC20 {
    /**
     * @dev Emitted when `value` tokens are moved from one account (`from`) to
     * another (`to`).
     *
     * Note that `value` may be zero.
     */
    event Transfer(address indexed from, address indexed to, uint256 value);

    /**
     * @dev Emitted when the allowance of a `spender` for an `owner` is set by
     * a call to {approve}. `value` is the new allowance.
     */
    event Approval(address indexed owner, address indexed spender, uint256 value);

    /**
     * @dev Returns the value of tokens in existence.
     */
    function totalSupply() external view returns (uint256);

    /**
     * @dev Returns the value of tokens owned by `account`.
     */
    function balanceOf(address account) external view returns (uint256);

    /**
     * @dev Moves a `value` amount of tokens from the caller's account to `to`.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transfer(address to, uint256 value) external returns (bool);

    /**
     * @dev Returns the remaining number of tokens that `spender` will be
     * allowed to spend on behalf of `owner` through {transferFrom}. This is
     * zero by default.
     *
     * This value changes when {approve} or {transferFrom} are called.
     */
    function allowance(address owner, address spender) external view returns (uint256);

    /**
     * @dev Sets a `value` amount of tokens as the allowance of `spender` over the
     * caller's tokens.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * IMPORTANT: Beware that changing an allowance with this method brings the risk
     * that someone may use both the old and the new allowance by unfortunate
     * transaction ordering. One possible solution to mitigate this race
     * condition is to first reduce the spender's allowance to 0 and set the
     * desired value afterwards:
     * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
     *
     * Emits an {Approval} event.
     */
    function approve(address spender, uint256 value) external returns (bool);

    /**
     * @dev Moves a `value` amount of tokens from `from` to `to` using the
     * allowance mechanism. `value` is then deducted from the caller's
     * allowance.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

// openzeppelin/contracts/utils/ReentrancyGuard.sol

// OpenZeppelin Contracts (last updated v5.1.0) (utils/ReentrancyGuard.sol)

/**
 * @dev Contract module that helps prevent reentrant calls to a function.
 *
 * Inheriting from `ReentrancyGuard` will make the {nonReentrant} modifier
 * available, which can be applied to functions to make sure there are no nested
 * (reentrant) calls to them.
 *
 * Note that because there is a single `nonReentrant` guard, functions marked as
 * `nonReentrant` may not call one another. This can be worked around by making
 * those functions `private`, and then adding `external` `nonReentrant` entry
 * points to them.
 *
 * TIP: If EIP-1153 (transient storage) is available on the chain you're deploying at,
 * consider using {ReentrancyGuardTransient} instead.
 *
 * TIP: If you would like to learn more about reentrancy and alternative ways
 * to protect against it, check out our blog post
 * https://blog.openzeppelin.com/reentrancy-after-istanbul/[Reentrancy After Istanbul].
 */
abstract contract ReentrancyGuard {
    // Booleans are more expensive than uint256 or any type that takes up a full
    // word because each write operation emits an extra SLOAD to first read the
    // slot's contents, replace the bits taken up by the boolean, and then write
    // back. This is the compiler's defense against contract upgrades and
    // pointer aliasing, and it cannot be disabled.

    // The values being non-zero value makes deployment a bit more expensive,
    // but in exchange the refund on every call to nonReentrant will be lower in
    // amount. Since refunds are capped to a percentage of the total
    // transaction's gas, it is best to keep them low in cases like this one, to
    // increase the likelihood of the full refund coming into effect.
    uint256 private constant NOT_ENTERED = 1;
    uint256 private constant ENTERED = 2;

    uint256 private _status;

    /**
     * @dev Unauthorized reentrant call.
     */
    error ReentrancyGuardReentrantCall();

    constructor() {
        _status = NOT_ENTERED;
    }

    /**
     * @dev Prevents a contract from calling itself, directly or indirectly.
     * Calling a `nonReentrant` function from another `nonReentrant`
     * function is not supported. It is possible to prevent this from happening
     * by making the `nonReentrant` function external, and making it call a
     * `private` function that does the actual work.
     */
    modifier nonReentrant() {
        _nonReentrantBefore();
        _;
        _nonReentrantAfter();
    }

    function _nonReentrantBefore() private {
        // On the first call to nonReentrant, _status will be NOT_ENTERED
        if (_status == ENTERED) {
            revert ReentrancyGuardReentrantCall();
        }

        // Any calls to nonReentrant after this point will fail
        _status = ENTERED;
    }

    function _nonReentrantAfter() private {
        // By storing the original value once again, a refund is triggered (see
        // https://eips.ethereum.org/EIPS/eip-2200)
        _status = NOT_ENTERED;
    }

    /**
     * @dev Returns true if the reentrancy guard is currently set to "entered", which indicates there is a
     * `nonReentrant` function in the call stack.
     */
    function _reentrancyGuardEntered() internal view returns (bool) {
        return _status == ENTERED;
    }
}

// openzeppelin/contracts/access/Ownable.sol

// OpenZeppelin Contracts (last updated v5.0.0) (access/Ownable.sol)

/**
 * @dev Contract module which provides a basic access control mechanism, where
 * there is an account (an owner) that can be granted exclusive access to
 * specific functions.
 *
 * The initial owner is set to the address provided by the deployer. This can
 * later be changed with {transferOwnership}.
 *
 * This module is used through inheritance. It will make available the modifier
 * `onlyOwner`, which can be applied to your functions to restrict their use to
 * the owner.
 */
abstract contract Ownable is Context {
    address private _owner;

    /**
     * @dev The caller account is not authorized to perform an operation.
     */
    error OwnableUnauthorizedAccount(address account);

    /**
     * @dev The owner is not a valid owner account. (eg. `address(0)`)
     */
    error OwnableInvalidOwner(address owner);

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /**
     * @dev Initializes the contract setting the address provided by the deployer as the initial owner.
     */
    constructor(address initialOwner) {
        if (initialOwner == address(0)) {
            revert OwnableInvalidOwner(address(0));
        }
        _transferOwnership(initialOwner);
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier onlyOwner() {
        _checkOwner();
        _;
    }

    /**
     * @dev Returns the address of the current owner.
     */
    function owner() public view virtual returns (address) {
        return _owner;
    }

    /**
     * @dev Throws if the sender is not the owner.
     */
    function _checkOwner() internal view virtual {
        if (owner() != _msgSender()) {
            revert OwnableUnauthorizedAccount(_msgSender());
        }
    }

    /**
     * @dev Leaves the contract without owner. It will not be possible to call
     * `onlyOwner` functions. Can only be called by the current owner.
     *
     * NOTE: Renouncing ownership will leave the contract without an owner,
     * thereby disabling any functionality that is only available to the owner.
     */
    function renounceOwnership() public virtual onlyOwner {
        _transferOwnership(address(0));
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Can only be called by the current owner.
     */
    function transferOwnership(address newOwner) public virtual onlyOwner {
        if (newOwner == address(0)) {
            revert OwnableInvalidOwner(address(0));
        }
        _transferOwnership(newOwner);
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Internal function without access restriction.
     */
    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
}

// ZKVault.sol

interface IVerifier {
    struct G1Point {
        uint256 X;
        uint256 Y;
    }

    struct G2Point {
        uint256[2] X;
        uint256[2] Y;
    }

    struct Proof {
        G1Point a;
        G2Point b;
        G1Point c;
    }

    function verifyTx(Proof memory proof, uint256[5] memory input) external view returns (bool);
}

contract ZKVault is Ownable, ReentrancyGuard {
    enum DepositEnum {
        UNAUTHORIZED_DEPOSITOR,
        UNSUPPORTED_TOKEN,
        EXCEEDS_ALLOWANCE,
        EXCEEDS_BALANCE,
        DEPOSIT_EXISTS,
        INVALID_AMOUNT,
        SUCCESS
    }

    enum WithdrawEnum {
        DEPOSIT_DOESNT_EXIST,
        USED_NULLIFIER,
        ZK_NOT_VERIFIED,
        SUCCESS
    }

    struct LimitStruct {
        uint256 gas;
        uint256 refuel;
    }

    struct DepositStruct {
        address token;
        uint256 amount;
    }

    LimitStruct public limits;

    mapping(uint256 => DepositStruct) public deposits;
    mapping(uint256 => bool) public usedNullifiers;
    mapping(address => bool) public approvedDepositors;
    mapping(address => bool) public approvedTokens;

    uint256 private constant ONE = 1000000;
    uint256 public gasStipend;
    uint256 public fee;

    address public immutable verifier;
    address public relayer;

    string public title;

    bool public stopped;

    event deposited(address depositor, address token, uint256 amountToken, uint256 amountFee);
    event withdrawn(address recipient, address token, uint256 amountToken, uint256 amountEth);

    error depositFailed(uint8 errorCode);

    modifier onlyRelayer() {
        require(msg.sender == relayer, "not relayer");
        _;
    }

    modifier notStopped() {
        require(!stopped, "stopped");
        _;
    }

    constructor(
        address _verifier,
        string memory _title,
        address _relayer,
        uint256 _gasStipend,
        uint256 _fee,
        LimitStruct memory _limits
    ) Ownable(msg.sender) {
        verifier = _verifier;
        title = _title;
        relayer = _relayer;
        gasStipend = _gasStipend;
        fee = _fee;
        limits = _limits;
    }

    function isDepositable(address depositor, uint256 root, address tokenAddr, uint256 amount)
        public
        view
        returns (DepositEnum)
    {
        if (!approvedDepositors[depositor]) return DepositEnum.UNAUTHORIZED_DEPOSITOR;
        if (!approvedTokens[tokenAddr]) return DepositEnum.UNSUPPORTED_TOKEN;
        IERC20 token = IERC20(tokenAddr);
        if (token.allowance(depositor, address(this)) < amount) return DepositEnum.EXCEEDS_ALLOWANCE;
        if (token.balanceOf(depositor) < amount) return DepositEnum.EXCEEDS_BALANCE;
        if (deposits[root].amount != 0) return DepositEnum.DEPOSIT_EXISTS;
        if (amount == 0) return DepositEnum.INVALID_AMOUNT;
        return DepositEnum.SUCCESS;
    }

    function calcFee(uint256 gross, uint256 _fee) internal pure returns (uint256, uint256) {
        uint256 feeAmount = gross * _fee / ONE;
        uint256 net = gross - feeAmount;
        return (net, feeAmount);
    }

    function deposit(address depositor, uint256 root, address tokenAddr, uint256 amount)
        external
        onlyRelayer
        notStopped
        nonReentrant
    {
        require(isDepositable(depositor, root, tokenAddr, amount) == DepositEnum.SUCCESS, "deposit validation failed");
        (uint256 netDeposit, uint256 feeAmount) = calcFee(amount, fee);
        deposits[root] = DepositStruct(tokenAddr, netDeposit);
        IERC20 token = IERC20(tokenAddr);
        uint256 balanceBefore = token.balanceOf(address(this));
        require(token.transferFrom(depositor, address(this), amount), "erc20 transferFrom failed");
        require(token.balanceOf(address(this)) - balanceBefore >= amount, "funds deposit incorrect");
        require(token.transfer(owner(), feeAmount), "erc20 transfer failed");
        emit deposited(depositor, tokenAddr, netDeposit, feeAmount);
    }

    function isWithdrawable(IVerifier.Proof calldata proof, uint256[5] calldata inputs)
        public
        view
        returns (WithdrawEnum)
    {
        if (deposits[inputs[0]].token == address(0)) return WithdrawEnum.DEPOSIT_DOESNT_EXIST;
        if (usedNullifiers[inputs[1]]) return WithdrawEnum.USED_NULLIFIER;
        if (!IVerifier(verifier).verifyTx(proof, inputs)) return WithdrawEnum.ZK_NOT_VERIFIED;
        return WithdrawEnum.SUCCESS;
    }

    function transferToken(uint256 root, address recipient, uint256 amount) internal returns (address) {
        DepositStruct memory d = deposits[root];
        IERC20 token = IERC20(d.token);
        require(token.balanceOf(address(this)) >= amount, "insolvent contract");
        require(token.transfer(recipient, amount), "erc20 transfer failed");
        return d.token;
    }

    function refuel(address payable targetAccount) internal returns (uint256) {
        uint256 amountToRefuel = gasStipend * tx.gasprice;
        if (targetAccount.balance < amountToRefuel) {
            require(amountToRefuel <= limits.refuel, "refuel overlimited");
            uint256 gap = amountToRefuel - targetAccount.balance;
            if (address(this).balance < gap) return 0;
            (bool success,) = targetAccount.call{value: gap, gas: limits.gas}("");
            return success ? gap : 0;
        }
        return 0;
    }

    function withdraw(IVerifier.Proof calldata proof, uint256[5] calldata inputs)
        external
        onlyRelayer
        notStopped
        nonReentrant
    {
        require(isWithdrawable(proof, inputs) == WithdrawEnum.SUCCESS, "not withdrawable");
        usedNullifiers[inputs[1]] = true;
        uint256 amountToken = inputs[2];
        address recipient = address(uint160(inputs[3]));
        address token = transferToken(inputs[0], recipient, amountToken);
        uint256 refueled = refuel(payable(recipient));
        emit withdrawn(recipient, token, amountToken, refueled);
    }

    function setStop(bool _stopped) external onlyOwner {
        stopped = _stopped;
    }

    function setDepositor(address _depositer, bool _state) external onlyOwner {
        approvedDepositors[_depositer] = _state;
    }

    function setToken(address _token, bool _state) external onlyOwner {
        approvedTokens[_token] = _state;
    }

    function setRelayer(address _relayer) external onlyOwner {
        relayer = _relayer;
    }

    function setLimits(LimitStruct calldata _limits) external onlyOwner {
        limits = _limits;
    }

    function setFee(uint256 _fee) external onlyOwner {
        fee = _fee;
    }

    function setGasStipend(uint256 _gasStipend) external onlyOwner {
        gasStipend = _gasStipend;
    }

    receive() external payable {}

    function withdrawGasAmount(uint256 amount) external onlyOwner {
        require(address(this).balance >= amount, "insufficient balance");
        (bool success,) = payable(owner()).call{value: amount}("");
        require(success, "transfer failed");
    }
}

