import base58
from bip_utils import *

coinType = Bip44Coins.SOLANA # Define the coin type : Bip44Coins.ETHEREUM, Bip44Coins.BITCOIN , Bip44Coins.DOGECOIN,...

def generateKeysFromMnemonic(mnemonic: str):
    seed = Bip39SeedGenerator(mnemonic).Generate() # Generate the seed from the mnemonic phrase

    if coinType == Bip44Coins.SOLANA: 
        masterKey = Bip44.FromSeed(seed, coinType) # For Solana we use a specific derivation path
           
        accountKey = masterKey.Purpose().Coin().Account(0) # Derive the account key
        changeKey = accountKey.Change(Bip44Changes.CHAIN_EXT)  # Derive the acccount key for public address transactions
        privKeyBytes = changeKey.PrivateKey().Raw().ToBytes() # Extract the private key
        pubAddrBytes = changeKey.PublicKey().RawCompressed().ToBytes()[1:] # Extract the public address
        key_pair = privKeyBytes + pubAddrBytes # Combine the private key and public address to form the keypair

        return changeKey.PublicKey().ToAddress(), base58.Base58Encoder.Encode(key_pair) # Return the public address and the private key in base58 format
   

    masterKey = Bip44.FromSeed(seed, coinType).DeriveDefaultPath() # For coins other than Solana, derive the default path
    return masterKey.PublicKey().ToAddress(), masterKey.PrivateKey().Raw().ToHex() # Return public address and private key in hex format



if __name__ == "__main__":
    mnemonic = input("Enter your mnemonic phrase(12 or 24 words): ")
    public_address, private_key = generateKeysFromMnemonic(mnemonic)
    print(f"Public Address: {public_address}")
    print(f"Private Key: {private_key}")
