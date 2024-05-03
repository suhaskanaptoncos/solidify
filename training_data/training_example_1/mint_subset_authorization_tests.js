const fs = require("fs").promises;
const contracts_to_deploy = ["Mint", "EUSD", "sAsset", "PriceFeed"];
let contracts = {};

for (const name of contracts_to_deploy) {
  contracts[name] = artifacts.require(name);
}

contract("Mint test", async (accounts) => {
  console.log("Starting authorization tests");

  // START SETUP
  it("Running setup", async () => {
    const instances = {};
    let owner;
    for (const name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }

    owner = await instances["Mint"].owner();

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
  it("FUNC TEST 1 registerAsset(): Registers a valid unregistered asset when called by the owner", async () => {
    const instances = {};
    for (const name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const sAssetAddress = await instances["sAsset"].address;
    await instances["Mint"].registerAsset(
      sAssetAddress,
      1,
      instances["PriceFeed"].address,
      { from: owner }
    );
  });

  it("FUNC TEST 2 registerAsset(): Errors when called by a non-owner account", async () => {
    const instances = {};
    for (const name of contracts_to_deploy) {
      instances[name] = await contracts[name].deployed();
    }
    const sAssetAddress = await instances["sAsset"].address;
    const nonOwner = accounts[1];
    try {
      await instances["Mint"].registerAsset(
        sAssetAddress,
        1,
        instances["PriceFeed"].address,
        { from: nonOwner }
      );
      assert.fail("Expected an error");
    } catch (error) {
      assert.ok(error);
    }
  });
  // END FUNCTIONAL TESTS FOR registerAsset()
});
