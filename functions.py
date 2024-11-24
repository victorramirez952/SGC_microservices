

def format_date_columns(rows, date_column_names):
    if not rows:
        return []

    formatted_rows = []

    for row in rows:
        formatted_row = dict(row)
        for column_name in date_column_names:
            if column_name in formatted_row:
                value = formatted_row[column_name]
                # if isinstance(value, datetime):
                formatted_row[column_name] = value.strftime('%Y-%m-%d')
                # else:
                #     try:
                #         print("Formato")
                #         formatted_row[column_name] = datetime.strptime(value, "%m/%d/%y").strftime("%Y-%m-%d")
                #     except ValueError:
                #         formatted_row[column_name] = value
        formatted_rows.append(formatted_row)

    return formatted_rows

import pandas as pd

def uppercase_keys(data):
    return {key.upper(): value for key, value in data.items()}
