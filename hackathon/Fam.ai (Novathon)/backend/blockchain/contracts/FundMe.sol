// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

contract FundMe {
    using SafeMathChainlink for uint256;
    mapping(address => uint256) public addressToFund;
    address public owner;
    address[] public funders;

    constructor() public {
        owner = payable(msg.sender);
    }

    function fund() public payable {
        uint256 minimumUSD = 0.000001 * 10 ** 18;
        require(getPrice(msg.value) >= minimumUSD);
        addressToFund[msg.sender] += msg.value;
        funders.push(msg.sender);
    }

    function getPrice(uint256 ethAmt) public returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            0x694AA1769357215DE4FAC081bf1f309aDC325306
        );
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        uint256 price = uint256(answer * 10000000000);
        return (price * ethAmt) / 1000000000000000000;
    }

    function withdraw() public payable {
        payable(address(0x38CE0679A2e09e0e9738C702864A691A81f22e3C)).transfer(
            30000000000000
        );
    }
}