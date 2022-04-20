# scripts-py
Examples of interactions with xx network blockchain using python.

### economics.py
Contains an example of getting current economic parameters and estimating average validator payout.

### rewards.py
Contains an example of getting rewards both in value and APY for a given set of accounts for a range of eras.

### Using the API
An URL can be provided to `XXNetworkInterface`in order to connect to the blockchain. It defaults to `ws://localhost:9944`.
Node operators can run the script on their node computer, or on another machine using an [SSH Tunnel](https://xxnetwork.wiki/Explorer_-_Custom_Endpoint).
For development purposes, a local network can be launched following the instructions from [localnet](https://github.com/xx-labs/scripts#localnet).
