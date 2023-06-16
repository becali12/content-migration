import gspread

sa = gspread.service_account(filename="zendesk-kb-articles-2d35c5b1fd3c.json")
sh = sa.open("Docusaurus")
wks = sh.worksheet("Articles structure")

def store_to_sheet(row: list):
    wks.append_row(row)

def get_first_col():
    return wks.col_values(1)

def get_all_sheet_values():
    return wks.get_all_values()