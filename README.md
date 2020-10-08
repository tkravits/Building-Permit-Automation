<h3> <a href="https://tkravits.github.io/Building-Permit-Automation">Building Permit Data Clean Up and Automation</a></h3>

This code allows the user to select an excel sheet from which to import given permit information. Many municipalities in Boulder County either hand enter or have extraneous data which leads to errors. The script then makes the necessary changes to the data and reformats the information.

This is a portion of the original dataset:

|PermitNum |	MasterPermitNum	|Description |	AppliedDate |	IssuedDate |	CompletedDate	| StatusCurrent	| OriginalAddress	|OriginalCity	|OriginalState	|OriginalZip	|PIN	|ProjectName	|PermitType|	PermitWorkType	|EstProjectCost |
| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- |
|BLD-NRE2020-00152|  |	"*UNIT 200: ALL INTERIOR WORK |	06/20/20| 07/01/20| |Pending at Applicant |	4845 PEARL EAST CIR|BOULDER|CO|80301|1.46328E+11|	| Building Permit - Non-Residential	|Remodel|85533|
|BLD-SFD2020-00435|	 |	*Remove old deck (75sq ft), and install a new deck (273 sq ft).	|10/5/2020|	| |Pending at Applicant	|1929 HARDSCRABBLE DR|BOULDER|CO|80305|1.57717E+11|	| Building Permit - Single Family Detached Dwelling	|Addition|4781.7|

|PermitNum |	MasterPermitNum	|Description |	AppliedDate |	IssuedDate |	CompletedDate	| StatusCurrent	| OriginalAddress	|OriginalCity	|OriginalState	|OriginalZip	|PIN	|ProjectName	|PermitType|	PermitWorkType	|EstProjectCost |
| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- |
|RFG2020-00745	| |	*Total tear-off & reroof of SFD, 34 squares of dimensional shingles|	9/28/2020|	9/30/2020	||	Issued|	1558 CRESS CT|BOULDER|CO|80304|1.46319E+11||		Roofing Replacement Permit	|Roofing Replacement Permit	|9000|
|RFG2020-00746	||	*Total tear-off & reroof of SFD, 23 squares of dimensional shingles	|9/28/2020	|9/29/2020||		Issued	|1775 FOREST AVE	|BOULDER	|CO|	80304|	1.46319E+11	||	Roofing Replacement Permit	|Roofing Replacement Permit|	10270|


The result it three output files: an excel sheet with the permits are being reviewed:
|Permit Number|	Parent Permit Number|	strap|	Description|	StreetNo_txt|	StreetDir|	StreetName|	StreetType|	Unit|	Value Total|	Issued Date|	Finaled Date|	Work Class|	SCOPE|	map_id|	nh_cd|	dor_cd|
| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- |
|RFG2020-00745|		R0111113	|Total tear-off & reroof of SFD, 34 squares of dimensional shingles |	1558	| 	CRESS	|CT	|	9000	|2020-09-30 00:00:00|		Roofing Replacement Permit	|RRR	|	120	|RES|
|RFG2020-00746	|	R0007293	|Total tear-off & reroof of SFD, 23 squares of dimensional shingles| 	1775	| 	FOREST|	AVE|		10270|	2020-09-29 00:00:00	|	Roofing Replacement Permit|	RRR	|	115	|RES|


a text file in the correct format to be pulled into a CAMA database, and an excel sheet summarizing the information for the appraisers.

The code is found <a href="https://github.com/tkravits/Building-Permit-Automation">here</a>
