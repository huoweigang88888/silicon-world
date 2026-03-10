import { expect } from "chai";
import hre from "hardhat";
const { ethers } = hre;

describe("SiliconWorldNFT", function () {
  let nftContract;
  let owner;
  let addr1;
  let addr2;

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();

    const NFT = await ethers.getContractFactory("SiliconWorldNFT");
    nftContract = await NFT.deploy(owner.address);
    await nftContract.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the correct owner", async function () {
      expect(await nftContract.owner()).to.equal(owner.address);
    });

    it("Should have correct royalty receiver", async function () {
      expect(await nftContract.royaltyReceiver()).to.equal(owner.address);
    });

    it("Should have 5% royalty", async function () {
      expect(await nftContract.royaltyBps()).to.equal(500);
    });
  });

  describe("Minting", function () {
    it("Should mint a new NFT", async function () {
      await nftContract.mint(addr1.address, "ipfs://test1", "land");
      
      expect(await nftContract.ownerOf(1)).to.equal(addr1.address);
      
      const info = await nftContract.getNFTInfo(1);
      expect(info.exists).to.be.true;
      expect(info.nftType).to.equal("land");
    });

    it("Should track total supply", async function () {
      await nftContract.mint(addr1.address, "ipfs://test1", "land");
      await nftContract.mint(addr2.address, "ipfs://test2", "building");
      
      expect(await nftContract.totalSupply()).to.equal(2);
    });

    it("Should only allow owner to mint", async function () {
      await expect(
        nftContract.connect(addr1).mint(addr1.address, "ipfs://test", "land")
      ).to.be.reverted;
    });
  });

  describe("Royalty", function () {
    it("Should calculate royalty correctly", async function () {
      const salePrice = ethers.parseEther("1");
      const royalty = await nftContract.calculateRoyalty(salePrice);
      
      // 5% of 1 ETH
      expect(royalty).to.equal(ethers.parseEther("0.05"));
    });

    it("Should allow owner to update royalty", async function () {
      await nftContract.setRoyaltyBps(250); // 2.5%
      expect(await nftContract.royaltyBps()).to.equal(250);
    });

    it("Should not allow royalty > 10%", async function () {
      await expect(nftContract.setRoyaltyBps(1001)).to.be.reverted;
    });
  });
});

describe("SiliconWorldMarketplace", function () {
  let marketplace;
  let nftContract;
  let owner;
  let seller;
  let buyer;

  beforeEach(async function () {
    [owner, seller, buyer] = await ethers.getSigners();

    const NFT = await ethers.getContractFactory("SiliconWorldNFT");
    nftContract = await NFT.deploy(owner.address);
    await nftContract.waitForDeployment();

    const Marketplace = await ethers.getContractFactory("SiliconWorldMarketplace");
    marketplace = await Marketplace.deploy(owner.address);
    await marketplace.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set correct platform fee", async function () {
      expect(await marketplace.platformFeeBps()).to.equal(100); // 1%
    });
  });

  describe("Listing", function () {
    it("Should list an NFT", async function () {
      // Mint NFT
      await nftContract.mint(seller.address, "ipfs://test", "land");
      
      // Approve marketplace
      await nftContract.connect(seller).approve(await marketplace.getAddress(), 1);
      
      // List NFT
      await marketplace.connect(seller).listNFT(
        await nftContract.getAddress(),
        1,
        ethers.parseEther("1"),
        86400 // 1 day
      );

      const listing = await marketplace.listings(1);
      expect(listing.active).to.be.true;
      expect(listing.price).to.equal(ethers.parseEther("1"));
    });
  });
});
