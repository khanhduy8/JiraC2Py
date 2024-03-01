import json

def comment_content(cmd_out, cmd_err):
    data = {
        "body": {
            "content": [
            {
                "content": [
                {
                    "text": cmd_out,
                    "type": "text"
                }
                ],
                "type": "codeBlock"
            },
            {
                "content": [
                {
                    "text": cmd_err,
                    "type": "text"
                }
                ],
                "type": "codeBlock"
            }
            ],
            "type": "doc",
            "version": 1
        }
    }
    return json.dumps(data)

def issue_content(key, summary):
    data = {
    "fields": {
            "project": {
                "key": key
            },
            "summary": summary,
            "issuetype": {
                "name": "Task"
            }
        }
    }
    
    return json.dumps(data)

    