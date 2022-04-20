import src.xxapi as xxapi


def main():
    # Connect to chain
    xxchain = xxapi.XXNetworkInterface()

    if xxchain is None:
        exit(1)

    # Estimate average validator payout for current era
    # Will print to logs all relevant economic parameters for current era
    xxchain.estimate_payout()


if __name__ == "__main__":
    main()
