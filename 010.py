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
            subquery = text[start:end]  # full ( ... )
            after = text[end:].lstrip()

            # Check if alias is already present
            alias_match = re.match(r'(?i)(as\s+\w+|\w+)', after)
            reserved_keywords = ['WHERE', 'JOIN', 'ON', 'GROUP', 'ORDER', 'UNION', 'EXCEPT', 'INTERSECT']
            alias_already = False
            if alias_match:
                word = alias_match.group(0).strip().upper()
                if word not in reserved_keywords:
                    alias_already = True

            if alias_already:
                pos = end
                continue

            # Recursively process inside subquery
            inner_only = subquery[1:-1]  # remove the outer ()
            updated_inner = process_block(inner_only)
            updated_subquery = f"({updated_inner})"

            alias = f" AS AutoAlias_NW{alias_counter} "
            alias_counter += 1

            text = text[:start] + updated_subquery + alias + text[end:]
            pos = start + len(updated_subquery) + len(alias)

        return text

    return process_block(sql)

# Provided SQL with subqueries missing aliases (especially inside UNION in JOIN)
sql = """
SELECT 
EFF_DATE as EFF_DATE,
H_POLICY_SEQ_NUM as H_POLICY_SEQ_NUM

FROM 
(
select 
    H_POLICY_SEQ_NUM,
    COVERAGE_CD,
    EFF_DATE,
    RANK() OVER ( PARTITION BY H_POLICY_SEQ_NUM ORDER BY COVERAGE_CD ) COVERAGE_RANK
FROM (

    SELECT
        COV_LOW.EFF_DATE as EFF_DATE,
        POL_COV.H_POLICY_SEQ_NUM AS H_POLICY_SEQ_NUM,
        COV.COVERAGE_CD AS COVERAGE_CD
        

    FROM     LIFEODS.L_POLICY_COVERAGE POL_COV
    --ON POL.H_POLICY_SEQ_NUM = POL_COV.H_POLICY_SEQ_NUM

    INNER JOIN (
    select * from (
                select * from table
                )
                
                union
                
                select * from (
                    select * from table
                ) 
                where 1=1
    ) as b
    ON COV.H_COVERAGE_SEQ_NUM = POL_COV.H_COVERAGE_SEQ_NUM
    AND COV.END_TS > SYSDATE 
    AND COV.COVERAGE_CD  in ('ASI', 'PCRB')

    INNER JOIN LIFEODS.S_COVERAGE_LIFE_LOW COV_LOW
    ON POL_COV.L_POLICY_COVERAGE_SEQ_NUM = COV_LOW.L_POLICY_COVERAGE_SEQ_NUM
    AND COV_LOW.END_TS > SYSDATE 
    -- AND NVL(COV_LOW.TERM_DATE, SYSDATE) > TO_date ('$$CYCLEDATEJHIM', 'MM/DD/YYYY HH24:MI:SS:FF6')

    INNER JOIN LIFEODS.S_COVERAGE_LIFE_MED COV_MED
    ON POL_COV.L_POLICY_COVERAGE_SEQ_NUM = COV_MED.L_POLICY_COVERAGE_SEQ_NUM
    AND COV_MED.END_TS > SYSDATE 

    INNER JOIN LIFEODS.S_COVERAGE_LIFE_HI hi 
    ON POL_COV.L_POLICY_COVERAGE_SEQ_NUM = hi.L_POLICY_COVERAGE_SEQ_NUM 
and f in (1,2,3)
    WHERE 
     POL_COV.LOAD_SRC  in (  'WA' )
     AND 
    POL_COV.END_TS > SYSDATE 
    
    )
    
)    

WHERE COVERAGE_RANK = 1
"""

# Apply alias insertion
result = add_aliases_recursively(sql)
result[:3000]  # only return relevant portion for display