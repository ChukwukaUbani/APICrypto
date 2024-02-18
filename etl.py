import pandas as pd
from datetime import datetime 
from sqlalchemy import create_engine
import psycopg2
import requests
from Util import get_database_conn


def extract_data():
    urls = [
        "https://www.football-data.co.uk/mmz4281/1920/E0.csv",
        "https://www.football-data.co.uk/mmz4281/0203/E1.csv",
        "https://www.football-data.co.uk/mmz4281/1920/E2.csv",
    ]

    dataframes = []

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  
            if response.status_code == 200:
                filename = url.split("/")[-1]

                with open(filename, 'wb') as file:
                    file.write(response.content)

                print(f"Downloaded and saved {filename}")

                try:
                    df = pd.read_csv(filename)
                    dataframes.append(df)
                    print(f"Read {filename} successfully.")
                except pd.errors.ParserError as e:
                    print(f"Error reading {filename}: {e}")
                except FileNotFoundError:
                    print(f"File {filename} not found.")
                except Exception as e:
                    print(f"An unexpected error occurred while reading {filename}: {e}")
            else:
                print(f"Failed to download {url}")
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error for {url}: {e}")

    result = pd.concat(dataframes)
    result.to_csv('combined.csv', index=False)
    print ('Data Extraction Successful')

extract_data()


def transform_data():
    data = pd.read_csv('combined.csv')
    date_format = "%d/%m/%Y"  
    time_format = "%H:%M" 
    data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], format=f"{date_format} {time_format}")
    data = data.drop(['Date', 'Time'], axis=1)
    column_to_move = data.pop('Datetime')
    position = 1
    data.insert(position, 'Datetime', column_to_move)
    data = data.rename(columns={'HomeTeam':'Home', 'AwayTeam':'Away'})
    data = data.drop(['MaxC<2.5','AvgC>2.5','AvgC<2.5','AHCh','B365CAHH','B365CAHA','PCAHH','PCAHA','MaxCAHH','MaxCAHA','AvgCAHH','AvgCAHA'], axis=1 )
    data.fillna(value=0, inplace=True)
    data.to_csv ('tt/transformed_data.csv', index=False)
    print ('Tranformation Successful')

transform_data()

def load_data():
    data = pd.read_csv('tt/transformed_data.csv')
    engine = get_database_conn()
    data.to_sql('betting_data', con=engine, if_exists = 'append', index = False)
    print ('Data Successfully Written To PostgresSQL Database')

load_data()


