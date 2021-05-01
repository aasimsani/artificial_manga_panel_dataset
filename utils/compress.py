import os

print("Creating zip")
zip_name = "db_illustrations_bw.zip"
zip_folder = "db_illustrations_bw"
if not os.path.isfile("dataset/image_dataset/"+zip_name):
    os.system('cd datasets/image_dataset; zip -r -q %s %s' % (zip_name, zip_folder))
else:
    print("Zip file already exists")

print("Please confirm removal the folder of the zip now:")
inp = input("y/n")
if inp.lower() = "y":
    os.system("cd datasets/image_dataset; rm -r %s" % zip_folder)
else:
    print("You have chosen not to remove the zip folder")
