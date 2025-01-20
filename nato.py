import streamlit as st

# NATO phonetic alphabet encoder dictionary
nato_encoder = {
    'A': 'Beta', 'B': 'Gamma', 'C': 'Cypher', 'D': 'Epsilon',
    'E': 'Zeta', 'F': 'Eta', 'G': 'Theta', 'H': 'Iota',
    'I': 'Kappa', 'J': 'Lambda', 'K': 'Mu', 'L': 'Nu',
    'M': 'Xi', 'N': 'Omicron', 'O': 'Pi', 'P': 'Rho',
    'Q': 'Sigma', 'R': 'Tau', 'S': 'Upsilon', 'T': 'Phi',
    'U': 'Chi', 'V': 'Psi', 'W': 'Omega', 'X': 'Alpha',
    'Y': 'Delta', 'Z': 'Zen', ' ': 'Space'
}


# Function to encrypt a message using the NATO phonetic alphabet
def encrypt_message(message, nato_encoder):
    encrypted_message = ''
    for char in message:
        if char.upper() in nato_encoder:
            encrypted_message += nato_encoder[char.upper()] + ' '
        elif char == ' ':
            encrypted_message += nato_encoder[char] + ' '
        else:
            encrypted_message += char + ' '

    return encrypted_message


# Function to decode an encoded message back to the original message
def decode_message(encoded_message, nato_encoder):
    decoded_message = ''
    words = encoded_message.split()

    for word in words:
        for key, value in nato_encoder.items():
            if value == word:
                decoded_message += key
                break
        else:
            decoded_message += word

    return decoded_message


def main():
    st.title("NATO Phonetic Alphabet Encoder/Decoder")

    # Create two tabs: Encode and Decode
    tab_choice = st.sidebar.radio("Select Tab:", ["Encode", "Decode"])

    if tab_choice == "Encode":
        st.header("Encode Message")
        message_to_encode = st.text_input("Enter the message to encode:")
        if st.button("Encode"):
            encoded_message = encrypt_message(message_to_encode, nato_encoder)
            st.success(f"{encoded_message}")

    elif tab_choice == "Decode":
        st.header("Decode Message")
        message_to_decode = st.text_input("Enter the message to decode:")
        if st.button("Decode"):
            decoded_message = decode_message(message_to_decode, nato_encoder)
            st.success(f"{decoded_message}")

    st.write('Creator:: Abhay Parashar @abhayparashar31 ')


if __name__ == "__main__":
    main()