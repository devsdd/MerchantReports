import yaml

def load_config(configFile):
    with open(configFile, "r") as f:
        yamlConfig = yaml.safe_load(f)
    
    return yamlConfig

if __name__ == "__main__":
    raise Exception(__file__ + " is not supposed to be run in standalone mode.")
