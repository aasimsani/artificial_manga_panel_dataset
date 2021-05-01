import os


print("Decompressing images")
zip_file = "db_illustrations_bw.zip"
os.system("cd datasets/image_dataset; unzip %s" % zip_file)

print("Please confirm removal of the zip:")
inp = input("y/n")
if inp.lower() = "y":
    os.system("cd datasets/image_dataset; rm %s" % zip_file)
else:
    print("You have chosen not to remove the zip folder")