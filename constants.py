CUSTOMER_NAME = "שם לקוח"
CUSTOMER_ID = "מס' לקוח"
PRODUCT_ID = "מק'ט"
PRODUCT_NAME = "תאור מוצר"
FAMILY_NAME = 'תאור משפחה'
MANUFACTURER = 'מספר יצרן'
SALES_ALL_MONTHS = 'סה"כ מכירות בשנה האחרונה'
SALES_6_MONTHS = 'סה"כ מכירות בחצי השנה האחרונה'
CURRENT_MONTH_SALES = 'נמכר בחודש נוכחי'
SALES_1_MONTH_BEFORE = 'נמכר בחודש הקודם'
SALES_2_MONTH_BEFORE = 'נמכר לפני חודשיים'
SALES_3_MONTH_BEFORE = 'נמכר לפני 3 חודשים'
TOTAL_SALES_1_YEARS = 'סה"כ מכירות בשנה האחרונה'
SUM = "סכום (שח)"
TOTAL_REVENUE = "רווח (שח)"
AGENT_NAME = 'שם סוכן'
ORDERS_REMAINING = 'יתרה לאספקה'
MONTH = 'month'
YEAR = 'year'
DATE = "תאריך"
ORDER_DATE = "תאריך ההזמנה"
QUANTITY = "כמות"
INVENTORY_QUANTITY = "כמות במלאי"
INVENTORY = 'מלאי זמין'
PROCUREMENT_ORDERS = 'הזמנות רכש פתוחות'

EXTENDED_VIEW = 'צפיה מורחבת'
ORDER_QUANTITY = 'כמות בהזמנה'
GENERAL_BUYS = 'כמות קניות'
GENERAL_SALES = 'מכירות כללי'
EXAMINED_SALES = 'מכירות מבחן'
OPENING_QUANTITY = 'כמות פתיחה'

ORDERS_LEFT_TO_SUPPLY = 'הזמנות לקוח שלא סופקו ב3 חודשים אחרונים'
DAMAGED_INVENTORY = 'מחסן פגומים'
MAIN_INVENTORY = 'מחסן ראשי'
PARTRIDE_INVENTORY = 'מחסן פארטסרייד פאי'
INQIRIES_INVENTORY = 'מחסן בירורים'
HAKOL_PO_INVENTORY = 'הכל פה'  # we remove disal ta warehouse, as it is not being presented in the original inventory column
ON_THE_WAY = 'עומד לבוא'
ON_THE_WAY_STATUS = 'סטטוס שורת הזמנת רכש'
ORDER_STATUS = 'סטטוס הזמנה'
STATUS = 'סטטוס'
LAST_PRICE = 'מחיר אחרון'
ALL = 'all'
YEAR_MONTH = 'year_month'
QUANTITY_PROCUREMENT = 'כמות הזמנות מהספק'
SUM_PROCUREMENT = 'תשלום לספק'
DROP_DOWN_STYLE = {
    'backgroundColor': '#333',
    # 'color': 'white',
    # 'border': '1px solid #555',
    # 'borderRadius': '4px'
}


MOVEMENT_TYPE = 'תאור סוג תנועת מלאי'
RETURN_TO_SUPPLIER = 'החזרת סחורה לספק'
RETURN_FROM_CLIENT = 'החזרה מלקוח'
WAREHOUSE_TRANSFER = 'העברה בין מחסנים'
INVENTORY_COUNT = 'ספירות מלאי'
RECEIVE_FROM_SUPPLIER = 'קבלות סחורה מספק'
FROM_WAREHOUSE = 'ממחסן'
TO_WAREHOUSE = 'למחסן'
MOVEMENTS_COUNT = 'כמות (קניה/מכירה)'
MAIN_WAREHOUSE = 'Main'


PROCUREMENT_ID = 'חשבונית'
STYLE_DATA = {"backgroundColor": "rgb(50, 50, 50)", "color": "white"}
STYLE_TABLE = {"overflowX": "auto", "maxWidth": "100%", "tableLayout": "fixed"}

STYLE_CELL = {
    "overflow": "hidden",
    "textOverflow": "ellipsis",
    "maxWidth": "0",
    'textAlign': 'right',  # Align text to the right
    'direction': 'rtl',  # Keep RTL direction for text
}

STYLE_HEADER = {
    "backgroundColor": "rgb(30, 30, 30)",
    "color": "white",
    'direction': 'rtl',
    "width": "auto",
}

SUPPLIERS = {'GSP': 'GSP',
             'LPR': 'LPR',
             'LONGKOU': 'LONGKOU',
             'DOLZ': 'DOLZ',
             'MATEC': 'MATEC',
             'BAW': 'BAW',
             'OSCAR': 'KOR'}

PRODUCTS_DATA_COLUMNS = [PRODUCT_ID, PRODUCT_NAME, FAMILY_NAME, OPENING_QUANTITY, GENERAL_BUYS, GENERAL_SALES, EXAMINED_SALES,
                   INVENTORY,
                   LAST_PRICE,
                   ORDER_QUANTITY, RECEIVE_FROM_SUPPLIER, INVENTORY_COUNT, WAREHOUSE_TRANSFER, RETURN_FROM_CLIENT,
                   RETURN_TO_SUPPLIER, 'בדיקת תקינות'][::-1]

HIDDEN_COLUMNS = [RECEIVE_FROM_SUPPLIER, INVENTORY_COUNT, WAREHOUSE_TRANSFER, RETURN_FROM_CLIENT,
                   RETURN_TO_SUPPLIER, 'בדיקת תקינות']