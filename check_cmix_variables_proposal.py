import src.xxapi as xxapi
from deepdiff import DeepDiff  # pip install deepdiff
import json


bins = [
    'North America',
    'South and Central America',
    'Western Europe',
    'Central Europe',
    'Eastern Europe',
    'Middle East',
    'Northern Africa',
    'Southern Africa',
    'Russia',
    'Eastern Asia',
    'Western Asia',
    'Oceania',
]

multiplier_decimals = 10**3


def main():
    # Connect to chain
    # Change the endpoint if necessary
    xxchain = xxapi.XXNetworkInterface('ws://127.0.0.1:63007')

    if xxchain is None:
        exit(1)

    # Get current cmix variables
    variables = xxchain.item_query('XXCmix', 'CmixVariables')

    #############################
    # MODIFY PREIMAGE HASH HERE #
    #############################

    preimage_hash = '0x4bb101c53c20857f233ab6429bb808ab411b1def18b2cbf2603b1ca1232bdc59'

    #############################
    #############################
    #############################

    # Get preimage data
    preimage = xxchain.map_query('Democracy', 'Preimages', preimage_hash)
    data = preimage['Available'][0]

    # Extract calldata and decode into cmix variables
    calldata = '0x' + data[6:]
    proposed_variables = xxchain.decode_scale('xx_cmix::cmix::variables', calldata)

    # Compare proposal to current (Generic comparison using DeepDiff)
    diff = DeepDiff(variables, proposed_variables)
    print(json.dumps(diff, indent=4))

    ##################################
    # MODIFY VERBOSE COMPARISON HERE #
    ##################################

    # Compare geo multipliers
    current_multipliers = [0] * len(variables['performance']['multipliers'])
    for value in variables['performance']['multipliers']:
        geobin = value[0]
        multiplier = value[1] / multiplier_decimals
        current_multipliers[geobin] = multiplier

    for value in proposed_variables['performance']['multipliers']:
        geobin = value[0]
        multiplier = value[1] / multiplier_decimals
        if multiplier != current_multipliers[geobin]:
            print(f"Multiplier for `{bins[geobin]}` changing from {current_multipliers[geobin]} to {multiplier}")

    #############################
    #############################
    #############################


if __name__ == "__main__":
    main()
