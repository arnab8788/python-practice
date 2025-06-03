import regex as re

def add_missing_aliases_to_subqueries(sql: str) -> str:
    alias_counter = 1
    output = sql
    i = 0

    while i < len(output):
        # Match FROM or JOIN followed by optional whitespace and then a '('
        match = re.search(r'\b(from|join)\s*\(\s*', output[i:], re.IGNORECASE)
        if not match:
            break

        keyword = match.group(1).upper()
        match_start = i + match.start()
        paren_start = output.find('(', match_start)

        # Use stack to find the matching closing parenthesis
        stack = ['(']
        j = paren_start + 1
        while j < len(output) and stack:
            if output[j] == '(':
                stack.append('(')
            elif output[j] == ')':
                stack.pop()
            j += 1

        if stack:
            # Unbalanced parentheses
            i = match_start + 5
            continue

        closing_paren_pos = j - 1
        after_closing = output[closing_paren_pos + 1:]
        after_strip = after_closing.lstrip()

        # Check if an alias already exists
        alias_match = re.match(r'(?i)(AS\s+\w+|\w+)', after_strip)
        reserved_keywords = ['WHERE', 'JOIN', 'ON', 'GROUP', 'ORDER', 'UNION', 'EXCEPT', 'INTERSECT']
        if alias_match:
            word = alias_match.group(0).strip().upper()
            if word not in reserved_keywords:
                i = closing_paren_pos + 1
                continue

        # Only skip aliasing if the subquery is part of a JOIN
        if keyword == "JOIN":
            i = closing_paren_pos + 1
            continue

        # Otherwise, we must add alias
        alias = f" AS AutoAlias_NW{alias_counter} "
        output = output[:closing_paren_pos + 1] + alias + output[closing_paren_pos + 1:]
        alias_counter += 1
        i = closing_paren_pos + len(alias)

    return output