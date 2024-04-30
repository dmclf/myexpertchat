import importlib.resources
from dynaconf import Dynaconf

#root_path = importlib.resources('myexpertchat')
settings = Dynaconf(
    envvar_prefix="MYEXPERTCHAT",
    settings_files=['settings.json', '.secrets.json'],
    # root_path = importlib.resources('myexpertchat')
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
