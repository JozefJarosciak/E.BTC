import sys
import time
import requests
from web3 import Web3
from web3.exceptions import TransactionNotFound

##################################################
############         CONFIG       ################
##################################################

# Wallet info - Enter your SEEDING Wallet details
main_wallet_address = '0x.... your_wallet_address_metamask'
main_wallet_address_private_key = 'your_wallet_address_metamask_private_key' # be careful to not expose this to anyone

# Set gas-related claiming parameters
only_claim_if_gas_is_below = 700_000
max_priority_fee_per_gas = 4_000
max_transactions_per_wallet = 25
balance_spent = 0
cooling_period_between_new_wallets = 10  # in seconds

# Budgets for mints
max_Spend_PLS = 20_000
max_total_transactions = 1_000  # Set your desired limit
stop_mining_at_PLS = 40

##################################################

# ANSI escape code for colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'

# Print out the configuration settings
print(f"{CYAN}{'=' * 60}{RESET}")
print(f"{CYAN}||{'E-BTC AUTO MINER v1.0'.center(56)}||{RESET}")
print(f"{GREEN}User Configuration:{RESET}")
print(f"1. Mine E.BTC until {YELLOW}either{RESET} of these conditions are met:")
print(f"   - A maximum spend limit of {YELLOW}{max_Spend_PLS:,} PLS{RESET} is reached.")
print(f"   - A total of {YELLOW}{max_total_transactions}{RESET} transactions have been processed.")
print(f"2. Mining will stop if the balance is below {YELLOW}{stop_mining_at_PLS} PLS{RESET}.")
print(f"3. E.BTC will be mined only when gwei is below {YELLOW}{only_claim_if_gas_is_below:,}{RESET}.")
print(f"{CYAN}{'=' * 60}{RESET}\n")

total_balance_EvmBitcoinToken = 0
rpc_url = f"https://rpc.pulsechain.com"
web3 = Web3(Web3.HTTPProvider(rpc_url))

# EvmBitcoinToken - Smart contract details
contract_address = web3.toChecksumAddress('0x10d46D6F8f691d3439A781FC5E7BE598Ab67b393')
contract_abi = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {
    "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "allowance", "type": "uint256"}, {"internalType": "uint256", "name": "needed", "type": "uint256"}],
    "name": "ERC20InsufficientAllowance", "type": "error"}, {"inputs": [{"internalType": "address", "name": "sender", "type": "address"}, {"internalType": "uint256", "name": "balance", "type": "uint256"},
                                                                        {"internalType": "uint256", "name": "needed", "type": "uint256"}], "name": "ERC20InsufficientBalance", "type": "error"},
                {"inputs": [{"internalType": "address", "name": "approver", "type": "address"}], "name": "ERC20InvalidApprover", "type": "error"},
                {"inputs": [{"internalType": "address", "name": "receiver", "type": "address"}], "name": "ERC20InvalidReceiver", "type": "error"},
                {"inputs": [{"internalType": "address", "name": "sender", "type": "address"}], "name": "ERC20InvalidSender", "type": "error"},
                {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}], "name": "ERC20InvalidSpender", "type": "error"}, {"anonymous": False, "inputs": [
        {"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": False, "internalType": "address", "name": "spender", "type": "address"},
        {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"},
                {"anonymous": False, "inputs": [{"indexed": False, "internalType": "string", "name": "message", "type": "string"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}],
                 "name": "Debug", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                                                                                    {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                                                                                    {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"},
                {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance",
                 "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
                {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "approve",
                 "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
                {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view",
                 "type": "function"}, {"inputs": [], "name": "currentHalving", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
                {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
                {"inputs": [], "name": "initialReward", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
                {"inputs": [], "name": "maxSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
                {"inputs": [], "name": "mint", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
                {"inputs": [], "name": "mintCount", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
                {"inputs": [{"internalType": "address", "name": "", "type": "address"}], "name": "mintCountPerWallet", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view",
                 "type": "function"}, {"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
                {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
                {"inputs": [], "name": "totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
                {"inputs": [{"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "name": "transfer",
                 "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
                {"inputs": [{"internalType": "address", "name": "from", "type": "address"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "value", "type": "uint256"}],
                 "name": "transferFrom", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)


def cleanup_and_transfer_if_key_provided():
    # Check if an Ethereum public key is provided as a command-line argument
    if len(sys.argv) > 1:
        eth_public_key = sys.argv[1]

        # Ensure the public key is valid (basic check)
        if not Web3.isAddress(eth_public_key):
            print(f"{RED}Invalid Ethereum public key provided.{RESET}")
            return

        # Fetch balances
        ebtc_balance = get_EvmBitcoinToken_balance(eth_public_key)
        pls_balance = get_pls_balance(eth_public_key)

        print(f"{CYAN}E.BTC balance to be transferred: {YELLOW}{ebtc_balance} E.BTC{RESET}")
        print(f"{CYAN}PLS balance to be transferred: {YELLOW}{pls_balance} PLS{RESET}")

        # Assuming you have the corresponding private key access method here
        private_key = get_private_key_for_public_key(eth_public_key)  # Implement this function based on your setup

        # Transfer E.BTC if balance is greater than 0
        if ebtc_balance > 0:
            transfer_tokens(eth_public_key, private_key, main_wallet_address, ebtc_balance)
        else:
            print(f"{GREEN}No E.BTC balance to transfer.{RESET}")

        # Transfer PLS if balance is greater than 0
        if pls_balance > 0:
            clean_account_send_pls(eth_public_key, private_key, main_wallet_address)
        else:
            print(f"{GREEN}No PLS balance to transfer.{RESET}")

        print("Transfers completed. Exiting program.")
        sys.exit(0)  # Exit the program after the transfers are completed


def get_gas_price():
    retries = 10
    for attempt in range(retries):
        try:
            gas_price_data = requests.post(url=rpc_url, json={"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1})
            gas_price_data.raise_for_status()  # Check for HTTP request errors
            gas_price_gwei = int(gas_price_data.json()['result'], 16) / 1e9
            return round(gas_price_gwei, 2)
        except (requests.HTTPError, requests.exceptions.RequestException, ValueError) as e:
            print(f"Attempt {attempt + 1}/{retries} - Error fetching gas price: {e}")
            if attempt < retries - 1:
                time.sleep(10)
            else:
                raise
    return None


def generate_new_wallet():
    account = web3.eth.account.create()
    # print(f"Created a new EIP-55 compliant wallet: {account.address}", f"Private Key: {account.privateKey.hex()}")
    print(f"Created a new temporary EIP-55 compliant wallet: {BLUE}{account.address}{RESET}")
    with open("EvmBitcoinToken.log", "a") as log_file:
        log_file.write(f"Address: {account.address}, Private Key: {account.privateKey.hex()}\n")
    return account.address, account.privateKey.hex()


def get_private_key_for_public_key(public_key, log_file_path="EvmBitcoinToken.log"):
    """
    Retrieve the private key for a given public key from the log file.

    :param public_key: The public Ethereum address to find the private key for.
    :param log_file_path: Path to the log file containing the address and private key pairs.
    :return: The private key if found, None otherwise.
    """
    try:
        # Ensure the public key is in the correct format
        public_key = Web3.toChecksumAddress(public_key)
    except ValueError:
        print("Invalid Ethereum address provided.")
        return None

    try:
        with open(log_file_path, "r") as log_file:
            for line in log_file:
                if public_key in line:
                    # Assuming the line format is 'Address: {address}, Private Key: {privateKey}\n'
                    parts = line.split(", Private Key: ")
                    if len(parts) == 2:
                        return parts[1].strip()  # Remove any trailing newline or spaces
    except FileNotFoundError:
        print(f"Log file not found at path: {log_file_path}")
    except Exception as e:
        print(f"An error occurred while searching for the private key: {e}")

    print("Private key not found for the provided public address.")
    return None



def mint_tokens(wallet_address, private_key):
    time.sleep(15)
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            nonce = web3.eth.getTransactionCount(wallet_address, 'pending')
            chain_id = web3.eth.chain_id
            contract_function = contract.functions.mint()

            estimated_gas = contract_function.estimateGas({'from': wallet_address})

            latest_block = web3.eth.get_block('latest')
            base_fee = latest_block['baseFeePerGas']
            base_fee_increased = base_fee + (base_fee * 40 // 100)
            max_priority_fee_per_gas_wei = base_fee // 11
            max_fee_per_gas = base_fee_increased + 2 * max_priority_fee_per_gas_wei

            transaction = contract_function.buildTransaction({
                'chainId': chain_id,
                'gas': estimated_gas,
                'maxFeePerGas': max_fee_per_gas,
                'maxPriorityFeePerGas': max_priority_fee_per_gas_wei,
                'nonce': nonce,
            })

            signed_txn = web3.eth.account.signTransaction(transaction, private_key)
            tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(f"Mining transaction sent, TX Hash: {tx_hash.hex()}")

            while True:
                try:
                    time.sleep(2)
                    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
                    if tx_receipt is not None and tx_receipt['blockNumber'] is not None:
                        print("Mining completed, transaction confirmed!")
                        return tx_receipt
                except TransactionNotFound:
                    print("Transaction not yet confirmed, waiting...")
                time.sleep(5)  # Wait before checking again

        except ValueError as e:
            if 'nonce too low' in str(e):
                print("Nonce too low, retrying...")
                time.sleep(10)  # Wait before retrying
            else:
                raise e
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)  # Wait before retrying or ending the attempt

    raise Exception("Failed to mint after retrying.")


def transfer_tokens(from_address, private_key, to_address, amount):
    amount_in_smallest_unit = web3.toWei(amount, 'ether')
    evm_bitcoin_token_contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    retry_attempts = 3  # Set the number of retry attempts
    for attempt in range(retry_attempts):
        try:
            nonce = web3.eth.getTransactionCount(from_address, 'pending')
            chain_id = web3.eth.chain_id
            contract_function = evm_bitcoin_token_contract.functions.transfer(
                to_address,
                amount_in_smallest_unit
            )

            estimated_gas = 60000

            latest_block = web3.eth.get_block('latest')
            base_fee = latest_block['baseFeePerGas']
            base_fee_increased = base_fee + (base_fee * 40 // 100)
            max_priority_fee_per_gas_wei = base_fee // 12
            max_fee_per_gas = base_fee_increased + 2 * max_priority_fee_per_gas_wei

            txn_dict = contract_function.buildTransaction({
                'chainId': chain_id,
                'gas': estimated_gas,
                'maxFeePerGas': max_fee_per_gas,
                'maxPriorityFeePerGas': max_priority_fee_per_gas_wei,
                'nonce': nonce,
            })

            signed_txn = web3.eth.account.signTransaction(txn_dict, private_key)
            tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(f"E.BTC Token transfer initiated. Transaction hash: {tx_hash.hex()}")
            while True:
                try:
                    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
                    if tx_receipt is not None and tx_receipt['blockNumber'] is not None:
                        print("E.BTC Token transfer successful. Transaction is confirmed.")
                        return tx_receipt
                except Exception as e:
                    print("Waiting for transaction to complete...")
                time.sleep(10)

        except ValueError as e:
            if 'nonce too low' in str(e):
                print("Nonce too low, retrying...")
                time.sleep(10)
            else:
                raise e
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)

    raise Exception("Failed to transfer tokens after retrying.")


def send_pls(from_address, private_key, to_address, amount):
    # Convert the amount to Wei

    amount_in_wei = web3.toWei(amount, 'ether')
    retry_attempts = 3  # Define the number of retry attempts

    for attempt in range(retry_attempts):
        try:
            nonce = web3.eth.getTransactionCount(from_address, 'pending')
            chain_id = web3.eth.chain_id

            gas_price = web3.eth.gas_price
            gas_limit = 21000
            gas_cost = gas_price * gas_limit

            # Fetch the current balance
            current_balance_wei = web3.eth.getBalance(from_address)
            current_balance = web3.fromWei(current_balance_wei, 'ether')
            amount_in_wei = web3.toWei(amount, 'ether')

            # Calculate the remaining balance after the amount to be sent
            remaining_balance_wei = current_balance_wei - amount_in_wei
            remaining_balance = web3.fromWei(remaining_balance_wei, 'ether')

            # Calculate what percentage of the balance will be left
            percent_left = (remaining_balance_wei / current_balance_wei) * 100 if current_balance_wei != 0 else 0

            print(f"Current balance in seeder account: {GREEN}{current_balance:,.2f} PLS{RESET}")
            print(f"Amount to be sent: {YELLOW}{amount:,.2f} PLS{RESET}")
            print(f"Estimated balance left in seeder account: {GREEN}{remaining_balance:,.2f} PLS{RESET} ({percent_left:.2f}%)")

            # Ensure there's enough balance to cover the transfer and the gas
            if current_balance_wei >= amount_in_wei + gas_cost:
                tx = {
                    'nonce': nonce,
                    'to': to_address,
                    'value': amount_in_wei,
                    'gas': gas_limit,
                    'gasPrice': gas_price,
                    'chainId': chain_id,
                }

                signed_tx = web3.eth.account.sign_transaction(tx, private_key)
                tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
                print(f"Sending {web3.fromWei(amount_in_wei, 'ether')} PLS to {to_address}. Transaction hash: {tx_hash.hex()}")

                # Wait for the transaction to be mined
                while True:
                    try:
                        tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
                        if tx_receipt and tx_receipt['blockNumber']:
                            print(f"PLS successfully sent. Transaction hash: {tx_hash.hex()}")
                            return tx_receipt
                    except Exception as e:
                        print("Waiting for transaction to be confirmed...")
                    time.sleep(10)
            else:
                raise ValueError(f"Insufficient funds for the transfer. Account balance is {web3.fromWei(current_balance, 'ether')} PLS.")

        except ValueError as e:
            if 'nonce too low' in str(e):
                print("Nonce too low, retrying...")
                time.sleep(10)
            else:
                print(e)
                break  # Exit the retry loop on a ValueError that is not 'nonce too low'
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)

    raise Exception("Failed to send PLS after retrying.")


def get_pls_balance(address):
    balance_wei = web3.eth.getBalance(address)
    balance_pls = web3.fromWei(balance_wei, 'ether')
    return round(float(balance_pls), 6)


def get_EvmBitcoinToken_balance(address):
    evm_bitcoin_token_contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    balance = evm_bitcoin_token_contract.functions.balanceOf(address).call()
    balance_tokens = web3.fromWei(balance, 'ether')
    return round(float(balance_tokens), 6)


def clean_account_send_pls(from_address, private_key, to_address):
    time.sleep(10)
    try:
        pls_balance = web3.eth.getBalance(from_address)
        gas_price = web3.eth.gas_price  # Fetch current gas price
        gas_limit = 21000  # Standard gas limit for a simple transfer

        # Calculate the gas cost
        gas_cost = gas_price * gas_limit

        # Ensure there's enough balance for gas + a small amount to send
        if pls_balance > gas_cost:
            # Calculate the amount after gas cost
            amount_to_send = pls_balance - gas_cost

            nonce = web3.eth.getTransactionCount(from_address, 'pending')
            chain_id = web3.eth.chain_id

            # Prepare transaction
            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': amount_to_send,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'chainId': chain_id,
            }

            # Sign and send the transaction
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(f"Final balance transfer initiated. Transaction hash: {tx_hash.hex()}")

            # Wait for transaction confirmation
            while True:
                try:
                    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
                    if tx_receipt and tx_receipt['blockNumber']:
                        print("Reminder of the PLS balance successfully transferred back to seeding wallet!")
                        return tx_receipt
                except Exception as e:
                    print("Transaction not yet confirmed. Waiting...")
                time.sleep(10)
        else:
            print("Not enough balance to cover the gas for the final balance transfer.")
    except Exception as e:
        print(f"An error occurred during the final balance transfer: {e}")


def send_pls_new_wallet(from_address, private_key, to_address):
    retry_attempts = 3  # Define the number of retry attempts

    for attempt in range(retry_attempts):
        try:
            nonce = web3.eth.getTransactionCount(from_address, 'pending')
            chain_id = web3.eth.chain_id
            gas_price = web3.eth.gas_price  # Fetch current gas price
            gas_limit = 21000  # Standard gas limit for a simple PLS transfer

            # Calculate the total gas cost
            gas_cost = gas_price * gas_limit

            # Fetch the current balance
            current_balance = web3.eth.getBalance(from_address)

            # Calculate the amount to send after deducting the gas cost
            amount_to_send = current_balance - gas_cost

            # Check if the calculated amount to send is positive
            if amount_to_send > 0:
                tx = {
                    'nonce': nonce,
                    'to': to_address,
                    'value': amount_to_send,
                    'gas': gas_limit,
                    'gasPrice': gas_price,
                    'chainId': chain_id,
                }

                signed_tx = web3.eth.account.sign_transaction(tx, private_key)
                tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
                print(f"Sending remaining balance minus gas costs to {to_address}. Transaction hash: {tx_hash.hex()}")

                # Wait for the transaction to be mined
                while True:
                    try:
                        tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
                        if tx_receipt and tx_receipt['blockNumber']:
                            print(f"Remaining balance successfully sent. Transaction hash: {tx_hash.hex()}")
                            return tx_receipt
                    except Exception as e:
                        print("Waiting for transaction to be confirmed...")
                        time.sleep(10)
            else:
                print("Not enough balance to cover the gas cost for the transfer.")
                return

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)

    raise Exception("Failed to send PLS after retrying.")


def automate_minting_and_transfer():
    time.sleep(5)
    global balance_spent, total_balance_EvmBitcoinToken
    account = 1
    total_transactions = 0
    # Initialize variables for the upcoming (next new) account details
    upcoming_new_wallet_address, upcoming_new_wallet_private_key = None, None
    # Flag to indicate if it's the first wallet being processed
    is_first_wallet = True

    print()
    print(f"\n{BLUE}{'*' * 65}{RESET}")
    print(f"{BLUE}*  Mining new wallet #{account}{RESET}")
    print(f"{BLUE}{'*' * 65}{RESET}\n")
    while balance_spent < (max_Spend_PLS - stop_mining_at_PLS):
        # Generate upcoming new wallet address and private key at the beginning of the loop
        if not upcoming_new_wallet_address:
            upcoming_new_wallet_address, upcoming_new_wallet_private_key = generate_new_wallet()

        new_wallet_address, new_wallet_private_key = upcoming_new_wallet_address, upcoming_new_wallet_private_key
        # Only send PLS from the main wallet for the first wallet
        if is_first_wallet:
            PLS_to_send = max_Spend_PLS - balance_spent
            send_pls(main_wallet_address, main_wallet_address_private_key, new_wallet_address, PLS_to_send)
            is_first_wallet = False

        balance_EvmBitcoinToken = 0

        for i in range(max_transactions_per_wallet):
            total_transactions += 1
            print('')
            print('------------------------------------')
            print(f"{MAGENTA}Preparing mining transaction #{i + 1} in wallet #{account} ({new_wallet_address}){RESET}")

            while True:
                gas_price = get_gas_price()
                if gas_price is None:
                    print("Error fetching gas price. Retrying...")
                    time.sleep(10)
                    continue
                elif gas_price >= only_claim_if_gas_is_below:
                    print(f"Gas price too high: {gas_price:,} gwei. Waiting for it to drop below {only_claim_if_gas_is_below:,} gwei.")
                    time.sleep(10)
                else:
                    break

            gas_price_percentage = (gas_price / only_claim_if_gas_is_below) * 100
            print(f"Gas price acceptable: {gas_price:,.0f} gwei ({gas_price_percentage:.2f}% of max). Proceeding with mining transaction.")

            balance_before = get_pls_balance(new_wallet_address)
            print(f'Current balance: {GREEN}{balance_before:,.2f} PLS{RESET}')

            # Mint tokens
            mint_tokens(new_wallet_address, new_wallet_private_key)
            balance_after = get_pls_balance(new_wallet_address)
            transaction_cost = balance_before - balance_after
            balance_spent += transaction_cost

            print(f"Transaction Cost = {transaction_cost:.2f} PLS")

            current_balance_EvmBitcoinToken = get_EvmBitcoinToken_balance(new_wallet_address)
            mined_EvmBitcoinToken = current_balance_EvmBitcoinToken - balance_EvmBitcoinToken
            total_balance_EvmBitcoinToken += mined_EvmBitcoinToken
            balance_EvmBitcoinToken = current_balance_EvmBitcoinToken
            print(f"Mined in this transaction: {mined_EvmBitcoinToken:.2f} E.BTC")
            print(f"Total mined so far: {CYAN}{total_balance_EvmBitcoinToken:.2f} E.BTC{RESET}")

        print('')
        print('------------------------------------')
        print("Mining wallet #", account, 'completed!')

        # Prepare for transferring the mined E.BTC to the seeder wallet
        if balance_EvmBitcoinToken > 0:
            print(f"Moving {GREEN}{balance_EvmBitcoinToken} E.BTC{RESET}, from wallet #{account} back to the Seeding wallet!")
            transfer_tokens(new_wallet_address, new_wallet_private_key, main_wallet_address, balance_EvmBitcoinToken)

        # Generate the next new wallet in advance
        upcoming_new_wallet_address, upcoming_new_wallet_private_key = generate_new_wallet()
        time.sleep(5)  # Wait a bit before attempting to transfer the remaining balance

        remaining_pls_balance = get_pls_balance(new_wallet_address) - 5  # Assuming a small amount to cover the gas for the transfer
        if remaining_pls_balance > 0:
            if not is_first_wallet:
                print(f"Transferring remaining PLS balance of: {GREEN}{remaining_pls_balance} PLS{RESET} to the next new wallet.")
                send_pls_new_wallet(new_wallet_address, new_wallet_private_key, upcoming_new_wallet_address)

        if (balance_spent >= (max_Spend_PLS - stop_mining_at_PLS)) or (total_transactions >= max_total_transactions):
            print('!!!!!!!!!!!!!!!!')
            print('!!! THE END !!!!')
            # If this was the last run, send the remaining PLS back to the seeder wallet
            remaining_pls_balance = get_pls_balance(upcoming_new_wallet_address) - 5
            if remaining_pls_balance > 0:
                print(f"Final clean-up: Transferring remaining PLS balance of: {remaining_pls_balance} PLS back to the seeder wallet.")
                clean_account_send_pls(upcoming_new_wallet_address, upcoming_new_wallet_private_key, main_wallet_address)
            return

        account += 1
        total_accounts = account * 25
        print(f'{cooling_period_between_new_wallets} second cooling period between wallets:')
        for i in range(cooling_period_between_new_wallets, 0, -1):
            print(i, end=' ', flush=True)
            time.sleep(1)
        print('\nCooling period ends!')
        print(f"\n{BLUE}{'*' * 65}{RESET}")
        print(f"{BLUE}*  Mining new wallet #{account}{RESET}")
        print(f"{BLUE}{'*' * 65}{RESET}\n")


# Start the process
if __name__ == "__main__":
    cleanup_and_transfer_if_key_provided()
    # If no key is provided or the cleanup function exits, continue with mining.
    automate_minting_and_transfer()
