import os

print("Creating zip")
zip_name = "db_illustrations_bw.zip"
zip_folder = "db_illustrations_bw"
os.system('cd datasets/image_dataset; zip -r -q %s %s' % (zip_name, zip_folder))

print("Removing folder of zip")
os.system("cd datasets/image_dataset; rm -r %s" % zip_folder)