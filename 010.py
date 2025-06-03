with abc as
(
select * from (
	            select * from table
	            )
	            
	            union
	            
	            select * from (
	                select * from table
	            ) 
	            where 1=1
)
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
		

	FROM 	LIFEODS.L_POLICY_COVERAGE POL_COV
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
