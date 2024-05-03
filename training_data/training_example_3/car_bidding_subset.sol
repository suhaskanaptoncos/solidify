pragma solidity ^0.8.0;

contract CarMarket {
    // Structure to represent a car
    struct Car {
        uint id;
        string model;
        uint price;
        address owner;
        bool isSold;
    }
    
    // Mapping to store cars
    mapping(uint => Car) public cars;
    
    // Event to notify when a new car is listed
    event CarListed(uint indexed carId, string model, uint price, address indexed owner);
    
    // Event to notify when a car is sold
    event CarSold(uint indexed carId, string model, uint price, address indexed buyer, address indexed seller);
    
    // Counter for generating unique car IDs
    uint public carIdCounter;
    
    // Modifier to ensure only the owner can perform certain actions
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }
    
    address public owner;
    
    // Constructor function to initialize the contract
    constructor() {
        owner = msg.sender;
    }
    
    // Function to list a new car for sale
    function listCar(string memory _model, uint _price) public {
        carIdCounter++;
        cars[carIdCounter] = Car(carIdCounter, _model, _price, msg.sender, false);
        emit CarListed(carIdCounter, _model, _price, msg.sender);
    }
    
    // Function to allow users to place a bid on a car
    function placeBid(uint _carId) public payable {
        require(!cars[_carId].isSold, "Car is already sold");
        require(msg.value > cars[_carId].price, "Bid amount must be higher than current price");
        
        cars[_carId].price = msg.value;
        cars[_carId].owner = msg.sender;
    }
    
    // Function to allow a user to buy a car instantly
    function buyCar(uint _carId) public payable {
        require(!cars[_carId].isSold, "Car is already sold");
        require(msg.value >= cars[_carId].price, "Insufficient funds to buy the car");
        
        address payable seller = payable(cars[_carId].owner);
        seller.transfer(msg.value);
        
        emit CarSold(_carId, cars[_carId].model, cars[_carId].price, msg.sender, seller);
        
        cars[_carId].isSold = true;
    }
}
