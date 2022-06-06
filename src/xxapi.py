import logging as log
from substrateinterface import SubstrateInterface, Keypair  # pip3 install substrate-interface
from substrateinterface.exceptions import SubstrateRequestException
import src.helpers as helpers
from datetime import datetime
import sys


########################################################################################################################
# XXNetworkInterface class
########################################################################################################################

class XXNetworkInterface(SubstrateInterface):
    # Constructor
    def __init__(self, url: str = "ws://localhost:63007", logfile: str = "", verbose: bool = False):
        try:
            super(XXNetworkInterface, self).__init__(url=url)
        except ConnectionRefusedError:
            log.error("Can't connect to specified xx network node endpoint")
            raise
        except Exception as e:
            log.error("Failed to get xx network connection: %s" % e)
            raise
        # Keychain
        self.keychain = {}
        # Known accounts
        self.treasury_account = "6XmmXY7zLRirfFQivNnn6LNyRP1aMvtzyr4gATsfbdFh2QqF"
        self.canary_account = "6XmmXY7zLRirfHC8R99We24pEv2vpnGi29qZBRkdHNKxMCEB"
        self.sale_account = "6XmmXY7zLRihLPUmtcKEtvKTxtphzwGRb7YUjztiEYBUG545"
        self.bridge_account = "6XmmXY7v7NeGH3qiiZTQCRsp2bV3m5zNKAgohiNPE8uiprJ7"
        self.rewards_pool_account = "6XmmXY7zLRirPixiSFxKNA54MYYFYajZMXeA6bo7cb95gPUR"
        # Unstakeable accounts
        self.unstakeable_accounts = [self.rewards_pool_account, self.sale_account, self.canary_account]
        # Useful time constants
        self.era_milis = 24 * 3600 * 1000
        self.block_time = 6000
        self.blocks_per_era = 14400
        self.year_milis = 365.25 * 24 * 3600 * 1000
        # Chain info cache
        self.cache = {}
        # Setup logging
        handlers = [log.StreamHandler(sys.stdout)]
        if logfile != "":
            handlers.append(log.FileHandler(logfile, mode='w'))
        log.basicConfig(
            handlers=handlers,
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=log.INFO if not verbose else log.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    ##############################
    # Generic query functions
    ##############################

    # Query a storage double map
    def double_map_query(self, module, storage, arg, second: str = "",
                         block_hash: str = None, force_cache_refresh: bool = False):
        if arg == "":
            log.error("Can't query a double map without any argument")
            return
        # Check if map is cached
        is_cached = False
        if module in self.cache:
            if storage in self.cache[module]:
                if arg in self.cache[module][storage]:
                    is_cached = True
        # Element query
        if second != "":
            try:
                if not is_cached or force_cache_refresh or block_hash is not None:
                    query = self.query(module, storage, [arg, second], block_hash=block_hash)
                    result = query.value
                else:
                    result = self.cache[module][storage][arg][second]
            except Exception as e:
                log.error("Connection lost while in \'xxnetwork.query(\"%s\", \"%s\", \"%s\")\'. Error: %s"
                          % (module, storage, [arg, second], e))
                return
            return result
        # Map query
        try:
            if not is_cached or force_cache_refresh or block_hash is not None:
                query = self.query_map(module, storage, [arg], block_hash=block_hash)
                result = {}
                for key, value in query:
                    result[key.value] = value.value
                # Update cache if no block hash was specified
                if block_hash is None:
                    if module not in self.cache:
                        self.cache[module] = {}
                    if storage not in self.cache[module]:
                        self.cache[module][storage] = {}
                    self.cache[module][storage][arg] = result
                log.debug(f"Result has {len(result)} entries")
            else:
                result = self.cache[module][storage][arg]
        except Exception as e:
            log.error("Connection lost while in \'xxnetwork.query_map(\"%s\", \"%s\", \"%s\")\'. Error: %s"
                      % (module, storage, arg, e))
            return
        return result

    # Query a storage map
    def map_query(self, module, storage, arg, block_hash: str = None, force_cache_refresh: bool = False):
        # Check if map is cached
        is_cached = False
        if module in self.cache:
            if storage in self.cache[module]:
                is_cached = True
        # Map query
        if arg == "":
            try:
                if not is_cached or force_cache_refresh or block_hash is not None:
                    query = self.query_map(module, storage, block_hash=block_hash)
                    result = {}
                    for key, value in query:
                        result[key.value] = value.value
                    # Update cache if no block hash was specified
                    if block_hash is None:
                        if module not in self.cache:
                            self.cache[module] = {}
                        self.cache[module][storage] = result
                    log.debug(f"Result has {len(result)} entries")
                else:
                    result = self.cache[module][storage]
            except Exception as e:
                log.error("Connection lost while in \'xxnetwork.query_map(\"%s\", \"%s\")\'. Error: %s"
                          % (module, storage, e))
                return
            return result
        # Element query
        try:
            if not is_cached or force_cache_refresh or block_hash is not None:
                query = self.query(module, storage, [arg], block_hash=block_hash)
                result = query.value
            else:
                result = self.cache[module][storage][arg]
        except Exception as e:
            log.error("Connection lost while in \'xxnetwork.query(\"%s\", \"%s\", \"%s\")\'. Error: %s"
                      % (module, storage, arg, e))
            return
        return result

    # Query a storage item
    def item_query(self, module, storage, block_hash: str = None, force_cache_refresh: bool = False):
        # Check if item is cached
        is_cached = False
        if module in self.cache:
            if storage in self.cache[module]:
                is_cached = True
        try:
            if not is_cached or force_cache_refresh or block_hash is not None:
                query = self.query(module, storage, block_hash=block_hash)
                result = query.value
                # Update cache if no block hash was specified
                if block_hash is None:
                    if module not in self.cache:
                        self.cache[module] = {}
                    self.cache[module][storage] = result
            else:
                result = self.cache[module][storage]
        except Exception as e:
            log.error("Connection lost while in \'xxnetwork.query(\"%s\", \"%s\")\'. Error: %s"
                      % (module, storage, e))
            return
        return result

    # Query a storage constant
    def constant_query(self, module, storage, block_hash: str = None, force_cache_refresh: bool = False):
        # Check if item is cached
        is_cached = False
        if module in self.cache:
            if storage in self.cache[module]:
                is_cached = True
        try:
            if not is_cached or force_cache_refresh or block_hash is not None:
                query = self.get_constant(module, storage, block_hash=block_hash)
                result = query.value
                # Update cache if no block hash was specified
                if block_hash is None:
                    if module not in self.cache:
                        self.cache[module] = {}
                    self.cache[module][storage] = result
            else:
                result = self.cache[module][storage]
        except Exception as e:
            log.error("Connection lost while in \'xxnetwork.get_constant(\"%s\", \"%s\")\'. Error: %s"
                      % (module, storage, e))
            raise e
        return result

    # Query a block
    def block_query(self, block_number: int = None):
        try:
            block = self.get_block(block_number=block_number)
        except Exception as e:
            log.error("Connection lost while in \'xxnetwork.get_block(%s)\'. Error: %s" % (block_number, e))
            return
        return block

    # Query a block header
    def block_header_query(self, block_number: int = None):
        try:
            block = self.get_block_header(block_number=block_number)
        except Exception as e:
            log.error("Connection lost while in \'xxnetwork.get_block_header(%s)\'. Error: %s" % (block_number, e))
            return
        return block

    # Run a query function from a given start block until present, with given block step
    def query_history(self, start_block, block_step, query_fn, *args):
        latest = self.block_header_query()
        latest_block_no = latest['header']['number']
        block_no = 1 if start_block is None else start_block
        step = self.blocks_per_era if block_step is None else block_step
        result = []
        while True:
            if block_no >= latest_block_no:
                break
            log.info(f"Querying block {block_no}")
            block = self.block_query(block_no)
            if block is None:
                block_no += 1
                continue
            value = query_fn(*args, block_hash=block['header']['hash'])
            timestamp = helpers.get_timestamp(block)
            date = datetime.utcfromtimestamp(int(timestamp/1000))
            result.append([date, value])
            block_no += step
        return result

    # Run a query function at a given era
    # If the era is not on-chain anymore, it will use an approximate newest block that contains
    # the given era
    # Example:
    # Assume current era is 150 and history depth is 84, so the oldest stored era is 66
    # If a query is done for era 50, it will approximate a block in middle of era 50+84-1=133
    def query_era(self, era, query_fn, *args):
        # History depth and current era
        depth = self.item_query("Staking", "HistoryDepth")
        curr_era = self.item_query("Staking", "ActiveEra")
        curr_era = curr_era['index']

        block_hash = None
        if era < (curr_era - depth):
            # Estimate block that contains info about given era
            block_estimate = int((era+depth-0.5)*self.blocks_per_era)
            block = self.block_header_query(block_estimate)
            block_hash = block['header']['hash']
        return query_fn(*args, block_hash=block_hash)

    ##############################
    # Generic call functions
    ##############################

    # Build a batch of calls
    def build_batch_calls(self, calls):
        convert_calls = []
        for call in calls:
            convert_calls.append(call.value)
        return self.compose_call(
            call_module='Utility',
            call_function='batch',
            call_params={'calls': convert_calls}
        )

    # Build a call
    def build_call(self, module, function, params):
        return self.compose_call(
            call_module=module,
            call_function=function,
            call_params=params
        )

    ##############################
    # Transaction send functions
    ##############################

    # Submit a transaction
    def send_transaction(self, account, call, wait_inclusion: bool = True, wait_finality: bool = False):
        keypair = self.keychain.get(account)
        if keypair is None:
            log.error(f"Can't send transaction from {account}, don't have keypair in keychain")
            return
        extrinsic = self.create_signed_extrinsic(call=call, keypair=keypair)
        try:
            receipt = self.submit_extrinsic(extrinsic,
                                            wait_for_inclusion=wait_inclusion,
                                            wait_for_finalization=wait_finality)
            log.info(f"Transaction sent, with hash {receipt.extrinsic_hash}")
        except SubstrateRequestException as e:
            log.error(f"Failed to send transaction: {e}")

    # Submit multiple calls in batches of given size
    def send_batches(self, account, calls, batch_size: int = 10,
                     wait_inclusion: bool = True, wait_finality: bool = False):
        call_batches = helpers.chunks(calls, batch_size)
        for call in call_batches:
            batch = self.build_batch_calls(call)
            log.info(f"Sending batch with {len(call)} calls")
            self.send_transaction(account, batch, wait_inclusion, wait_finality)

    # Add an account to the keychain
    def add_account(self, mnemonic, path: str = ''):
        try:
            keypair = Keypair.create_from_uri(mnemonic+path, ss58_format=self.ss58_format)
            addr = keypair.ss58_address
            self.keychain[addr] = keypair
            log.info(f"Added account {addr} to keychain")
        except Exception as e:
            log.error(f"Error adding account to keychain: {e}")

    ##############################
    # Economics queries
    ##############################

    # Get account balance, with optional block number or block hash
    def balance(self, account, block_number: int = None, block_hash: str = None):
        if account == "":
            log.error("Account address not specified")
            raise Exception
        if block_number is not None:
            block = self.block_header_query(block_number)
            block_hash = block['header']['hash']
        balance = self.map_query("System", "Account", account, block_hash)
        return helpers.remove_decimals(balance['data']['free'] + balance['data']['reserved'])

    # Get account balance history, optionally starting at specified block and with a given block step
    def balance_history(self, account, start_block: int = None, block_step: int = None):
        if account == "":
            log.error("Account address not specified")
            raise Exception
        return self.query_history(start_block, block_step, self.balance, account)

    # Get issuance, with optional block number or block hash
    def issuance(self, block_number: int = None, block_hash: str = None):
        if block_number is not None:
            block = self.block_header_query(block_number)
            block_hash = block['header']['hash']
        issuance = self.item_query("Balances", "TotalIssuance", block_hash)
        log.info(f"Issuance: {issuance}")
        return helpers.remove_decimals(issuance)

    # Get unstakeable balance, with optional block number or block hash
    def unstakeable(self, block_number: int = None, block_hash: str = None):
        if block_number is not None:
            block = self.block_header_query(block_number)
            block_hash = block['header']['hash']
        # Get balance of unstakeable accounts
        unstakeable = 0
        for acct in self.unstakeable_accounts:
            data = self.map_query("System", "Account", acct, block_hash)
            balance = data['data']['free'] + data['data']['reserved']
            unstakeable += balance

        # Get total balance under custody and add to unstakeable
        custody = self.item_query("XXCustody", "TotalCustody", block_hash)
        # Get liquidity rewards balance and add to unstakeable
        liquidity = self.item_query("XXEconomics", "LiquidityRewards", block_hash)
        unstakeable += custody + liquidity
        log.info(f"Unstakeable: {unstakeable}")
        return helpers.remove_decimals(unstakeable)

    # Get current stakeable issuance, with optional block number or block hash
    def stakeable(self, block_number: int = None, block_hash: str = None):
        if block_number is not None:
            block = self.block_header_query(block_number)
            block_hash = block['header']['hash']
        return self.issuance(block_number, block_hash) - self.unstakeable(block_number, block_hash)

    # Get issuance history, optionally starting at specified block and with a given block step
    def issuance_history(self, start_block: int = None, block_step: int = None):
        return self.query_history(start_block, block_step, self.issuance, None)

    # Get stakeable history, optionally starting at specified block and with a given block step
    def stakeable_history(self, start_block: int = None, block_step: int = None):
        return self.query_history(start_block, block_step, self.stakeable, None)

    # Compute estimate of validator rewards for current era
    # If a validator address is provided, it computes its portion based on current era points
    # Otherwise the average payout is given
    def estimate_payout(self, validator_address: str = ""):
        # Get inflation params
        inflation = self.item_query("XXEconomics", "InflationParams")
        min_inflation = inflation['min_inflation'] / helpers.DECIMALS
        ideal_stake = inflation['ideal_stake'] / helpers.DECIMALS

        # Get interest points
        interest_points = self.item_query("XXEconomics", "InterestPoints")

        # Get current era stake
        era = self.item_query("Staking", "ActiveEra")
        start = era['start']
        era = era['index']
        stake = self.map_query("Staking", "ErasTotalStake", era)
        stake = helpers.remove_decimals(stake)

        # Get validator set size
        val_set = self.double_map_query("Staking", "ErasStakers", era)
        val_size = len(val_set)

        # Estimate block number for middle of curr era
        block = self.get_block()
        block_no = block['header']['number']
        log.info(f"Block: {block_no}")

        # Find block timestamp
        network_time = helpers.get_timestamp(block)
        log.info(f"Network time: {datetime.utcfromtimestamp(int(network_time/1000))}")
        log.info(f"Era start: {datetime.utcfromtimestamp(int(start/1000))}")
        predicted_middle_curr = block_no - int((network_time-start)/self.block_time) + int(self.blocks_per_era/2)
        log.info(f"Middle curr era block: {predicted_middle_curr}")

        # Compute fixed economics
        interest = helpers.get_interest(interest_points, predicted_middle_curr)
        ideal_inflation = ideal_stake * interest
        log.info(f"Min inflation: {min_inflation}")
        log.info(f"Ideal staking ratio: {ideal_stake}")
        log.info(f"Interest ratio: {interest}")
        log.info(f"Ideal inflation: {ideal_inflation}")

        # Compute economics
        stakeable = self.stakeable()
        stake_ratio = stake / stakeable

        log.info(f"Era: {era}")
        log.info(f"Stakeable: {stakeable}")
        log.info(f"Staked: {stake}")
        log.info(f"Stake ratio: {stake_ratio}")
        inflation = min_inflation + (ideal_inflation - min_inflation)*stake_ratio/ideal_stake
        log.info(f"Inflation: {inflation}")

        # Compute era payout
        total_payout = ideal_inflation*stakeable*self.era_milis/self.year_milis
        payout = inflation*stakeable*self.era_milis/self.year_milis
        treasury = total_payout - payout
        log.info(f"Treasury payout: {treasury}")
        log.info(f"Validator set payout: {payout}")

        # Estimated per validator
        val_payout = None
        if validator_address != "":
            # Get validator points
            reward_points = self.map_query("Staking", "ErasRewardPoints", era)
            total = reward_points['total']
            for tup in reward_points['individual']:
                if tup[0] == validator_address:
                    val_points = tup[1]
                    log.info(f"Validator {validator_address} has {val_points} points out of {total}")
                    log.info(f"Current validator payout")
                    val_payout = payout * (val_points/total)
                    log.info(val_payout)
                    return val_payout
            if val_payout is None:
                log.info(f"Specified address {validator_address} doesn't correspond to a validator")

        val_payout = payout / val_size
        log.info(f"Validator set size: {val_size}")
        log.info("Estimated validator payment, assuming equal performance")
        log.info(val_payout)
        return val_payout

    # Get staking rewards per validator earned by given account(s) in given era range
    # Defaults to start_era = 0, end_era = None, which gets all rewards up to last era
    def staking_rewards(self, accounts, start_era: int = 0, end_era: int = None):
        if len(accounts) == 0:
            log.error("At least one account address should be specified")
            raise Exception
        curr_era = self.item_query("Staking", "ActiveEra")
        curr_era = curr_era['index']
        if end_era is None:
            end_era = curr_era - 1
        if start_era > end_era:
            log.error("Start era can't be larger than end era")
            raise Exception
        if end_era > curr_era - 1:
            log.error("End era can't be larger than last era")
            raise Exception

        # Gather necessary information for era range
        # History depth
        depth = self.item_query("Staking", "HistoryDepth")
        rewards = {}
        points = {}
        target_era = start_era
        while True:
            eras_rewards = self.query_era(target_era, self.map_query, "Staking", "ErasValidatorReward", "")
            rewards = {**rewards, **eras_rewards}
            eras_points = self.query_era(target_era, self.map_query, "Staking", "ErasRewardPoints", "")
            points = {**points, **eras_points}
            target_era += depth - 1
            if target_era >= end_era:
                break

        result = {
            "start_era": start_era,
            "end_era": end_era,
            "accounts": []
        }
        for acct in accounts:
            era_rewards = {}
            for era in range(start_era, end_era+1):
                era_rewards[era] = []
            result["accounts"].append({
                "address": acct,
                "rewards": era_rewards
            })

        for era in range(start_era, end_era+1):
            log.info(f"Processing era {era}")
            era_total_reward = rewards[era]
            era_points = points[era]
            points_total = era_points["total"]

            # Get stakers for specified era
            stakers = self.query_era(era, self.double_map_query, "Staking", "ErasStakers", era)
            # Get validator preferences for specified era
            prefs = self.query_era(era, self.double_map_query, "Staking", "ErasValidatorPrefs", era)

            for validator, info in stakers.items():
                # Validator info
                validator_stake = info["own"]
                total_stake = info["total"]
                validator_commission = helpers.remove_decimals(prefs[validator]["commission"])

                # Find points
                validator_points = 1
                for value in era_points["individual"]:
                    if value[0] == validator:
                        validator_points = value[1]
                        break

                # Validator reward according to performance points
                validator_reward = validator_points * era_total_reward / points_total

                # Validator commission reward
                commission_reward = validator_commission * validator_reward
                # Deduct commission reward from validator reward
                validator_leftover_reward = validator_reward - commission_reward

                # Validator stake reward
                validator_stake_reward = validator_stake * validator_leftover_reward / total_stake

                # Validator total reward
                validator_reward = validator_stake_reward + commission_reward

                # Compute reward for each desired account
                for idx, acct in enumerate(accounts):
                    if acct == validator:
                        result["accounts"][idx]["rewards"][era].append({
                            "validator": validator,
                            "stake": helpers.remove_decimals(validator_stake),
                            "reward": helpers.remove_decimals(validator_reward)
                        })
                        continue
                    for value in info["others"]:
                        if acct == value["who"]:
                            nominator_stake = value["value"]
                            nominator_reward = nominator_stake * validator_leftover_reward / total_stake
                            result["accounts"][idx]["rewards"][era].append({
                                "validator": validator,
                                "stake": helpers.remove_decimals(nominator_stake),
                                "reward": helpers.remove_decimals(nominator_reward)
                            })
        return result

    ##############################
    # Staking queries
    ##############################

    # Check current nomination targets of given accounts are validators
    def check_nominations(self, accounts):
        nominators = self.map_query("Staking", "Nominators", "")
        validators = self.map_query("Staking", "Validators", "")
        bad_targets = {}
        for acct in accounts:
            bad_targets[acct] = []
            if acct not in nominators:
                log.warning(f"Account {acct} is not nominating")
                continue
            targets = nominators[acct]["targets"]
            if len(targets) == 0:
                log.warning(f"Account {acct} has no targets")
                continue
            for target in targets:
                if target not in validators:
                    log.warning(f"Nominated target {target} of account {acct} is not a validator")
                    bad_targets[acct].append(target)
            if len(bad_targets[acct]) == 0:
                log.info(f"Account {acct} has valid nomination targets")
        return bad_targets

    # Rank validators based on performance over the last given number of eras (defaults to 7)
    def rank_validators(self, eras: int = 7):
        validators = self.map_query("Staking", "Validators", "")
        curr_era = self.item_query("Staking", "ActiveEra")
        curr_era = curr_era['index']
        end_era = curr_era - 1
        start_era = end_era - eras + 1

        # Gather necessary information for era range
        # History depth
        depth = self.item_query("Staking", "HistoryDepth")
        points = {}
        target_era = start_era
        while True:
            eras_points = self.query_era(target_era, self.map_query, "Staking", "ErasRewardPoints", "")
            points = {**points, **eras_points}
            target_era += depth - 1
            if target_era >= end_era:
                break

        totals = {}
        for era in range(start_era, end_era+1):
            log.info(f"Processing era {era}")
            era_points = points[era]

            for validator in validators:
                # Find points
                validator_points = 0
                for value in era_points["individual"]:
                    if value[0] == validator:
                        validator_points = value[1]
                        break
                # Accumulate points
                if validator not in totals:
                    totals[validator] = validator_points
                else:
                    totals[validator] += validator_points

        return sorted(totals, key=totals.get, reverse=True)

    ##############################
    # Actions
    ##############################

    # Nominate given accounts
    # NOTE: function doesn't check if all accounts are validators
    def nominate(self, account, targets, wait_inclusion: bool = True, wait_finality: bool = False):
        log.info(f"Nominating following {len(targets)} accounts: {targets} from {account}")
        # Build call
        nom_call = self.build_call("Staking", "nominate", {'targets': targets})
        # Send transaction
        self.send_transaction(account, nom_call, wait_inclusion, wait_finality)
