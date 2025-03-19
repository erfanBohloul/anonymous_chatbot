from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from credentials import AES_KEY



def pad(data):
   # Calculate the number of bytes to pad
    padding_length = AES.block_size - len(data) % AES.block_size
    # Create the padding byte
    padding = bytes([padding_length] * padding_length)
    return data + padding

# Function to unpad the data
def unpad(data):
    # Get the last byte, which indicates the number of padding bytes
    padding_length = data[-1]
    return data[:-padding_length]


def encrypt(text):
    key = AES_KEY

    # Convert username to bytes
    text_bytes = text.encode('utf-8')
    
    # Generate a random IV
    iv = get_random_bytes(AES.block_size)
    
    # Create AES cipher in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad the username to match block size
    padded_username = pad(text_bytes, AES.block_size)
    
    # Encrypt the username
    ciphertext = cipher.encrypt(padded_username)
    
    # Combine IV and ciphertext
    encrypted_data = iv + ciphertext
    
    # Encode in base64 for easy storage/transmission
    return base64.b64encode(encrypted_data).decode('utf-8')


def decrypt(ciphertext, key):
    # Decode base64 ciphertext
    encrypted_data = base64.b64decode(ciphertext.encode('utf-8'))
    
    # Extract IV and ciphertext
    iv = encrypted_data[:AES.block_size]
    ciphertext_bytes = encrypted_data[AES.block_size:]
    
    # Create AES cipher in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Decrypt the ciphertext
    padded_text = cipher.decrypt(ciphertext_bytes)
    
    # Unpad the text
    text_bytes = unpad(padded_text, AES.block_size)
    
    # Convert bytes to string
    return text_bytes.decode('utf-8')