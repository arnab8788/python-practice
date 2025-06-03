import regex as re

def add_missing_aliases_to_subqueries(sql: str) -> str:
    alias_counter = 1

    def add_alias_to_subquery(match):
        nonlocal alias_counter
        full_match = match.group(0)
        inner_sql = match.group(1)

        # Check for alias after closing parenthesis
        after = match.group(2)
        if re.search(r'\b(as\s+\w+|\b\w+)\b', after.strip(), re.IGNORECASE):
            return full_match  # Alias already present

        # Do not alias if preceded by JOIN
        before = sql[:match.start()]
        if re.search(r'\bjoin\s*$', before.strip().split('\n')[-1], re.IGNORECASE):
            return full_match

        return f"{full_match}) AS AutoAlias_NW{alias_counter}{after}" if after.strip() else f"{full_match}) AS AutoAlias_NW{alias_counter}"

    def process_subqueries(s):
        nonlocal alias_counter
        pattern = re.compile(
            r"""
            (
                \(\s*                             # Opening parenthesis of subquery
                (?:SELECT\b.*?(?:(?R)|[^()])*?)   # A SELECT statement (non-greedy, recursive for nested)
            )
            \)                                   # Closing parenthesis of subquery
            (\s*(?!\b(as|\w+\s+join|join)\b)[^;)]*)  # What comes after - should not already be an alias or JOIN
            """,
            re.IGNORECASE | re.VERBOSE | re.DOTALL,
        )

        prev_s = None
        while prev_s != s:
            prev_s = s
            s = pattern.sub(lambda m: add_alias_to_subquery(m), s)
            alias_counter += 1
        return s

    return process_subqueries(sql)