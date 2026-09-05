```mermaid
flowchart LR
    c0(Scotiabank)
    c1(bcp_credit)
    c2(yape)
    b0(jpeg)
    b1(pdf)
    b2(csv)
    a0(Scotiabank app)
    a1(BCP app)
    a2(yape app)
    a0  -- snapshot --> b0  --> c0
    a1  -- select --> b1  --> c1
    a2  -- select --> b2  --> c2
subgraph where
    a0
    a1
    a2
    end
subgraph what
    b0
    b1
    b2
    end
subgraph document format
    c0
    c1
    c2
    end
```