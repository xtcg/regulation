import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

import numpy as np
import requests
from langchain_core.embeddings import Embeddings
from app.config import settings

MAX_BATCHES = 16
MAX_REQUEST_TOKENS = 200000


class JinaEmbeddings(Embeddings):
    def __init__(self, url: str, api_key: str, model: str, cpu: Optional[bool] = False) -> None:
        super().__init__()
        self.url = url
        self.cpu = cpu
        self.api_key = api_key
        self.model = model

    def get_batch_embedding(self, batch_texts):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"input": batch_texts, "model": self.model, "encoding_format": "float"}
        response = requests.request("POST", url=self.url, json=payload, headers=headers)
        if response.status_code == 200:
            response = response.json()
            return np.array([i['embedding'] for i in response['data']])
        else:
            # print(len(i) for i in batch_texts)
            raise ValueError(f"Error Code {response.status_code}, {response.text}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.cpu:
            payload = {"text": texts}
            response = requests.post(self.url, json=payload)
            if response.status_code == 200:
                return np.array(response.json())
            else:
                raise ValueError(f"Error Code {response.status_code}, {response.text}")
        else:
            length_per_batch = max([len(text) for text in texts])
            num_batch = min(MAX_BATCHES, MAX_REQUEST_TOKENS // length_per_batch)
            batches = math.ceil(len(texts) / num_batch)
            _results = [None] * batches
            with ThreadPoolExecutor(max_workers=8) as executor:
                future_map = {
                    executor.submit(
                        self.get_batch_embedding,
                        texts[i * num_batch : (i + 1) * num_batch],
                    ): i
                    for i in range(batches)
                }
                for future in as_completed(future_map):
                    index = future_map[future]
                    _results[index] = future.result()
            results = np.concatenate(_results, axis=0)
            return results

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


jina_embedding = JinaEmbeddings(url=settings.knowledge.embedding_url, api_key=settings.knowledge.api_key, model=settings.knowledge.embedding_model)
