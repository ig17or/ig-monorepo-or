// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.8.34;

contract CommitmentBank {
    enum RevealEnum {
        MessageTooLong,
        CommitmentNotFound,
        AlreadyRevealed,
        InvalidRevealProof,
        SUCCESS
    }

    uint256 public constant MAX_MESSAGE_LENGTH = 10240;

    struct Commitment {
        uint64 timestamp;
        bool revealed;
        string revealedMessage;
    }

    address public owner;
    uint256 public commitFee;

    mapping(address => mapping(uint256 => Commitment)) public userCommitment;
    mapping(address => uint256[]) private userCommitments;

    event Committed(address user, uint256 id);
    event Revealed(address user, uint256 id, string message);

    constructor(uint256 _initialFee) {
        owner = msg.sender;
        commitFee = _initialFee;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Unauthorized");
        _;
    }

    function commit(uint256 id) external payable {
        require(msg.value >= commitFee, "InsufficientFee");
        require(userCommitment[msg.sender][id].timestamp == 0, "CommitmentExists");
        userCommitment[msg.sender][id] =
            Commitment({timestamp: uint64(block.timestamp), revealed: false, revealedMessage: ""});
        userCommitments[msg.sender].push(id);
        emit Committed(msg.sender, id);
    }

    function _isRevealableWithData(address user, uint256 id, string calldata message)
        internal
        view
        returns (RevealEnum, Commitment storage)
    {
        if (bytes(message).length > MAX_MESSAGE_LENGTH) {
            return (RevealEnum.MessageTooLong, userCommitment[user][id]);
        }
        Commitment storage c = userCommitment[user][id];
        if (c.timestamp == 0) return (RevealEnum.CommitmentNotFound, c);
        if (c.revealed) return (RevealEnum.AlreadyRevealed, c);
        uint256 computed = uint256(keccak256(abi.encode(message)));
        if (computed != id) return (RevealEnum.InvalidRevealProof, c);
        return (RevealEnum.SUCCESS, c);
    }

    function isRevealable(address user, uint256 id, string calldata message) public view returns (RevealEnum) {
        (RevealEnum result,) = _isRevealableWithData(user, id, message);
        return result;
    }

    function reveal(uint256 id, string calldata message) external {
        (RevealEnum status, Commitment storage c) = _isRevealableWithData(msg.sender, id, message);
        require(status == RevealEnum.SUCCESS, "NotRevealable");
        c.revealed = true;
        c.revealedMessage = message;
        emit Revealed(msg.sender, id, message);
    }

    function getUserCommitments(address user, uint256 from, uint256 to)
        external
        view
        returns (uint256[] memory, Commitment[] memory)
    {
        uint256 len = to - from;
        uint256[] memory ids = new uint256[](len);
        Commitment[] memory commitments = new Commitment[](len);
        uint256 j = 0;
        for (uint256 i = from; i < to; i++) {
            uint256 id = userCommitments[user][i];
            ids[j] = id;
            commitments[j] = userCommitment[user][id];
            j++;
        }
        return (ids, commitments);
    }

    function userCommitmentsCounter(address user) external view returns (uint256) {
        return userCommitments[user].length;
    }

    function setFee(uint256 _newFee) external onlyOwner {
        commitFee = _newFee;
    }

    function withdraw() external onlyOwner {
        (bool success,) = payable(owner).call{value: address(this).balance}("");
        require(success, "TransferFailed");
    }
}
