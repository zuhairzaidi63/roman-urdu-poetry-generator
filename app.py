import torch
import torch.nn as nn
import torch.optim as optim
import streamlit as st

import pickle
class SimpleVocab:
    def __init__(self, vocab):
        self.stoi = vocab.get_stoi()  # Word to index mapping
        self.itos = vocab.get_itos()  # Index to word mapping
        self.default_index = vocab.get_default_index()  # Default index for unknown words

    def __getitem__(self, word):
        return self.stoi.get(word, self.default_index)

    def lookup_token(self, index):
        return self.itos[index] if 0 <= index < len(self.itos) else "<UNK>"

with open('simple_vocab (2).pkl', 'rb') as f:
    vocab = pickle.load(f)

class PoetryLSTM(nn.Module):
    def __init__(self, vocab_size, embedding_dim=128, hidden_dim=256, num_layers=2):
        super(PoetryLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True)

        # Layer Normalization (Added)
        self.layer_norm = nn.LayerNorm(hidden_dim)

        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        lstm_out, _ = self.lstm(x)

        # Apply Layer Normalization
        lstm_out = self.layer_norm(lstm_out)

        out = self.fc(lstm_out[:, -1])  # Use last LSTM output
        return out

# Model
model = PoetryLSTM(vocab_size=len(vocab.stoi))

# Load the model to CPU
model.load_state_dict(torch.load('poetry_lstm_model.pth', map_location=torch.device('cpu')))

import random

def generate_poetry(seed_text, model, vocab, max_words=68):
    model.eval()
    words = seed_text.split()

    for _ in range(max_words):
        encoded = torch.tensor([vocab[word] for word in words[-6:]]).unsqueeze(0)
        with torch.no_grad():
            output = model(encoded)
            next_word = vocab.lookup_token(output.argmax().item())
            words.append(next_word)

    return " ".join(words)
def print_poetry(generated_text):
    formatted_text = generated_text.replace(" <NEWLINE> ", "\n")
    formatted_text = generated_text.replace(" <NEWLINE>", "\n")
    return formatted_text

# Example Usage
st.title('Roman Urdu Poetry Generator')
input_text = st.text_input('Enter the first few words of poetry:', '')
num_words = st.number_input('Enter the number of words to generate:', min_value=5, max_value=100, value=20)
if st.button('Generate Poetry'):
    if input_text:
        generated_poetry = generate_poetry(input_text, model, vocab,num_words)
        poetry=print_poetry(generated_poetry)
        print(poetry)
        st.subheader('Generated Poetry:')
        st.markdown(
            f"""
            <div style="margin-left: 120px; text-align: left;">
                {poetry.replace("\n", "<br><br>")}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.write("Please enter some words to generate poetry.")

