Social_Memory_Template = [
    {"role": "system", 
     "content": """
        I have an event description from the perspective of Harry Potter, and I want to extract two types of memory from it: social memory (related to the people Harry interacts with) and knowledge memory (related to the knowledge Harry gains or applies in the event).

        For each person mentioned in the event, extract their social memory in the following format:

        {{
        "name": "Person's full name",
        "other-names": "Any nicknames or alternate names used for this person in the event, or null if none are present.",
        "description": "A brief description of this person, focusing only on their role or characteristics within this specific event.",
        "impression": "Harry's emotional or cognitive impression of this person during the event. Only include information directly tied to Harry's experience in this specific event.",
        "relationship": "The nature of the relationship between Harry and this person (e.g., friend, ally, enemy, etc.), based on this event.",
        "interaction": "A specific interaction Harry has with this person during the event, focusing strictly on what happens in this event."
        }}

        For any knowledge Harry gains or applies in the event, extract knowledge memory in the following format:

        {{
        "name": "The name of the knowledge or skill (e.g., a spell, fact, tactic, or experience).",
        "description": "A brief description of the knowledge or skill, focusing on what is learned or applied in the event.",
        "learning_context": "The specific context or moment in the event where Harry learns or applies this knowledge.",
        "knowledge_content": "The key content or essence of the knowledge Harry learns or applies in the event.",
        "outcome": "The result or outcome of applying the knowledge in this event.",
        }}

        And you need to output social memory and knowledge memory in one json format, here is the Expected Output Example:

        {{
            "social_memory": [
                {{
                "name": "Hermione Granger",
                "other-names": null,
                "description": "Muggle-born witch, one of Harry's companions during their refuge at Grimmauld Place.",
                "impression": "In this event, Hermione remained calm and focused while helping Harry with the protective spells.",
                "relationship": "Friend",
                "interaction": "During their stay at Grimmauld Place, Hermione assisted Harry in understanding and dealing with the protective spells around the house."
                }},
                {{
                "name": "xxx",
                "other-names": null,
                "description": "xxx",
                "impression": "xxx",
                "relationship": "xxx",
                "interaction": "xxx"
                }},

                ...
            ],
            "knowledge_memory": [
                {{
                "name": "Defensive Spells",
                "description": "Magical spells set up for defense against intruders or enemies.",
                "learning_context": "While seeking refuge at Grimmauld Place, Harry encountered and xxx",
                "knowledge_content": "xxx",
                "outcome": "Harry successfully led the group through the defensive measures, xxx.",
                }},

                ...
            ]
        }
        if there is no social memory or knowledge memory, just leave the corresponding list empty. like:
        {{
        "social_memory": [],
        "knowledge_memory": []
        }}

        JUST OUTPUT THE JSON, WITH NO OTHER TEXT.

    """},
    {"role": "user",
    "content": """
        ---Input---
        Here is the event you need to extract social memory and knowledge memory from: 

        {input_text}
    """}
]

Combine_Social_Template = [
    {"role": "system", 
     "content": """
        You are tasked with merging social memory cards that describe interactions between Harry Potter and other characters. Each social memory card contains fields such as name, other-names, description, impression, relationship, and interaction. Your goal is to merge multiple cards related to the same person into a single card, ensuring that the description and impression fields are summarized rather than concatenated.

        Follow these steps for merging:
        
        1.Summarize the description: Combine the description fields from both cards into a cohesive summary that reflects the key points about the person's role in Harry's life, while avoiding repetition. The summary should be concise but retain the essence of past and present interactions.
        2.Summarize the impression: Combine the impression fields by summarizing the most important aspects of how Harry feels about the person. Focus on how Harry's views have evolved over time and provide a balanced, concise statement.
        3.Update the relationship: Always take the most recent relationship status from the newest card to reflect the latest understanding of the relationship.
        4.Keep the latest interaction: Replace the older interaction field with the most recent one to ensure only the latest interaction is preserved.
        5.Update the name and other-names: Keep the primary name field unchanged. If there are multiple names (e.g., nicknames, aliases, titles), update the other-names field to include all unique names used for the person. Ensure there are no duplicates.

        Ensure the summaries are concise, coherent, and reflective of the key aspects of Harry's relationship with the person.

        Expected Output in JSON format, the key should be "merged_profile", the value should be a list of profiles with name, other-name, description, impression, relationship, interaction. 
        Here is the Expected Output Example:
        {{"merged_profile": [
                {{
                "name": "Hermione Granger",
                "other-names": null,
                "description": "Muggle-born witch, one of Harry's companions during their refuge at Grimmauld Place.",
                "impression": "In this event, Hermione remained calm and focused while helping Harry with the protective spells.",
                "relationship": "Friend",
                "interaction": "During their stay at Grimmauld Place, Hermione assisted Harry in understanding and dealing with the protective spells around the house."
                }},
                {{
                "name": "xxx",
                "other-names": null,
                "description": "xxx",
                "impression": "xxx",
                "relationship": "xxx",
                "interaction": "xxx"
                }}
            ]
        }}
        NOTE IF THE TWO CARDS ARE NOT THE SAME PERSON, JUST RETURN THE TWO CARDS WITHOUT ANY MERGING. AS THE OUTPUT IS A LIST OF TWO CARDS, YOU CAN RETURN THE TWO CARDS IN ANY ORDER.
        IF THE TWO CARDS ARE THE SAME PERSON, JUST RETURN THE MERGED PROFILE. AS THE OUTPUT IS A LIST OF ONE CARD.
        JUST OUTPUT THE JSON, WITH NO OTHER TEXT.

    """},
    {"role": "user",
    "content": """
        ---Input---
        Here is the old card: 

        {old_card}

        Here is the new card: 

        {new_card}
    """}
]

Valid_JSON_Template = [
    {"role": "system", 
     "content": """
        You are a JSON validator and corrector. Your task is to take any input and modify it to be a valid JSON format. If the input is already in valid JSON, return it unchanged. If the input is not valid, correct the syntax errors while maintaining the original structure and intent.

        Make sure the output is:

        Well-formed and valid JSON.
        Correctly formatted with proper use of quotes, commas, colons, brackets, and curly braces.
        All keys are strings enclosed in double quotes, and values are properly formatted according to JSON rules.
        Just output the corrected JSON with no other text. If the input is already valid, return it as is.

    """},
    {"role": "user",
    "content": """
        ---Input---
        Here is the JSON you need to correct: 

        {input_text}
    """}
]