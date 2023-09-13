import requests
import json
import pandas as pd
from tqdm import tqdm


def save_dapil(return_file = True):
    resp = requests.get(url = "https://infopemilu.kpu.go.id/Pemilu/Dcs_dpr/GetDapilOptions_dprri")
    
    tmp_data = pd.DataFrame(resp.json()["data"])

    dapil_data = tmp_data
    
    dapil_data.to_csv("dapil_data.csv", index = False)

    if return_file:
        return dapil_data
    
def scrape_data():
    dapil_data = pd.read_csv("dapil_data.csv")

    for kode, nama in tqdm(dapil_data.to_numpy()):
        resp = requests.get(url = f"https://infopemilu.kpu.go.id/Pemilu/Dcs_dpr/Dcs_dpr?kode_dapil={kode}")

        with open(f"json_data/{kode}-{nama}.json", 'w', encoding = 'utf-8') as f:
            json.dump(resp.json(), f, indent = 4)

MAPPING_COLUMNS = {
    0: "Partai",
    1: "Dapil",
    2: "Nomor Urut",
    3: "Foto",
    4: "Nama Lengkap",
    5: "Jenis Kelamin",
    6: "Kota"
}

def clean_nama_partai(data_partai):
    data_partai = data_partai.split(" > ")
    
    return data_partai[-1]

def clean_dapil(data_dapil):
    data_dapil = data_dapil.split("<br>")
    data_dapil = data_dapil[-1].split("</center>")
    
    return data_dapil[0]

def clean_nomor_urut(data_nomor_urut):
    data_nomor_urut = data_nomor_urut.split('<font size=\"3\">')
    data_nomor_urut = data_nomor_urut[-1].split("</font>")

    return data_nomor_urut[0]

def clean_foto(data_foto):
    data_foto = data_foto.split('" width=')

    return data_foto[0]

def convert_json_to_dataframe(filename):
    raw_data = pd.read_json(filename)

    data = pd.DataFrame(raw_data["data"].tolist(), index = raw_data.index)
    
    data = data.drop(columns=[7], axis = 1)

    data = data.rename(columns = MAPPING_COLUMNS)

    data["Partai"] = data["Partai"].apply(clean_nama_partai)

    data["Dapil"] = data["Dapil"].apply(clean_dapil)

    data["Nomor Urut"] = data["Nomor Urut"].apply(clean_nomor_urut)

    data["Foto"] = data["Foto"].str.extract(r'(https.*)(?:>)')

    data["Foto"] = data["Foto"].apply(clean_foto)

    return data

def convert_all():
    dapil_data = pd.read_csv("dapil_data.csv")

    for kode, nama in tqdm(dapil_data.to_numpy()):
        # read data
        filename = f"json_data/{kode}-{nama}.json"
        
        data = convert_json_to_dataframe(filename)

        data.to_csv(f"csv_data/{kode}-{nama}.csv", index = False)    

convert_all()