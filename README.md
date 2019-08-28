# DecisionMakerSLR
A decision-making algorithm for NBASLR, a BBGM NBA simulation league.

Currently, this algorithm is on version 3.0.1.

To run the program, download all the files in a folder then run
"decisionmaker.py", the main file for the algorithm.

Credit to tus for creating and refining the importance-defining algorithms. Couldn't
have done it without you!

This is an open-source repository licensed under the MIT License. The License
is included in the repository.

### How to Use the Spreadsheet Functions of DecisionMakerSLR:
When running Free Agency, there may be a multitude of offers you need to run through the algorithm.

To help with these situations, DecisionMakerSLR can receive a CSV file that contains all FA data and
will automatically run through each decision and spit them out.

The proper format for the CSV is as follows: 

The first line of the CSV contains the headers: Name/Team, Age/Offer, OVR/Power Ranking, Asking Amount/Team Payroll, 
isRFA (0 or 1)/Player Role, # of Contracts/Use MLE (0 or 1).

The next line holds the player information (name, age, OVR, askingAmount, isRFA, and # of contracts).

The next few lines holds all the contracts that player has received (the team, offer, power ranking, payroll, player role, and 
whether the offer uses MLE or not.)

Once you write out each offer in each line, move onto to the next player, and their contracts, and so on and so forth.

Making a spreadsheet as FA goes will drastically reduce the time required for input.

Remember to also place the final .csv in the same directory as 'decisionmaker.py'.

### TODO:

The generation of interest might need to be touched, and less linear relationships 
must be used.

The open FA decision algorithm may need to be modified to be less random.

Make things look nicer.



