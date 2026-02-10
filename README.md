# FlyMyAI CLI

CLI app provides functionality to deploy custom models onto fma infrastructure.
It employs features of pydantic library extended with custom field types to describe model's io.
It interacts with fma services to send your models code and to run it on fma's hardware.

## Quickstart

#### Initialization

You have to create a new folder and run `fma init <your_model_name>` inside of it.
This will create one more folder with your model name and a `model.py` file inside of it.
The `model.py` will be prepolutated with:
```python
from typing import List

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
        return {}

```

*__IMPORTANT NOTE__*: even though io is described via pydantic models they are not actually supported in the `predict` method.
Instead `predict` method accepts and returns python dicts.
Support for pydantic models will be added eventually.

### Model development

During this step you simply have to populate the `initialize` and `predict` methods with inferences logic.
You can set instance attributes via accessing `self`, all the imports should be inside of the methods.
You can also specify required libraries and packages in the `requirements` field of `Model` class.

### Deploying the model

If you have finished all the steps above all you need to do is to:

#### Log in

You can do this via `fma login --username <username> --password <password>`
or by providing one/none, missing ones will be prompted.

#### Actually deploy

By running `fma deploy`
After this the data about your model will be written into `metadata.yaml` file.


## Extra info

### Additional fields

Currenly standard python `str, int, bool, float` are available.   
The also can be used in combination with `typing.Optional`   
You can specify image or file fields in the io classes by:

```
from fma.toolkit.fields.image import Image
```

or

```
from fma.toolkit.fields.file import File
```

*Note* that `File` is currently supported **only** as the output


### Deleting deployed model

You can delete the deployed model if you don't need it anymore:
`fma delete`

### Updating the model

`fma update` will delete the model and redeploy it under the same name if available.

### Fetching startup logs

`fma logs --output-file logs.tx` will download logs into specified file or display them in stdout otherwise.
