# -*- coding: utf-8 -*-

"""
    lcsc_uniroyal_resistor_0603.py
    LCSC.comからUNIROYALの0603な抵抗器の情報を取得してみるテスト
"""


from logging import getLogger, DEBUG
import requests
import re
import json
import pyodbc

# ログの設定
logger = getLogger(__name__)
logger.setLevel(DEBUG)

# 定数です
NUM_SPHERE = 4
NUM_TRYSAIL = 3

s = requests.Session()
table_name = "passive_resistor_smd"
crsr = None

key_part_number = "Part Number"

def main():
    global crsr
    """ エントリポイント

    """

    use_dummy_data = True

    data = None
    
    #test_pattern()

    if use_dummy_data:
        path = "sample_response.json"
        with open(path) as f:
            json_str = f.read()
            data = json.loads(json_str)
    else:
        setup()
        data = post()
    
    #print(json.dumps(data["result"]["data"][0], sort_keys=True, indent=4))

    #print(data["result"]["data"][0])
    #quit()

    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=..\passive_resistor.mdb;'
        )
    pyodbc.pooling = False
    conn = pyodbc.connect(conn_str)
    conn.autocommit = False
    crsr = conn.cursor()
    #for table_info in crsr.tables():#tableType='TABLE'):
    #    print(table_info.table_name)
    #    print(table_info.table_type)

    #sql_select_all = "select * from passive_resistor_smd"
    #rs = crsr.execute(sql_select_all)
    #cols = [d[0] for d in rs.description]
    #print(cols)
    #for row in crsr.fetchall():
    #    print(row)


    for entry in data["result"]["data"]:
        add_entry(entry)

    crsr.commit()

    crsr.close()
    conn.close()

def add_entry(entry):
    entry_dict = dict()

    entry_dict[key_part_number] = entry["info"]["number"]
    entry_dict["Comment"] = "=Resistance"
    entry_dict["Description"] = entry["description"]
    entry_dict["Manufacturer 1"] = entry["manufacturer"]["en"]
    entry_dict["Manufacturer Part Number 1"] = "=Part Number"
    entry_dict["Supplier 1"] = "LCSC"
    entry_dict["Supplier Part Number 1"] = entry["number"]
    attributes = entry["attributes"]
    entry_dict["Resistance"] = attributes["Resistance"]
    entry_dict["Tolerance"] = attributes["Tolerance"]
    entry_dict["Temperature Coefficient"] = attributes["Temperature Coefficient"]
    entry_dict["Power Rating"] = attributes["Power(Watts)"]
    entry_dict["Voltage Rating"] = "75V"
    entry_dict["Case/Package"] = "0603"
    entry_dict["Library Ref"] = "Resistor"
    entry_dict["Library Path"] = "symbols/passive/passive_resistor.SchLib"
    entry_dict["Footprint Ref"] = "R0603"
    entry_dict["Footprint Path"] = "footprints/passive/passive_resistor.PcbLib"
    entry_dict["Component Type"] = "Standard"
    entry_dict["ComponentLink1URL"] = entry["datasheet"]["pdf"]
    entry_dict["ComponentLink1Description"] = "Datasheet"
    entry_dict["ComponentLink2URL"] = "https://lcsc.com" + entry["url"]
    entry_dict["ComponentLink2Description"] = "Supplier Product Page"

    sql_query = "SELECT * FROM " + table_name + " WHERE `" + key_part_number + "` = '" + entry_dict[key_part_number] + "';"
    
    crsr.execute(sql_query)
    #crsr.commit()

    if(len(crsr.fetchall()) != 0):
        sql_query = ("UPDATE " + table_name + " SET " + 
        ", ".join(["`" + param + "` = '" + entry_dict[param] + "' " for param in entry_dict if param != key_part_number]) + 
        "WHERE `" + key_part_number + "` = '" + entry_dict[key_part_number] + "';"
        )
    else:
        sql_query = ("INSERT INTO " + table_name + " (`" + "`, `".join(entry_dict.keys()) + "`) "
        "VALUES ('" + "', '".join(entry_dict.values()) + "');"
        )
    

    print("executing sql query: \r\n" + sql_query)
    
    try:
        crsr.execute(sql_query)
        crsr.commit()
    except pyodbc.IntegrityError:
        pass

def test_pattern():
    # こんな感じの記述があるはず：
    #    <script type="text/javascript">
    #    $.ajaxSetup({ headers: { 'X-CSRF-TOKEN': 'r6Bk5hhzEuoBKi0cAzrAGvaHaW5V5g0dnCoxE7AA'}});
    #    </script>
    content = "    <script type=\"text/javascript\">"\
            "    $.ajaxSetup({ headers: { 'X-CSRF-TOKEN': 'r6Bk5hhzEuoBKi0cAzrAGvaHaW5V5g0dnCoxE7AA'}});"\
            "    </script>"
    pattern = r".+X-CSRF-TOKEN[\s|'|:]+(\w+).+"

    result1 = re.match(pattern, content)
    if result1:
        print('result1:', result1.group(1))
    else:
        print('result1:none')

def setup():
    
    #s.headers.update({'Cookie': '_ga=GA1.2.1471047320.1599628979; _gid=GA1.2.795103921.1599628979; _gat_UA-98399433-1=1; _fbp=fb.1.1599628979142.479377481; ONEAPM_BI_sessionid=1109.111|159962898434'})


    response = s.get('https://lcsc.com/products/Chip-Resistor-Surface-Mount_439.html')
    print("First GET request headers:")
    print(response.request.headers)
    print("\r\n")
    print("First GET response:")
    print(response.status_code)
    print(response.headers)
    print("\r\n")
    #print(response.text)
    # こんな感じの記述があるはず：
    #    <script type="text/javascript">
    #    $.ajaxSetup({ headers: { 'X-CSRF-TOKEN': 'r6Bk5hhzEuoBKi0cAzrAGvaHaW5V5g0dnCoxE7AA'}});
    #    </script>
    pattern = r".+X-CSRF-TOKEN[\s|'|:]+(\w+).+"

    csrf_token = re.match(pattern, response.text, re.S)
    if csrf_token:
        print('csrf_token detected:', csrf_token.group(1))
    else:
        print('csrf_token detection failed.')
        raise RuntimeError("csrf_token detection failed.")

    s.headers.update({
        "accept": "application/json, text/javascript, */*; q=0.01", 
        "accept-encoding": "gzip, deflate, br", 
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8", 
        "dnt": "1", 
        "isajax": "true", 
        "origin": "https://lcsc.com", 
        "referer":"https://lcsc.com/products/Chip-Resistor-Surface-Mount_439.html", 
        "sec-fetch-dest": "empty", 
        "sec-fetch-mode": "cors", 
        "sec-fetch-site": "same-origin", 
        "x-csrf-token": csrf_token.group(1),
        "x-requested-with": "XMLHttpRequest"
        })

def post():
    post_data = {"attributes[manufacturer][]": "UNI-ROYAL(Uniroyal Elec)","attributes[package][]": "0603","attributes[Tolerance][]":"±1%","current_page": "1","category": "439"}
    response = s.post('https://lcsc.com/api/products/search', data=post_data)#, headers=headers)

    print("First POST request headers:")
    print(response.request.headers)
    print("\r\nFirst POST response :")
    print(response.status_code)
    print(response.headers)
    print("\r\n")
    #print(response.text)


    result = json.loads(response.text)

    if result["success"] != True:
        raise RuntimeError("remote server reported a failure.")

    path = "sample_response.json"
    with open(path, mode="w") as f:
        f.write(response.text)

    #print(json.dumps(result, sort_keys=True, indent=4))

    return result

class MyClass:

    def __init__(self):
        """ コンストラクタの説明
        """
        self._pv_v = "インスタンス変数"

    def process(self, parm1):
        """ メソッドの説明
        """
        logger.debug("process")

    def _pv_process(self):
        logger.debug("_pv_process")


if __name__ == "__main__":
    main()
