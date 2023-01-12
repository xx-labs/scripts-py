# scripts-py
Examples of interactions with xx network blockchain using python.

### check_cmix_variables_proposal.py
Verify an on-chain proposal to change cmix variables (which includes geo multipliers).

### economics.py
Get current economic parameters and estimating average validator payout.

### election.py
Run the phragmen election algorithm on the current Staking state of the chain.

### nominate.py
Nominate the top 16 validators by performance over last week.

### rewards.py
Get rewards information both in value and APY for a given set of accounts for a range of eras.

### set_cmix_variables.py
Create a proposal to change cmix variables (which includes geo multipliers).

### Using the API
An URL can be provided to `XXNetworkInterface` in order to connect to the blockchain. It defaults to `ws://localhost:63007`.
Node operators can run the script on their node computer, or on another machine using an [SSH Tunnel](https://xxnetwork.wiki/Wallet_-_Custom_Endpoint).
For development purposes, a local network can be launched following the instructions from [localnet](https://github.com/xx-labs/scripts#localnet).
