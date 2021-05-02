import dask.dataframe as dd
import os


def convert_jesc_to_dataframe():
    """
    Convert the CSV file of the text to a
    Dask Dataframe 
    """
    dataset_path = "datasets/text_dataset/"
    print("Loading data and converting to Dask Dataframe")
    filename = "raw.txt"
    df = dd.read_csv(dataset_path+filename, sep="\t")
    df.columns = ["English", "Japanese"]

    print("Saving data as Parquet archive")
    df.to_parquet(dataset_path+"jesc_dialogues")
    os.remove(dataset_path+filename)
    os.remove("datasets/raw.tar.gz")


