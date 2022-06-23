import src.xxapi as xxapi
import src.helpers as helpers


def main():
    # Connect to chain
    xxchain = xxapi.XXNetworkInterface()

    if xxchain is None:
        exit(1)

    # Replace with desired accounts
    accounts = [
        '6VPoNGcw4QnU6oCGbT4Fqe6PwGRu6JVTXSWQ6dmj5SpPx77Q',
        '6WwFERALLriPE91PpBvcFyCnHAT9TfBQHw5UfxKR9j5V5NKK',
        '6ZnU6zo1kUbuDBacxqx1sYA7UzVXXr3H94FXKoatTipaLvCq',
        '6ZCi18xFZABq4wne2zrX8GWomeitVXVYhp8S541qUyrJjY3M',
        '6VQ1WSzb3xawHi6uDXqYyMvQh3D7TgGM1quBoWNGdv9KDzWZ',
        '6XAVVPx5jWoJ3NjGWseXJbaod5ZtkTDQsQz9gVHCy1ejvgMC',
        '6XLZbikndRHTE23DiTcAJAWmjwx51gPnqfyJEzWFUZB7hr6J',
        '6WfWL98XBvc6tLPKaZPKbonnrAfrgLGVZJ8Zna8onMRe6yKW',
    ]

    # Can specify start (defaults to 0) and end era (defaults to last finished)
    raw_data = xxchain.staking_rewards(accounts)

    headers, csv_data = helpers.derive_csv_rewards(raw_data)
    helpers.save_csv_file('rewards.csv', headers, csv_data)

    headers, csv_data = helpers.derive_csv_apy(raw_data)
    helpers.save_csv_file('apy.csv', headers, csv_data)


if __name__ == "__main__":
    main()
