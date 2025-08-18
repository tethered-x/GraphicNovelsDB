# pip install mysql-connector-python
# pip install bcrypt
# pip install tabulate

import subprocess

def install_packages_from_list(package_list):
    for package in package_list:
        try:
            subprocess.check_call(['pip', 'install', package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")

# Example usage:
packages_to_install = ["mysql-connector-python", "bcrypt", "tabulate"]
install_packages_from_list(packages_to_install)