import os

CONFIG_DIR = f"{os.getenv('HOME')}/.config/fma"
CONFIG_PATH = f"{CONFIG_DIR}/config.yaml"
BASE_URL = os.getenv("FMA_BACKEND", "https://backend.flymy.ai/api/v1")
URLS = {"login": f"{BASE_URL}/auth/login/", "deploy": f"{BASE_URL}/deploy/"}

MODEL_TEMPLATE = """from typing import List

from pydantic import BaseModel

from fma.toolkit import model as fma_model


class Input(BaseModel):
    pass


class Output(BaseModel):
    pass


class Model(fma_model.Model):
    requirements: List[str] = []

    def initialize(self):
        pass

    def predict(self, input: Input) -> Output:
        return Output()

"""
