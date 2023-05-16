import requests
import json


url = "http://cbms4prdapp.chitalebandhu.net.in:8000/sap/opu/odata/sap/ZCBM_OD_SD_CSCMFOODERP_SRV/OrderHeaderSet"

payload = json.dumps({
  "Customer": "500581",
  "DocDate": "04.05.2023",
  "Indicator": "F",
  "OrderNo": "127407",
  "Stats": "1",
  "OrderItemSet": [
    {
      "OrderNo": "127407",
      "ItemNo": "3706465",
      "Material": "1200249",
      "Quantity": "10.000",
      "Unit": "KG",
      "Plant": "IW03",
      "Batch": ""
    }
  ],
  "CancelFlag": " "
})
headers = {
  'X-Requested-With': 'x',
  'Authorization': 'Basic SW50ZXJmYWNlOkFkbWluQDEyMzQ=',
  'Content-Type': 'application/json',
  'Cookie': 'SAP_SESSIONID_CSP_900=zUHoJ83NYxxPWHzOoQ8TsJOcV2HvGxHtptICAEHiAA8%3d; sap-usercontext=sap-client=900'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
# print(response.json())


