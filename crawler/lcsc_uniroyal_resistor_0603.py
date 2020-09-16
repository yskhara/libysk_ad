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


def main():
    global crsr
    """ エントリポイントだよ。

    """
    logger.debug("mainの開始")

    data = None
    
    #test_pattern()

    #setup()
    #data = post()

    path = "sample_response.json"
    with open(path) as f:
        json_str = f.read()
        data = json.loads(json_str)
    
    #print(json.dumps(data["result"]["data"][0], sort_keys=True, indent=4))

    #print(data["result"]["data"][0])
    #quit()

    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        r'DBQ=..\passive_resistor.mdb;'
        )
    conn = pyodbc.connect(conn_str)
    crsr = conn.cursor()
    #for table_info in crsr.tables(tableType='TABLE'):
    #    print(table_info.table_name)

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
    part_number = entry["info"]["number"]
    comment = "=Resistance"
    description = entry["description"]
    manufacturer = entry["manufacturer"]["en"]
    manufacturer_part_number = "=Part Number"
    supplier = "LCSC"
    supplier_part_number = entry["number"]
    attributes = entry["attributes"]
    resistance = attributes["Resistance"]
    tolerance = attributes["Tolerance"]
    temp_coeff = attributes["Temperature Coefficient"]
    pow_rating = attributes["Power(Watts)"]
    volt_rating = "75V"
    case_pkg = "0603"
    lib_ref = "Resistor"
    lib_path = "symbols/passive/passive_resistor.SchLib"
    fot_ref = "R0603"
    fot_path = "footprints/passive/passive_resistor.PcbLib"
    component_type = "Standard"
    link1url = entry["datasheet"]["pdf"]
    link1desc = "Datasheet"
    link2url = "https://lcsc.com" + entry["url"]
    link2desc = "Supplier Product Page"

    sql_add_entry = ("insert into " + table_name + "("
        "`Part Number`, `Comment`, `Description`, `Manufacturer 1`, `Manufacturer Part Number 1`, "
        "`Supplier 1`, `Supplier Part Number 1`, `Resistance`, `Tolerance`, `Temperature Coefficient`, "
        "`Power Rating`, `Voltage Rating`, `Case/Package`, `Library Ref`, `Library Path`, `Footprint Ref`, "
        "`Footprint Path`, `Component Type`, `ComponentLink1URL`, `ComponentLink1Description`, `ComponentLink2URL`, `ComponentLink2Description`"
        ") values ("
        "'" + "', '".join([part_number, comment, description, manufacturer, manufacturer_part_number, supplier, supplier_part_number, 
        resistance, tolerance, temp_coeff, pow_rating, volt_rating, case_pkg, lib_ref, lib_path, fot_ref, fot_path,
        component_type, link1url, link1desc, link2url, link2desc]) 
        + "');"
        )
        

    print("executing sql query: \r\n    " + sql_add_entry)

    try:
        crsr.execute(sql_add_entry)
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
