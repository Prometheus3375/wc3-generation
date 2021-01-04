import gspread

gc = gspread.service_account(filename='sandbox/wisptd-reader.json')
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1LfpGAp6Z0qlFUxjVStFu5Z_0_Dj_U5Wck339fdPyUKk')
