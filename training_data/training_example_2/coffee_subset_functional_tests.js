const CoffeeShopLoyalty = artifacts.require("CoffeeShopLoyalty");

contract("CoffeeShopLoyalty Functional Test", async (accounts) => {
  console.log("Starting CoffeeShopLoyalty functional tests");

  let loyaltyInstance;
  let customer = accounts[0];

  // START SETUP
  it("Setup: Deploy contract and initialize variables", async () => {
    loyaltyInstance = await CoffeeShopLoyalty.deployed();
  });
  // END SETUP

  // START FUNCTIONAL TESTS
  it("FUNC TEST 1 enroll(): Customer can enroll in the loyalty program", async () => {
    await loyaltyInstance.enroll({ from: customer });
    const enrolled = await loyaltyInstance.customers(customer);
    assert.equal(enrolled.isEnrolled, true, "Customer is not enrolled");
  });

  it("FUNC TEST 2 earnPoints(): Customer can earn loyalty points", async () => {
    await loyaltyInstance.earnPoints(100, { from: customer });
    const points = await loyaltyInstance.customers(customer);
    assert.equal(points.loyaltyPoints, 100, "Incorrect loyalty points");
  });

  it("FUNC TEST 3 redeemPoints(): Customer can redeem loyalty points", async () => {
    await loyaltyInstance.redeemPoints(50, { from: customer });
    const points = await loyaltyInstance.customers(customer);
    assert.equal(points.loyaltyPoints, 50, "Incorrect loyalty points after redemption");
  });
  // END FUNCTIONAL TESTS
});
