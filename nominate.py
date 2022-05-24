import src.xxapi as xxapi


def main():
    # Connect to chain
    xxchain = xxapi.XXNetworkInterface()

    if xxchain is None:
        exit(1)

    # Replace with desired accounts
    accounts = [
        "6YqWUNQVwA3k6NwM173w4crsN3e4SV719z9xkWRP71a6ZBBz",
        "6Ydyrg6uKLzdp9oPG7AQMiuCg1SxgXWRqpaMs3FqHQShJsUv",
        "6Y7tiHiypNecHar732Qy7uXbbNAgmntqvGaZdF8cRPi4Fhhp",
        "6XnYh3yvhoKW4fTvFsadg52yD9zWUYuaVjz5QWesw5Tfy4Bf",
        "6ap5Fvkqfdrwye1TKeVTchDF22zZywW1Hpgms9gntoFH1EFn",
        "6WcEGud85mqEuTfKKEJFBuyfKnBRqcPuHoDLpb6XAx9d6Y9H",
        "6a2qQCow8cAMp3h1eTGmdkVZt9yiHC6VjgqatxuaFMwjfPQn",
        "6ZidkVepTfbAzbQMCd4bJ6egqoNYWdUJEYobXTwbe5v1Huhj"
    ]

    ##########################
    # ADD ACCOUNTS KEYS HERE #
    ##########################
    # Example code:
    # with open('mnemonic') as file:
    #     mnemonic = file.readline().strip()
    # xxchain.add_account(mnemonic)
    ##########################
    ##########################
    ##########################

    # Number of targets per account
    # (Maximum is 16 which is the best value to allow Phragmen to optimize distribution of stake)
    num_targets = 16

    # Get list of validators ranked by points in ast 7 eras
    ranked = xxchain.rank_validators()

    # Nominate
    for idx, account in enumerate(accounts):
        targets = []
        for j in range(num_targets):
            targets.append(ranked[idx+j*len(accounts)])
        xxchain.nominate(account, targets, False)


if __name__ == "__main__":
    main()
