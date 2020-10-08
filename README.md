<h3> <a href="https://tkravits.github.io/Building-Permit-Automation">Building Permit Data Clean Up and Automation</a></h3>

This code allows the user to select an excel sheet from which to import given permit information. Many municipalities in Boulder County either hand enter or have extraneous data which leads to errors. The script then makes the necessary changes to the data and reformats the information.

This is an example of the dataset

| Command | Description |
| --- | --- |
| git status | List all new or modified files |
| git diff | Show file differences that haven't been staged |

|PermitNum |	MasterPermitNum	|Description |	AppliedDate |	IssuedDate |	CompletedDate	| StatusCurrent	| OriginalAddress	|OriginalCity	|OriginalState	|OriginalZip	|PIN	|ProjectName	|PermitType|	PermitWorkType	|EstProjectCost |
| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- | --- | ---| --- |
|BLD-NRE2020-00152	| - |	"*UNIT 200: ALL INTERIOR WORK - NO ALTERATIONS TO EXISTING BUILDING ENVELOPE MINOR REMODEL WORK & MINOR ELECTRICAL WORK TO EXISTING CU SUITE CHANGE ORIENTATION OF AN EXISTING CLOSET |	|06/20/20| |07/01/20| | | |Pending at Applicant |	4845 PEARL EAST CIR|	BOULDER|	CO|	80301|	1.46328E+11	|	Building Permit - Non-Residential	Remodel|	85533|

|BLD-SFD2020-00435|		*Remove old deck (75sq ft), and install a new deck (273 sq ft).	10/5/2020	|		Pending at Applicant	|1929 HARDSCRABBLE DR	|BOULDER	|CO	|80305|	1.57717E+11	|	Building Permit - Single Family Detached Dwelling	Addition	|4781.7|


The result it three output files: an excel sheet with the permits are being reviewed, a text file in the correct format to be pulled into a CAMA database, and an excel sheet summarizing the information for the appraisers.

The code is found <a href="https://github.com/tkravits/Building-Permit-Automation">here</a>
