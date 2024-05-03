// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IPriceFeed.sol";
import "./interfaces/IMint.sol";
import "./sAsset.sol";
import "./EUSD.sol";

contract Mint is Ownable, IMint {

    struct Asset {
        address token;
        uint minCollateralRatio;
        address priceFeed;
    }

    struct Position {
        uint idx;
        address owner;
        uint collateralAmount;
        address assetToken;
        uint assetAmount;
    }

    mapping(address => Asset) _assetMap;
    uint _currentPositionIndex;
    mapping(uint => Position) _idxPositionMap;
    address public collateralToken;
    

    constructor(address collateral) {
        collateralToken = collateral;
    }

    // Registers an asset as a token that can be borrowed. 
    function registerAsset(address assetToken, uint minCollateralRatio, address priceFeed) external override onlyOwner {
        require(assetToken != address(0), "Invalid assetToken address");
        require(minCollateralRatio >= 1, "minCollateralRatio must be greater than 100%");
        require(_assetMap[assetToken].token == address(0), "Asset was already registered");
        
        _assetMap[assetToken] = Asset(assetToken, minCollateralRatio, priceFeed);
    }

    // Returns a position that has already been opened.
    function getPosition(uint positionIndex) external view returns (address, uint, address, uint) {
        require(positionIndex < _currentPositionIndex, "Invalid index");
        Position storage position = _idxPositionMap[positionIndex];
        return (position.owner, position.collateralAmount, position.assetToken, position.assetAmount);
    }

    // Returns the amount of asset that can be minted given the asset price.
    function getMintAmount(uint collateralAmount, address assetToken, uint collateralRatio) public view returns (uint) {
        Asset storage asset = _assetMap[assetToken];
        (int relativeAssetPrice, ) = IPriceFeed(asset.priceFeed).getLatestPrice();
        uint8 decimal = sAsset(assetToken).decimals();
        uint mintAmount = collateralAmount * (10 ** uint256(decimal)) / uint(relativeAssetPrice) / collateralRatio ;
        return mintAmount;
    }

    // Checks if the asset is registered.
    function checkRegistered(address assetToken) public view returns (bool) {
        return _assetMap[assetToken].token == assetToken;
    }

    // Opens a position in which collateral is used to borrow a given asset.
    function openPosition(uint collateralAmount, address assetToken, uint collateralRatio) external override  {
        require(checkRegistered(assetToken));
        Asset storage asset = _assetMap[assetToken];
        uint mcr = asset.minCollateralRatio;
        require(collateralRatio >= mcr);
        
        uint assetAmount = getMintAmount(collateralAmount, assetToken, collateralRatio);

        EUSD(collateralToken).transferFrom(msg.sender, address(this), collateralAmount);
        sAsset(assetToken).mint(msg.sender, assetAmount);

        
        _idxPositionMap[_currentPositionIndex] = Position(_currentPositionIndex, msg.sender, collateralAmount, assetToken, assetAmount);
        _currentPositionIndex++;

    }

    // Closes an opened position.
    function closePosition(uint positionIndex) external override {
        Position storage position = _idxPositionMap[positionIndex];
        require(position.owner == msg.sender);
        ERC20(collateralToken).transfer(msg.sender, position.collateralAmount);
        sAsset(position.assetToken).burn(msg.sender, position.assetAmount);
        delete _idxPositionMap[positionIndex];

    }

    // Deposits collateral into a position.
    function deposit(uint positionIndex, uint collateralAmount) external override  {
        Position storage position = _idxPositionMap[positionIndex];
        require(position.owner == msg.sender);
        ERC20(collateralToken).transferFrom(msg.sender, address(this), collateralAmount);
        position.collateralAmount += collateralAmount;
    }

    // Withdraws collateral into a position. This should not allow the collateral ratio to drop below the minimum.
    function withdraw(uint positionIndex, uint withdrawAmount) external override  {
        Position storage position = _idxPositionMap[positionIndex];
        require(position.owner == msg.sender);
        uint mcr = _assetMap[position.assetToken].minCollateralRatio;
        uint proposedNewAmount = position.collateralAmount - withdrawAmount;
        (int assetPrice, ) = IPriceFeed(_assetMap[position.assetToken].priceFeed).getLatestPrice();
        uint8 decimal = sAsset(position.assetToken).decimals();
        uint proposedCollateralRatio = proposedNewAmount / (position.assetAmount * (uint(assetPrice) / (10 ** uint256(decimal))));
        require(proposedCollateralRatio >= mcr);
        ERC20(collateralToken).transfer(msg.sender, withdrawAmount);
        position.collateralAmount -= withdrawAmount;

    }

    // Mints the asset token that is being borrowed.
    function mint(uint positionIndex, uint mintAmount) external override  {
        Position storage position = _idxPositionMap[positionIndex];
        require(position.owner == msg.sender);
        uint mcr = _assetMap[position.assetToken].minCollateralRatio;
        uint proposedNewAmount = position.assetAmount + mintAmount;
        (int assetPrice, ) = IPriceFeed(_assetMap[position.assetToken].priceFeed).getLatestPrice();
        uint8 decimal = sAsset(position.assetToken).decimals();
        uint proposedCollateralRatio = position.collateralAmount / (proposedNewAmount * (uint(assetPrice) / (10 ** uint256(decimal))));
        require(proposedCollateralRatio >= mcr);
        sAsset(position.assetToken).mint(position.owner, mintAmount);
        position.assetAmount += mintAmount;
    }
    
    // Burns the asset token that was borrowed.
    function burn(uint positionIndex, uint burnAmount) external override {
        Position storage position = _idxPositionMap[positionIndex];
        require(position.owner == msg.sender);
        sAsset(position.assetToken).burn(position.owner, burnAmount);
        position.assetAmount -= burnAmount;
    }
    
}
    


