"""Defines a class for holding a vocabulary set."""

import torchtext

import logging


logger = logging.getLogger(__name__)


class Vocab:
    """
    Class for abstracting a set of vocabulary.

    Basically just wraps a dict object for terms and dict object for
    characters.

    Parameters
    ----------
    unk_term : str
        The code to use for unknown terms.

    unk_char : str
        The code to use for unknown chars.

    word_vec_dim : int
        The dimension of the vector word embedding. As of now, can only be 50,
        100, 200, or 300.

    cache : str
        Optional path to GloVe cache. If not given and the cache cannot be
        found automatically, the GloVe embeddings will be downloaded.

    Attributes
    ----------
    unk_term : str
        The code to use for unknown terms.

    unk_char : str
        The code to use for unknown chars.

    glove : :obj:`torchtext.vocab.GloVe`
        GloVe word embeddings.

    chars_stoi : dict
        Keys are chars, values are unique ids (int).

    chars_itos : dict
        Keys are ids (int), values are chars.

    """

    def __init__(self, unk_term="UNK", unk_char="UNK", word_vec_dim=300,
                 cache=None):
        self.unk_term = unk_term
        self.unk_char = unk_char
        self.word_vec_dim = word_vec_dim
        self.chars_stoi = {unk_char: 0}
        self.chars_itos = {0: unk_char}
        self.glove = torchtext.vocab.GloVe(
            name="6B", dim=self.word_vec_dim, cache=cache)

        for s in self.glove.stoi:
            for ch in s:
                ind = self.chars_stoi.setdefault(
                    ch, len(self.chars_stoi))
                self.chars_itos.setdefault(ind, ch)
                ind = self.chars_stoi.setdefault(
                    ch.upper(), len(self.chars_stoi))
                self.chars_itos.setdefault(ind, ch.upper())

    @property
    def n_chars(self):
        return len(self.chars)

    @property
    def dim(self):
        return self.n_chars + self.word_vec_dim

    def sent2tensor(self, sent):
        """
        Transform a sentence into a tensor.

        Parameters
        ----------
        sent : str
            The sentence to transform.

        Returns
        -------
        tuple (list of :obj:`torch.tensor`, :obj:`torch.tensor`)
            The first item is a list of length `len(sent)` of tensors, each of
            which has size `[len(sent[i]) x self.n_chars]`.
            The second item has is a tensor of size
            `[len(sent) x self.word_vec_dim]`.

        """
        char_tensors = []
        word_tensors = []
        for tok in sent:
            word_tensors.append(
                self.glove[self.glove.stoi.get(tok.lower(), -1)])
            tmp_list = []
            for ch in tok:
                tmp = torch.zeros(self.n_chars)
                tmp[self.chars_stoi.get(ch, 0)] = 1
                tmp_list.append(tmp.view(1, -1))
            char_tensors.append(torch.cat(tmp_list))
        return char_tensors, word_tensors
