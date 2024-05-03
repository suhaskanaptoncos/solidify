// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract CoffeeShopLoyalty {
    // Structure to represent a customer
    struct Customer {
        uint loyaltyPoints;
        bool isEnrolled;
    }
    
    // Mapping to store customers
    mapping(address => Customer) public customers;
    
    // Event to notify when a customer enrolls in the loyalty program
    event Enrolled(address indexed customer);
    
    // Event to notify when a customer earns loyalty points
    event LoyaltyPointsEarned(address indexed customer, uint points);
    
    // Event to notify when a customer redeems loyalty points
    event LoyaltyPointsRedeemed(address indexed customer, uint points);
    
    // Modifier to ensure only enrolled customers can perform certain actions
    modifier onlyEnrolled() {
        require(customers[msg.sender].isEnrolled, "Only enrolled customers can perform this action");
        _;
    }
    
    // Function to enroll a customer in the loyalty program
    function enroll() public {
        require(!customers[msg.sender].isEnrolled, "Customer is already enrolled");
        
        customers[msg.sender].isEnrolled = true;
        emit Enrolled(msg.sender);
    }
    
    // Function to earn loyalty points
    function earnPoints(uint _points) public onlyEnrolled {
        customers[msg.sender].loyaltyPoints += _points;
        emit LoyaltyPointsEarned(msg.sender, _points);
    }
    
    // Function to redeem loyalty points
    function redeemPoints(uint _points) public onlyEnrolled {
        require(customers[msg.sender].loyaltyPoints >= _points, "Insufficient loyalty points");
        
        customers[msg.sender].loyaltyPoints -= _points;
        emit LoyaltyPointsRedeemed(msg.sender, _points);
    }
}
