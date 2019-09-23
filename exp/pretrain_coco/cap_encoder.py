import copy
import torch
import torch.nn as nn
import pytorch_transformers

import utils.io as io


class CapEncoderConstants(io.JsonSerializableClass):
    def __init__(self):
        super().__init__()
        self.model = 'BertModel'
        self.tokenizer = 'BertTokenizer'
        self.pretrained_weights = 'bert-base-uncased'
        self.max_len = 15


class CapEncoder(nn.Module,io.WritableToFile):
    def __init__(self,const):
        super().__init__()
        self.const = copy.deepcopy(const)
        self.model = getattr(
            pytorch_transformers,
            self.const.model).from_pretrained(self.const.pretrained_weights)
        self.tokenizer = getattr(
            pytorch_transformers,
            self.const.tokenizer).from_pretrained(self.const.pretrained_weights)
    
    @property
    def pad_token(self):
        return self.tokenizer.pad_token

    @property
    def pad_token_id(self):
        return self.tokenizer._convert_token_to_id(self.pad_token)

    def tokenize(self,caption):
        token_ids = self.tokenizer.encode(caption,add_special_tokens=True)
        tokens = [
            self.tokenizer._convert_id_to_token(t_id) for t_id in token_ids]
        return token_ids, tokens

    def pad_list(self,list_to_pad,pad_item,max_len):
        L = len(list_to_pad)
        if L==max_len:
            padded_list = list_to_pad[:]
        elif L > max_len:
            padded_list = list_to_pad[:max_len]
        else:
            padding = []
            for i in range(max_len-L):
                padding.append(pad_item)
            
            padded_list = list_to_pad + padding
        
        return padded_list

    def tokenize_batch(self,captions,pad_tokens=True,max_len=None):
        batch_token_ids = []
        batch_tokens = []
        token_lens = []
        max_token_len = 0
        for cap in captions:
            token_ids, tokens = self.tokenize(cap)
            batch_token_ids.append(token_ids)
            batch_tokens.append(tokens)
            token_len = len(tokens)
            token_lens.append(token_len)
            max_token_len = max(max_token_len,token_len)

        if max_len is not None:
            max_token_len = min(max_len,max_token_len)

        if pad_tokens is True:
            for i in range(len(captions)):
                batch_token_ids[i] = self.pad_list(
                    batch_token_ids[i],
                    self.pad_token_id,
                    max_token_len)
                batch_tokens[i] = self.pad_list(
                    batch_tokens[i],
                    self.pad_token,
                    max_token_len)
        
        return batch_token_ids, batch_tokens, token_lens

    def forward(self,batch_token_ids):
        return self.model(batch_token_ids)[0]



if __name__=='__main__':
    const = CapEncoderConstants()
    cap_encoder = CapEncoder(const)
    caps = ['i am here for fun','what are you here for?']
    token_ids, tokens, token_lens = cap_encoder.tokenize_batch(caps)
    token_ids = torch.LongTensor(token_ids)
    output = cap_encoder(token_ids)
    import pdb; pdb.set_trace()
