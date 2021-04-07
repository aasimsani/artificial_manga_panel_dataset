import os


print("Decompressing images")
zip_file = "db_illustrations.zip"
os.system("cd datasets/image_dataset; unzip %s" % zip_file)

print("Removing zip of images")
os.system("cd datasets/image_dataset; rm %s" % zip_file)