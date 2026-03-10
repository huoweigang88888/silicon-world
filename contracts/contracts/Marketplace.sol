// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SiliconWorldMarketplace is ReentrancyGuard, Ownable, IERC721Receiver {
    uint256 public platformFeeBps = 100; // 1%
    address public platformFeeReceiver;

    struct Listing {
        uint256 listingId;
        address seller;
        address nftContract;
        uint256 tokenId;
        uint256 price;
        bool active;
        uint256 createdAt;
        uint256 expiresAt;
    }

    struct Auction {
        uint256 auctionId;
        address seller;
        address nftContract;
        uint256 tokenId;
        uint256 startingPrice;
        uint256 reservePrice;
        uint256 endTime;
        address highestBidder;
        uint256 highestBid;
        bool active;
        bool finalized;
    }

    mapping(uint256 => Listing) public listings;
    mapping(uint256 => Auction) public auctions;
    mapping(address => uint256[]) public sellerListings;
    mapping(address => uint256[]) public sellerAuctions;

    uint256 private _listingIdCounter;
    uint256 private _auctionIdCounter;

    event Listed(
        uint256 indexed listingId,
        address indexed seller,
        address indexed nftContract,
        uint256 tokenId,
        uint256 price
    );

    event Delisted(uint256 indexed listingId);
    event Sold(
        uint256 indexed listingId,
        address indexed seller,
        address indexed buyer,
        uint256 tokenId,
        uint256 price
    );

    event AuctionCreated(
        uint256 indexed auctionId,
        address indexed seller,
        address indexed nftContract,
        uint256 tokenId,
        uint256 startingPrice,
        uint256 endTime
    );

    event BidPlaced(
        uint256 indexed auctionId,
        address indexed bidder,
        uint256 amount
    );

    event AuctionFinalized(
        uint256 indexed auctionId,
        address indexed winner,
        uint256 amount
    );

    event AuctionCancelled(uint256 indexed auctionId);

    constructor(address _platformFeeReceiver) 
    {
        platformFeeReceiver = _platformFeeReceiver;
        _transferOwnership(msg.sender);
    }

    function listNFT(
        address nftContract,
        uint256 tokenId,
        uint256 price,
        uint256 duration
    ) public nonReentrant returns (uint256) {
        require(price > 0, "Price must be > 0");
        require(duration > 0, "Duration must be > 0");
        
        IERC721 nft = IERC721(nftContract);
        require(nft.ownerOf(tokenId) == msg.sender, "Not token owner");
        require(
            nft.getApproved(tokenId) == address(this) || 
            nft.isApprovedForAll(msg.sender, address(this)),
            "Not approved"
        );

        _listingIdCounter++;
        uint256 listingId = _listingIdCounter;

        listings[listingId] = Listing({
            listingId: listingId,
            seller: msg.sender,
            nftContract: nftContract,
            tokenId: tokenId,
            price: price,
            active: true,
            createdAt: block.timestamp,
            expiresAt: block.timestamp + duration
        });

        sellerListings[msg.sender].push(listingId);

        emit Listed(listingId, msg.sender, nftContract, tokenId, price);

        return listingId;
    }

    function delistNFT(uint256 listingId) public nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.active, "Listing not active");
        require(listing.seller == msg.sender, "Not seller");

        listing.active = false;
        emit Delisted(listingId);
    }

    function buyNFT(uint256 listingId) public payable nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.active, "Listing not active");
        require(msg.value >= listing.price, "Insufficient payment");
        require(block.timestamp <= listing.expiresAt, "Listing expired");
        require(msg.sender != listing.seller, "Cannot buy own NFT");

        listing.active = false;

        uint256 platformFee = (listing.price * platformFeeBps) / 10000;
        uint256 sellerProceeds = listing.price - platformFee;

        (bool platformSuccess, ) = platformFeeReceiver.call{value: platformFee}("");
        require(platformSuccess, "Platform fee transfer failed");

        (bool sellerSuccess, ) = listing.seller.call{value: sellerProceeds}("");
        require(sellerSuccess, "Seller transfer failed");

        IERC721 nft = IERC721(listing.nftContract);
        nft.safeTransferFrom(listing.seller, msg.sender, listing.tokenId);

        emit Sold(listingId, listing.seller, msg.sender, listing.tokenId, listing.price);
    }

    function createAuction(
        address nftContract,
        uint256 tokenId,
        uint256 startingPrice,
        uint256 reservePrice,
        uint256 duration
    ) public nonReentrant returns (uint256) {
        require(startingPrice > 0, "Starting price must be > 0");
        require(duration > 0, "Duration must be > 0");
        
        IERC721 nft = IERC721(nftContract);
        require(nft.ownerOf(tokenId) == msg.sender, "Not token owner");
        require(
            nft.getApproved(tokenId) == address(this) || 
            nft.isApprovedForAll(msg.sender, address(this)),
            "Not approved"
        );

        _auctionIdCounter++;
        uint256 auctionId = _auctionIdCounter;

        auctions[auctionId] = Auction({
            auctionId: auctionId,
            seller: msg.sender,
            nftContract: nftContract,
            tokenId: tokenId,
            startingPrice: startingPrice,
            reservePrice: reservePrice,
            endTime: block.timestamp + duration,
            highestBidder: address(0),
            highestBid: 0,
            active: true,
            finalized: false
        });

        sellerAuctions[msg.sender].push(auctionId);

        emit AuctionCreated(auctionId, msg.sender, nftContract, tokenId, startingPrice, block.timestamp + duration);

        return auctionId;
    }

    function placeBid(uint256 auctionId) public payable nonReentrant {
        Auction storage auction = auctions[auctionId];
        require(auction.active, "Auction not active");
        require(block.timestamp < auction.endTime, "Auction ended");
        require(msg.value > auction.highestBid, "Bid too low");
        require(msg.sender != auction.seller, "Cannot bid on own auction");

        if (auction.highestBidder != address(0)) {
            (bool success, ) = auction.highestBidder.call{value: auction.highestBid}("");
            require(success, "Refund failed");
        }

        auction.highestBidder = msg.sender;
        auction.highestBid = msg.value;

        emit BidPlaced(auctionId, msg.sender, msg.value);
    }

    function finalizeAuction(uint256 auctionId) public nonReentrant {
        Auction storage auction = auctions[auctionId];
        require(!auction.finalized, "Already finalized");
        require(block.timestamp >= auction.endTime, "Auction not ended");

        auction.finalized = true;
        auction.active = false;

        if (auction.highestBidder != address(0)) {
            if (auction.reservePrice == 0 || auction.highestBid >= auction.reservePrice) {
                uint256 platformFee = (auction.highestBid * platformFeeBps) / 10000;
                uint256 sellerProceeds = auction.highestBid - platformFee;

                (bool platformSuccess, ) = platformFeeReceiver.call{value: platformFee}("");
                require(platformSuccess, "Platform fee transfer failed");

                (bool sellerSuccess, ) = auction.seller.call{value: sellerProceeds}("");
                require(sellerSuccess, "Seller transfer failed");

                IERC721 nft = IERC721(auction.nftContract);
                nft.safeTransferFrom(auction.seller, auction.highestBidder, auction.tokenId);

                emit AuctionFinalized(auctionId, auction.highestBidder, auction.highestBid);
            } else {
                (bool success, ) = auction.highestBidder.call{value: auction.highestBid}("");
                require(success, "Refund failed");
            }
        }
    }

    function cancelAuction(uint256 auctionId) public nonReentrant {
        Auction storage auction = auctions[auctionId];
        require(auction.seller == msg.sender, "Not seller");
        require(auction.active, "Auction not active");
        require(auction.highestBidder == address(0), "Has bids");

        auction.active = false;
        auction.finalized = true;

        emit AuctionCancelled(auctionId);
    }

    function getSellerListings(address seller) public view returns (uint256[] memory) {
        return sellerListings[seller];
    }

    function getSellerAuctions(address seller) public view returns (uint256[] memory) {
        return sellerAuctions[seller];
    }

    function setPlatformFeeBps(uint256 bps) public onlyOwner {
        require(bps <= 500, "Fee too high");
        platformFeeBps = bps;
    }

    function setPlatformFeeReceiver(address receiver) public onlyOwner {
        require(receiver != address(0), "Invalid address");
        platformFeeReceiver = receiver;
    }

    function withdraw() public onlyOwner {
        (bool success, ) = owner().call{value: address(this).balance}("");
        require(success, "Withdraw failed");
    }

    function onERC721Received(
        address,
        address,
        uint256,
        bytes memory
    ) public pure override returns (bytes4) {
        return this.onERC721Received.selector;
    }
}
