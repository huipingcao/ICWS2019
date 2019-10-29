import subprocess

# Call the run_model.py inside the model folder
result_s1 = subprocess.call(["python", "Run_Models.py"], cwd="model")
