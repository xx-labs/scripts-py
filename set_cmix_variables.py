import src.xxapi as xxapi

multiplier_decimals = 10**3


def main():
    # Connect to chain
    # Change the endpoint if necessary
    xxchain = xxapi.XXNetworkInterface('ws://127.0.0.1:63007')

    if xxchain is None:
        exit(1)

    # Get current cmix variables
    variables = xxchain.item_query('XXCmix','CmixVariables')

    ##########################
    # MODIFY ANY VALUES HERE #
    ##########################
    # Example: set all multipliers to 1 (the multiplier value has 3 decimal places)
    variables['performance']['multipliers'] = [
        [0, int(1*multiplier_decimals)],
        [1, int(1*multiplier_decimals)],
        [2, int(1*multiplier_decimals)],
        [3, int(1*multiplier_decimals)],
        [4, int(1*multiplier_decimals)],
        [5, int(1*multiplier_decimals)],
        [6, int(1*multiplier_decimals)],
        [7, int(1*multiplier_decimals)],
        [8, int(1*multiplier_decimals)],
        [9, int(1*multiplier_decimals)],
        [10, int(1*multiplier_decimals)],
        [11, int(1*multiplier_decimals)],
    ]
    #########################
    #########################
    #########################

    # Build set cmix variables call
    call = xxchain.compose_call(
        call_module='XXCmix',
        call_function='set_next_cmix_variables',
        call_params={'variables': variables}
    )

    # Encode note preimage call
    preimage = xxchain.compose_call(
        call_module='Democracy',
        call_function='note_preimage',
        call_params={
            'encoded_proposal': str(call.data),
        }
    )

    print(preimage.data)


if __name__ == "__main__":
    main()
