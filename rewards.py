import src.xxapi as xxapi
import src.helpers as helpers


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

    # Can specify start (defaults to 0) and end era (defaults to last finished)
    raw_data = xxchain.staking_rewards(accounts, 143)

    headers, csv_data = helpers.derive_csv_rewards(raw_data)
    helpers.save_csv_file('rewards.csv', headers, csv_data)

    headers, csv_data = helpers.derive_csv_apy(raw_data)
    helpers.save_csv_file('apy.csv', headers, csv_data)


if __name__ == "__main__":
    main()
