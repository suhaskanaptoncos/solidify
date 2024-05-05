const CarMarket = artifacts.require("CarMarket");

contract("CarMarket Input Validation Test", async (accounts) => {
  console.log("Starting CarMarket input validation tests");

  let carMarketInstance;
  let owner = accounts[0];
  let bidder = accounts[1];
  let carId;

  // START SETUP
  it("Setup: Deploy contract and initialize variables", async () => {
    carMarketInstance = await CarMarket.deployed();
  });
  // END SETUP

  // START INPUT VALIDATION TESTS
  it("INPUT TEST 1 listCar(): Reverts if empty model is provided", async () => {
    try {
      await carMarketInstance.listCar("", web3.utils.toWei("5", "ether"), { from: owner });
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });

  it("INPUT TEST 2 placeBid(): Reverts if bid amount is less than current price", async () => {
    await carMarketInstance.listCar("Ford Mustang", web3.utils.toWei("10", "ether"), { from: owner });
    carId = 3;
    try {
      await carMarketInstance.placeBid(carId, { from: bidder, value: web3.utils.toWei("8", "ether") });
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });

  it("INPUT TEST 3 buyCar(): Reverts if buyer sends insufficient funds", async () => {
    await carMarketInstance.listCar("BMW X5", web3.utils.toWei("20", "ether"), { from: owner });
    carId = 4;
    try {
      await carMarketInstance.buyCar(carId, { from: bidder, value: web3.utils.toWei("18", "ether") });
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });
  // END INPUT VALIDATION TESTS
});
