import regex as re

def add_aliases_recursively(sql: str) -> str:
    alias_counter = 1

    def process_block(text):
        nonlocal alias_counter

        pattern = re.compile(r'\b(from|join)\s*\(\s*', re.IGNORECASE)
        pos = 0
        while True:
            match = pattern.search(text, pos)
            if not match:
                break

            keyword = match.group(1).upper()
            start = match.end() - 1  # position of '('

            # Match balanced parentheses
            stack = ['(']
            i = start + 1
            while i < len(text) and stack:
                if text[i] == '(':
                    stack.append('(')
                elif text[i] == ')':
                    stack.pop()
                i += 1

            if stack:
                pos = match.end()
                continue

            end = i
            subquery = text[start:end]  # from first `(` to its closing `)`
            after = text[end:].lstrip()

            # Check if alias is already present
            alias_match = re.match(r'(?i)(as\s+\w+|\w+)', after)
            reserved_keywords = ['WHERE', 'JOIN', 'ON', 'GROUP', 'ORDER', 'UNION', 'EXCEPT', 'INTERSECT']
            alias_already = False
            if alias_match:
                word = alias_match.group(0).strip().upper()
                if word not in reserved_keywords:
                    alias_already = True

            # Skip aliasing only if JOIN is used
            if keyword == "JOIN" or alias_already:
                pos = end
                continue

            # Recursively process inside subquery
            updated_subquery = process_block(subquery)

            alias = f" AS AutoAlias_NW{alias_counter} "
            alias_counter += 1

            # Replace original subquery with aliased and updated version
            text = text[:start] + updated_subquery + ")" + alias + text[end:]
            pos = start + len(updated_subquery) + len(alias) + 1

        return text

    return process_block(sql)