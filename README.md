# DecisionMaker
A decision-making algorithm for the Exodus League, a BBGM NBA simulation league.

Currently, this algorithm is on version 5.0.0.

To run the program, download all the files in a folder then run
"decisionmaker.py", the main file for the algorithm.

Credit to tus for creating and refining the importance-defining algorithms and the
Gaussian distribution fit. Couldn't have done it without you!

This is an open-source repository licensed under the GNU GPLv3 License. The License
is included in the repository.

### Now Fully Automated
DecisionMaker can now pull data **directly from an export**, process your offers,
and then input your offers directly back into the export. To use this functionality,
place the export you want to modify in the root directory and name it `export.json`
and the offer csv in the root directly as `offers.csv`. Then, run the program and
choose option 2 at the first prompt.

The offer sheet CSV must have a certain style — the first row should contain headers.
The columns should be Team Name, Player Being Offered, Offer Amount, Offer Years, Role, Exception, Option,
in that order. Note: for Option, the choices should be exactly "TO", "PO", and "None".

If you want to see what outputs/decisions the program has made, check out `generated.csv` for the
generated input csv, `list.txt` for all decisions in plain text, and `decisionMatrix.csv` for
decisions in a CSV format (compatible with Ainge-BBGM).

### How to Use the Spreadsheet Functions of DecisionMaker:
When running Free Agency, there may be a multitude of offers you need to run through the algorithm.

To help with these situations, DecisionMaker can receive a CSV file that contains all FA data and
will automatically run through each decision and spit them out.

The proper format for the CSV is as follows:

The first line of the CSV contains the headers: Name/Team, Age/Offer, OVR/Power Ranking, Asking Amount/Team Payroll,
isRFA (0 or 1)/Player Role, # of Contracts/Use MLE (0 or 1).

The next line holds the player information (name, age, OVR, askingAmount, isRFA, and # of contracts).

The next few lines holds all the contracts that player has received (the team, offer, power ranking, payroll, player role,
whether the offer uses MLE or not, and facilities rank.)

Once you write out each offer in each line, move onto to the next player, and their contracts, and so on and so forth.

Making a spreadsheet as FA goes will drastically reduce the time required for input.

Remember to also place the final .csv in the same directory as 'decisionmaker.py'.
