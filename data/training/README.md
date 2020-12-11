# Sample training data
## Files
* case.txt `Input file`
* parsed_field.json `Standard output`
* field_for_training.json `Data used for training`
* generator.py `Script to generate training data based on standard output for reference`
## Basic training input format
```json
{
    "case_id": {                                // Attribute name
        "content": "（2019）黑0521民初2092号",   // Content
        "line": 1,                              // Starting line number (starting from 0)
        "start": 3,                             // Starting character sequence number (starting from 0, including)
        "stop": 70                              // End character sequence number (starting from 0, not including)
    }
}
```
