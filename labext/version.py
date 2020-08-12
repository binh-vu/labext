import pkg_resources


if __name__ == '__main__':
    print("You are using LabExt version", pkg_resources.get_distribution("labext").version)
