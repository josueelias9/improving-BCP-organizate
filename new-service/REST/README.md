
when you start the project, you are not going to have nothing, so populate with the files and then export

```mermaid

stateDiagram
s0 : Create Document
s1 : Export Transactions
s3 : Create Transactions
s5 : Update Transaction

        [*] --> s0
        s0 --> s3: id
        s3 --> s5
        s5 --> s5
        s5 --> s1

```

if the project is restarted, and you already have the .csv files, you can use them to update the transaction table. You will have to update all the files that you need to work, then import all the csv files

> TODO: this can be done automatically, just reading all csv files from a directory

```mermaid

stateDiagram
s0 : Create Document
s4 : Import Transactions

        [*] --> s0
        s0 --> s0
        s0 --> s4
        s4 --> s4

```

to update the transactions, you will necesarily must know the category names to select the one that fits that specific transaction. Then take that category id and update the transaction

```mermaid

stateDiagram
s3 : Create Transactions
s0 : Get Transactions
s4 : Get Categories
s2 : Update Transaction

        [*] --> s3
        [*] --> s4
        s0 --> s2
        s3 --> s0
        s4 --> s2
        s2 --> s2

```
