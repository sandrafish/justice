import csv

def read_links():
    with open("inmate_details.csv", "r") as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            print line[1]

if __name__ == "__main__":
    read_links()