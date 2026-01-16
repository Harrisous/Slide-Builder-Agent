from jinja2 import Environment, FileSystemLoader
import os

print(f"CWD: {os.getcwd()}")
env = Environment(loader=FileSystemLoader('.'))
try:
    template = env.get_template('templates/slide_template.html')
    print("--- Template Source Start ---")
    with open(template.filename, 'r') as f:
        print(f.read()[:500])
    print("--- Template Source End ---")
except Exception as e:
    print(f"Error: {e}")
