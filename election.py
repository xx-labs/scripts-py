import src.xxapi as xxapi


def main():
    # Connect to chain
    xxchain = xxapi.XXNetworkInterface() 
    if xxchain is None:
        exit(1)

    # Run phragmen
    xxchain.seq_phragmen()


if __name__ == "__main__":
    main()
