// SPDX-License-Identifier: MIT
pragma solidity 0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract SimpleCollectible is ERC721 {
    uint256 public tokenCounter;

    constructor() public ERC721("Certificate", "DeepFakeCertification") {
        tokenCounter = 0;
    }

    function createCollectible(
        string memory tokenURI,
        address recipient
    ) public returns (uint256) {
        uint256 newTokenId = tokenCounter;
        _safeMint(address(recipient), newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        tokenCounter = tokenCounter + 1;
        return newTokenId;
    }
}