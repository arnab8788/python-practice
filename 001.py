def regex_func_convert_to_date(sql: str) -> str:
    try:
        format_map = {
            'YYYY-MM-DD': 120,
            'YYYY-MM-DD HH24:MI:SS': 120,
            'YYYY/MM/DD': 111,
            'YYYY/MM/DD HH24:MI:SS': 111,
            'MM/DD/YYYY': 101,
            'MM/DD/YYYY HH24:MI:SS': 101,
            'DD/MM/YYYY': 103,
            'DD/MM/YYYY HH24:MI:SS': 103,
            'DD-MM-YYYY': 105,
            'DD-MM-YYYY HH24:MI:SS': 105,
            'YYYY.MM.DD': 102,
            'YYYY.MM.DD HH24:MI:SS': 102
        }

        pattern = r'\bTO_DATE\s*\(\s*((?:[^()]+|(?R))*?)\s*\)'

        # Function to convert TO_DATE's content to SQL Server syntax
        def convert_to_sqlserverformat(to_date_match):

            args_str = to_date_match.group(1)

            # Split top-level commas only
            parts = [p.strip() for p in re.split(r',(?![^(]*\))', args_str)]

            expr = parts[0]
            if len(parts) > 1:
                dateformat = str(parts[1]).replace("  ", " ").replace("'", "")
                formattoken = format_map.get(dateformat.upper(), None)

                if formattoken is not None:
                    return f"CONVERT(DATETIME, {expr}, {formattoken})"

            # Fallback if something goes wrong
            return f"CAST({expr} AS DATETIME)"

        # Perform replacement in-place while preserving query formatting
        converted_sql = re.sub(pattern, convert_to_sqlserverformat, sql, flags=re.IGNORECASE | re.DOTALL)
        return converted_sql

    except Exception as e:
        print(f"Error in 'regex_func_convert_to_date': \t{e}")
        exit(-1)


def regex_func_convert_to_char(sql: str) -> str:
    try:
        format_map = {
            'YYYY-MM-DD': 'yyyy-MM-dd',
            'DD-MM-YYYY': 'dd-MM-yyyy',
            'MM/DD/YYYY': 'MM/dd/yyyy',
            'YYYY/MM/DD': 'yyyy/MM/dd',
            'DD/MM/YYYY': 'dd/MM/yyyy',
            'YYYY.MM.DD': 'yyyy.MM.dd',
            'HH24:MI:SS': 'HH:mm:ss',
            'YYYY-MM-DD HH24:MI:SS': 'yyyy-MM-dd HH:mm:ss',
            'MM/DD/YYYY HH24:MI:SS': 'MM/dd/yyyy HH:mm:ss',
            'YYYYMMDD': 'yyyyMMdd'
        }

        system_date_map = {
            'SYSDATE': 'SYSDATETIME()'
            , 'CURRENT_DATE': 'SYSDATETIME()'
            , 'CURRENT_TIMESTAMP': 'SYSDATETIME()'
            , 'NOW()': 'SYSDATETIME()'
            , 'NOW': 'SYSDATETIME()'
        }

        pattern = r"\b(TO_CHAR|VARCHAR_FORMAT)\s*\(\s*(.+?)\s*(?:,\s*'([^']+)')?\s*\)"

        def replacer(match):
            raw_expression = match.group(2).strip()
            format_str = match.group(3)

            expression = system_date_map.get(raw_expression.upper(), raw_expression)
            if format_str:
                normalized_format = format_str.upper().replace("  ", " ").strip()
                sql_format = format_map.get(normalized_format, format_str)
                # sql_format = format_map[format_str.strip()]
                return f"FORMAT({expression}, '{sql_format}')"
            else:
                return f"CAST({expression} AS VARCHAR)"

        return re.sub(pattern, replacer, sql, flags=re.IGNORECASE)

    except Exception as e:
        print(f"Error in 'regex_func_convert_to_char': \t{e}")
        exit(-1)

