const CoffeeShopLoyalty = artifacts.require("CoffeeShopLoyalty");

contract("CoffeeShopLoyalty Input Validation Test", async (accounts) => {
  console.log("Starting CoffeeShopLoyalty input validation tests");

  let loyaltyInstance;
  let customer = accounts[0];

  // START SETUP
  it("Setup: Deploy contract and initialize variables", async () => {
    loyaltyInstance = await CoffeeShopLoyalty.deployed();
  });
  // END SETUP

  // START INPUT VALIDATION TESTS
  it("INPUT TEST 1 enroll(): Reverts if customer tries to enroll again", async () => {
    try {
      await loyaltyInstance.enroll({ from: customer });
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });

  it("INPUT TEST 2 redeemPoints(): Reverts if customer tries to redeem more points than they have", async () => {
    try {
      await loyaltyInstance.redeemPoints(100, { from: customer });
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });
  // END INPUT VALIDATION TESTS
});
