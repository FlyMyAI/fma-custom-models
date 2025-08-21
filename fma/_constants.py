import os

CONFIG_DIR = f"{os.getenv('HOME')}/.config/fma"
CONFIG_PATH = f"{CONFIG_DIR}/config.yaml"
BASE_URL = "https://backend.flymy.ai/api/v1"
URLS = {"login": f"{BASE_URL}/auth/login/"}

MODEL_TEMPLATE = """from typing import List

from fma.toolkit import model as fma_model


class Input:
    pass


class Output:
    pass


class Model(fma_model.Model):
    requirements: List[str] = []

    def initialize(self):
        pass

    def predict(self, input: Input) -> Output:
        return Output()

"""
