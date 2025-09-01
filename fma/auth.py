from fma._config_manager import config_manager


def check_authorization():
    auth_token = config_manager.get("auth_token")
    if auth_token is None:
        print("ERROR: You need to authenticate first! Run `fma login`")
        exit()
