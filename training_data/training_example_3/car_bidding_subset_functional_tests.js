const CarMarket = artifacts.require("CarMarket");

contract("CarMarket Functional Test", async (accounts) => {
  console.log("Starting CarMarket functional tests");

  let carMarketInstance;
  let owner = accounts[0];
  let bidder = accounts[1];
  let buyer = accounts[2];
  let carId;

  // START SETUP
  it("Setup: Deploy contract and initialize variables", async () => {
    carMarketInstance = await CarMarket.deployed();
  });
  // END SETUP

  // START FUNCTIONAL TESTS
  it("FUNC TEST 1 listCar(): Owner can list a car for sale", async () => {
    await carMarketInstance.listCar("Toyota Camry", web3.utils.toWei("5", "ether"), { from: owner });
    carId = 1;
    const car = await carMarketInstance.cars(carId);
    assert.equal(car.model, "Toyota Camry", "Car model does not match");
  });

  it("FUNC TEST 2 placeBid(): Bidder can place a bid on a listed car", async () => {
    await carMarketInstance.placeBid(carId, { from: bidder, value: web3.utils.toWei("6", "ether") });
    const car = await carMarketInstance.cars(carId);
    assert.equal(car.price, web3.utils.toWei("6", "ether"), "Bid amount is incorrect");
  });

  it("FUNC TEST 3 buyCar(): Buyer can buy a car instantly", async () => {
    const initialBalance = await web3.eth.getBalance(owner);
    await carMarketInstance.buyCar(carId, { from: buyer, value: web3.utils.toWei("6", "ether") });
    const car = await carMarketInstance.cars(carId);
    const finalBalance = await web3.eth.getBalance(owner);
    assert.equal(car.isSold, true, "Car is not marked as sold");
    assert(finalBalance > initialBalance, "Owner balance not increased after car sale");
  });
  // END FUNCTIONAL TESTS
});
