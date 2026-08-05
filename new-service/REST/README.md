### case 1

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

### case 2

if the project is restarted, and you already have the .csv files, you can use them to update the transaction table. You will have to update all the files that you need to work, then import all the csv files

> TODO: this can be done automatically, just reading all csv files from a directory

```mermaid

stateDiagram
s0 : Create Document
s4 : Import Transactions
s1 : Get Documents

        [*] --> s0
        s0 --> s0
        s0 --> s1
        s1 --> s4
        s4 --> s4

```

### case 3

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

### final flow

- this project dont work if you dont have transactions in the db. That is why it is important to have apply `Create Document` and `Create Transactions` for all the documents that you have.
- if you have previously saved csv files, you need to import that information. For that, you need to know the unique identifier of the documents already saved on the db. Apply `Get Documents` and then `Import Transactions` for this
- now you are ready to work, but, before updating the transactions, you need to have transactions and the categories abailable. Apply `Get Transactions` and `Get Categories` paralellaly.
- apply `Update Transaction` as many times as you think is necessary
- finally, export all your work to save it in case the db is lost. Apply `Export Transaction`

```mermaid

stateDiagram
cd : Create Document
cds : Create Documents
ct : Create Transactions
it : Import Transactions
gd : Get Documents
et : Export Transactions
state if_state <<choice>>

state Streamlit(localhost:8501) {
        state join_state <<join>>
        state fork_state <<fork>>
        ut : Update Transaction
        gt : Get Transactions
        gc : Get Categories
}
        [*] --> cd
        cd --> ct
        ct --> if_state
        if_state --> gd: csv files
        if_state --> join_state : no csv files
        ct --> cd
        gd --> it
        it --> it
        it --> join_state
        join_state --> gc
        join_state --> gt
        ut --> ut
        ut --> et
        gt --> fork_state
        gc --> fork_state
        fork_state --> ut

```
