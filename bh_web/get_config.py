from beacon_huntress.src.bin.data import get_data, del_data, add_data, get_run_conf
import yaml

conf = get_run_conf("34bb25b5-9a8e-11ee-8115-34298f791f87")

# with open(conf) as conf_file:
#     config = yaml.safe_load(conf_file)

config = yaml.safe_load(conf)
print(conf)