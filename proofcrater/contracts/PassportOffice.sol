// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.8.34;

contract PassportOffice {
    struct Passport {
        bytes photo;
        string birthDate;
        string documentNumber;
        string expirationDate;
        string firstName;
        string issuingState;
        string lastName;
        string nationality;
        string sex;
    }

    address public immutable owner;
    uint256 public uploadFee;

    mapping(address => mapping(uint256 => Passport)) public userPassport;
    mapping(address => uint256[]) public userPassports;

    event Uploaded(address user, string documentNumber);

    constructor(uint256 _initialFee) {
        owner = msg.sender;
        uploadFee = _initialFee;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Unauthorized");
        _;
    }

    function uploadPassport(Passport calldata passport) external payable {
        require(msg.value >= uploadFee, "InsufficientFee");
        userPassport[msg.sender][block.number] = passport;
        userPassports[msg.sender].push(block.number);
        emit Uploaded(msg.sender, passport.documentNumber);
    }

    function getUserPassportsPaginated(address user, uint256 fm, uint256 to) external view returns (uint256[] memory) {
        uint256[] storage allPassports = userPassports[user];
        uint256 total = allPassports.length;
        if (total == 0 || fm >= total) {
            return new uint256[](0);
        }
        if (to >= total) {
            to = total - 1;
        }
        if (fm > to) {
            return new uint256[](0);
        }
        uint256 pageSize = (to - fm) + 1;
        uint256[] memory page = new uint256[](pageSize);
        for (uint256 i = 0; i < pageSize; i++) {
            page[i] = allPassports[fm + i];
        }
        return page;
    }

    function userPassportsCounter(address user) external view returns (uint256) {
        return userPassports[user].length;
    }

    function setFee(uint256 _newFee) external onlyOwner {
        uploadFee = _newFee;
    }

    function withdraw() external onlyOwner {
        (bool success,) = payable(owner).call{value: address(this).balance}("");
        require(success, "TransferFailed");
    }
}
