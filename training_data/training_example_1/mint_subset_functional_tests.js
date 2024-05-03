const fs = require("fs").promises;
contracts_to_deploy = ["Mint", "EUSD", "sAsset", "PriceFeed"];
var contracts = {};
for (name of contracts_to_deploy) {
  contracts[name] = artifacts.require(name);
}

contract("Mint test", async (accounts) => {
  console.log("starting functional tests");

  // START SETUP
  it("Running setup", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }

    let minterRole = await instances["sAsset"].MINTER_ROLE.call();
    let burnerRole = await instances["sAsset"].BURNER_ROLE.call();

    let minter_result = await instances["sAsset"].hasRole.call(
      minterRole,
      instances["Mint"].address
    );
    let burner_result = await instances["sAsset"].hasRole.call(
      burnerRole,
      instances["Mint"].address
    );
    assert.equal(minter_result, false);
    assert.equal(burner_result, false);
    await instances["sAsset"].grantRole(minterRole, instances["Mint"].address);
    await instances["sAsset"].grantRole(burnerRole, instances["Mint"].address);
  });
  // END SETUP

  // START FUNCTIONAL TESTS FOR registerAsset()
  it("FUNC TEST 1 registerAsset(): TEST THAT registerAsset() REGISTERS A VALID UNREGISTERED ASSET", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const sAssetAddress = await instances["sAsset"].address;
    // Use .call() for view functions
    await instances["Mint"].registerAsset(
      sAssetAddress,
      1,
      instances["PriceFeed"].address
    );
  });
  it("FUNC TEST 2 registerAsset(): TEST THAT registerAsset() ERRORS WHEN REGISTERING OF ASSET WITH collateralRatio <= 1 MCR ", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const testAddress = await instances["EUSD"].address;
    try {
      await instances["Mint"].registerAsset(
        testAddress,
        0.5,
        instances["PriceFeed"].address
      );
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });

  // END FUNCTIONAL TESTS FOR registerAsset()
  // START FUNCTIONAL TESTS FOR openPosition()
  it("FUNC TEST 1 openPosition(): TEST THAT openPosition() OPENS A POSITION FOR A REGISTERED ASSET", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const sAssetAddress = await instances["sAsset"].address;
    await instances["EUSD"].approve(instances["Mint"].address, 10);
    await instances["Mint"].openPosition(10, sAssetAddress, 2);
  });
  it("FUNC TEST 2 openPosition(): TEST THAT openPosition() ERRORS WHEN OPENING POSITION WITH UNREGISTERED ASSET", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const testAddress = await instances["EUSD"].address;
    try {
      await instances["EUSD"].approve(instances["Mint"].address, 10);
      await instances["Mint"].openPosition(10, testAddress, 2);
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });
  it("FUNC TEST 3 openPosition(): TEST THAT openPosition() ERRORS WHEN OPENING POSITION WITH collateralRatio < MCR", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const sAssetAddress = await instances["sAsset"].address;
    try {
      await instances["EUSD"].approve(instances["Mint"].address, 10);
      await instances["Mint"].openPosition(10, sAssetAddress, 0.5);
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });
  // END FUNCTIONAL TESTS FOR openPosition()
});
