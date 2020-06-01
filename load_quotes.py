import csv

from db.base import Session
from db.models import Quote

if __name__ == '__main__':
    session = Session()
    with open('quotes.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    for row in data:
        print(row)
        quote = Quote(row[0], row[1])
        session.add(quote)
    session.commit()
