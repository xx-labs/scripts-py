import math
import csv
import logging as log


DECIMALS = 1e9


def get_timestamp(block):
    for ext in block['extrinsics']:
        data = ext.value
        mod = data['call']['call_module']
        func = data['call']['call_function']
        if mod == "Timestamp" and func == "set":
            return data['call']['call_args'][0]['value']


def get_interest(points, block):
    # Find interest points
    idx = 0
    for idx, pt in enumerate(points):
        if pt["block"] > block:
            break
    start = points[idx-1]
    end = points[idx]
    diff = start["interest"] - end["interest"]
    block_diff = end["block"] - start["block"]
    interpolated = start["interest"] - int(block*block_diff/diff)
    return interpolated / DECIMALS


def remove_decimals(balance):
    return float(balance/DECIMALS)


def remove_decimals_round(balance):
    return int(math.floor(balance/DECIMALS))


def add_decimals(balance):
    return int(balance*DECIMALS)


def save_csv_file(path, headers, data):
    with open(path, 'w') as csvfile:
        wr = csv.writer(csvfile)
        wr.writerow(headers)
        if len(headers) != len(data[0]):
            log.error(f"Headers length {len(headers)} doesn't match data length {len(data[0])}")
            raise Exception
        for row in data:
            wr.writerow(row)


def derive_csv_rewards(raw_data):
    headers = ["account", "validator"]
    start_era = raw_data["start_era"]
    end_era = raw_data["end_era"]
    for era in range(start_era, end_era+1):
        headers.append(f"era {era}")
    csv_data = []
    era_totals = [0] * len(headers)
    era_totals[0] = "TOTAL"
    era_totals[1] = "TOTAL"
    for account in raw_data["accounts"]:
        account_data = [[""] * len(headers)]
        account_data[0][0] = account["address"]
        account_data[0][1] = "TOTAL"
        index = 1
        validators = {}
        for era in range(start_era, end_era+1):
            rewards = account["rewards"][era]
            era_sum = 0
            col_idx = 2+era-start_era
            for entry in rewards:
                validator = entry["validator"]
                if validator not in validators:
                    validators[validator] = index
                    index += 1
                    row = [""] * len(headers)
                    row[0] = account["address"]
                    row[1] = validator
                    account_data.append(row)
                row_idx = validators[validator]
                account_data[row_idx][col_idx] = entry["reward"]
                era_sum += entry["reward"]
            account_data[0][col_idx] = era_sum
            era_totals[col_idx] += era_sum
        for row in account_data:
            csv_data.append(row)
    csv_data.append(era_totals)
    return headers, csv_data


def derive_csv_apy(raw_data):
    headers = ["account", "validator"]
    start_era = raw_data["start_era"]
    end_era = raw_data["end_era"]
    for era in range(start_era, end_era+1):
        headers.append(f"era {era}")
    csv_data = []
    era_totals = [""] * len(headers)
    era_totals[0] = "TOTAL"
    era_totals[1] = "TOTAL"
    era_total_stake = [0] * len(headers)
    era_total_reward = [0] * len(headers)
    for account in raw_data["accounts"]:
        account_data = [[""] * len(headers)]
        account_data[0][0] = account["address"]
        account_data[0][1] = "TOTAL"
        index = 1
        validators = {}
        for era in range(start_era, end_era+1):
            rewards = account["rewards"][era]
            reward_sum = 0
            stake_sum = 0
            col_idx = 2+era-start_era
            for entry in rewards:
                validator = entry["validator"]
                if validator not in validators:
                    validators[validator] = index
                    index += 1
                    row = [""] * len(headers)
                    row[0] = account["address"]
                    row[1] = validator
                    account_data.append(row)
                row_idx = validators[validator]
                apy = 100 * (entry["reward"] * 365 / entry["stake"])
                account_data[row_idx][col_idx] = apy
                reward_sum += entry["reward"]
                stake_sum += entry["stake"]
            account_data[0][col_idx] = 0 if stake_sum == 0 else 100 * (reward_sum * 365 / stake_sum)
            era_total_stake[col_idx] += stake_sum
            era_total_reward[col_idx] += reward_sum
        for row in account_data:
            csv_data.append(row)
    for era in range(start_era, end_era+1):
        idx = 2+era-start_era
        era_totals[idx] = 0 if era_total_stake[idx] == 0 else 100 * (era_total_reward[idx] * 365 / era_total_stake[idx])
    csv_data.append(era_totals)
    return headers, csv_data
