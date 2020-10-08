<h3> <a href="https://tkravits.github.io/Building-Permit-Automation">Building Permit Data Clean Up and Automation</a></h3>

This code allows the user to select an excel sheet from which to import given permit information. Many municipalities in Boulder County either hand enter or have extraneous data which leads to errors. The script then makes the necessary changes to the data and reformats the information.

This is a portion of the original dataset:

|PermitNum |	MasterPermitNum	|Description |	AppliedDate |	IssuedDate |	CompletedDate	| StatusCurrent	| OriginalAddress	|OriginalCity	|OriginalState	|OriginalZip	|PIN	|ProjectName	|PermitType|	PermitWorkType	|EstProjectCost |
| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- |
|RFG2020-00745	| |	*Total tear-off & reroof of SFD, 34 squares of dimensional shingles|	9/28/2020|	9/30/2020	||	Issued|	1558 CRESS CT|BOULDER|CO|80304|1.46319E+11||		Roofing Replacement Permit	|Roofing Replacement Permit	|9000|
|RFG2020-00746	||	*Total tear-off & reroof of SFD, 23 squares of dimensional shingles	|9/28/2020	|9/29/2020||		Issued	|1775 FOREST AVE	|BOULDER	|CO|	80304|	1.46319E+11	||	Roofing Replacement Permit	|Roofing Replacement Permit|	10270|

The biggest accomplishments of this code is classifying the type of permit (SCOPE) into a preset code (ex: Roofing permits are classified as RRR), attaching the correct tax ID (strap) using the address and if the address is not found in our system, using the parcel number.

The result it three output files: an text and excel sheet with the permits are issued for the appraisers to use to review permits:

|Permit Number|	Parent Permit Number|	strap|	Description|	StreetNo_txt|	StreetDir|	StreetName|	StreetType|	Unit|	Value Total|	Issued Date|	Finaled Date|	Work Class|	SCOPE|	map_id|	nh_cd|	dor_cd|
| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- |--- |
|RFG2020-00745| |		R0111113	|Total tear-off & reroof of SFD, 34 squares of dimensional shingles |	1558	|| 	CRESS	|CT	||	9000	|2020-09-30 00:00:00|	|	Roofing Replacement Permit	|RRR	|	|120|	RES|
|RFG2020-00746	||	R0007293	|Total tear-off & reroof of SFD, 23 squares of dimensional shingles| 	1775	|| 	FOREST|	AVE||		10270|	2020-09-29 00:00:00	|	|Roofing Replacement Permit|	RRR	|	|115	|RES|

The code is found <a href="https://github.com/tkravits/Building-Permit-Automation">here</a>
