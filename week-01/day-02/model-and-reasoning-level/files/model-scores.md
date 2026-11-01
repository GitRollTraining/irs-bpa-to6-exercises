# Two models on the same 20 notes

The course made up these scores, waits and costs. The costs are not the prices of a vendor.

A teammate wants the extractor to call sonnet in place of haiku. Haiku is the model that the extractor calls now. Sonnet is a more capable model from the same vendor.

Before any change, the team sent each note of its evaluation set to each model five times. The set has 20 notes. For each note, the team wrote down the correct five fields before the run. Both models got the same system prompt and the same schema. Then the team compared each reply with the correct fields.

| | haiku, the model now | sonnet |
|---|---|---|
| Notes with the correct fields in all five replies | 16 of 20 | 17 of 20 |
| Notes with a wrong field in one or more replies | 0104: `amount_in_question`, an amount in place of null in two of the five replies. 0105 and 0122: `amount_in_question`. 0137: `tax_year`. | 0105 and 0122: `amount_in_question`. 0137: `tax_year`. |
| Wait for one note, on average | 2 seconds | 5 seconds |
| Cost of 1,000 notes | 1 dollar | 3 dollars |

The extractor will read thousands of notes, one note in each call.
