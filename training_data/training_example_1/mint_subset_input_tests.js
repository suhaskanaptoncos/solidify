const fs = require("fs").promises;
contracts_to_deploy = ["Mint", "EUSD", "sAsset", "PriceFeed"];
var contracts = {};
for (name of contracts_to_deploy) {
  contracts[name] = artifacts.require(name);
}

contract("Mint test", async (accounts) => {
  console.log("starting input tests");

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

  // START INPUT TESTS FOR registerAsset()
  it("INPUT TEST 1 registerAsset(): TEST THAT registerAsset() fails with invalid sAssetAddress (string)", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    try {
      await instances["Mint"].registerAsset(
        "0x123", 
        1,
        instances["PriceFeed"].address
      );
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });

  it("INPUT TEST 2 registerAsset(): TEST THAT registerAsset() fails with empty sAssetAddress", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    try {
      await instances["Mint"].registerAsset(
        "",
        1,
        instances["PriceFeed"].address
      );
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });

  it("INPUT TEST 3 registerAsset(): TEST THAT registerAsset() fails with zero collateralRatio", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const sAssetAddress = await instances["sAsset"].address;
    try {
      await instances["Mint"].registerAsset(
        sAssetAddress,
        0, 
        instances["PriceFeed"].address
      );
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });

  it("INPUT TEST 4 registerAsset(): TEST THAT registerAsset() fails with invalid priceFeedAddress (string)", async () => {
    var instances = {};
    for (name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const sAssetAddress = await instances["sAsset"].address;
    try {
      await instances["Mint"].registerAsset(
        sAssetAddress,
        1,
        "0x123"
      );
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });
  // END INPUT TESTS FOR registerAsset()
});