def read_cfg(file_name: str):
    with open(file_name, "r") as f:
        d = {}
        for line in f.readlines():
            sep = line.strip().split('=')
            d[sep[0]] = sep[1]
        return d


def write_cfg(file_name: str, cfg: dict):
    with open(file_name, "w") as f:
        f.writelines(["{}={}\n".format(k, cfg[k]) for k in cfg])
