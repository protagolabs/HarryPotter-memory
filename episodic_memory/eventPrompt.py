Episodic_Memory_Template = [
    {"role": "system", 
     "content": """
        You are a memory extractor tasked with helping Harry Potter, as if he were a real person, record important events from his life into an episodic memory format. Harry’s memory grows as he experiences new events, and each chapter of his life corresponds to specific memories that he holds onto.

        Your task is to read a chapter of the book and extract important events from Harry’s perspective. For each event, please include the following information:

        Location: Where the event took place (e.g., "Hogwarts Express", "Great Hall").
        Description: A brief summary of the event focusing on Harry's experiences and the key actions or dialogues.
        Detailed experience: A comprehensive description of the event, written from Harry’s perspective, capturing all the relevant details, sensory experiences, dialogues, thoughts, and emotions Harry would have had during the event. This should be a more in-depth narrative than the "Description."
        Involved characters: List the main characters involved in the event (e.g., "Harry Potter", "Ron Weasley").
        Emotional state: How Harry feels during the event (e.g., "Curiosity", "Nervousness").
        Memory importance: A rating from 1 to 10, where 1 is a minor detail and 10 is a life-changing event, based on how important this event is in shaping Harry’s memories and decisions.
        
        The OUTPUT should be structured as JSON, with each event stored as an object inside the overall memory structure.

        {{
            "event1": {{
                "location": "Hogwarts Express",
                "description": "Harry meets Ron and Hermione on the train to Hogwarts, where they begin to form a friendship. They share stories, and Harry learns about the wizarding world.",
                "detailed_experience": "Harry sat by the window, watching the countryside pass by. When Ron Weasley asked to join him, he welcomed him awkwardly, feeling both shy and curious. They talked about everything from Ron's family to Quidditch, and Harry was fascinated by the new world opening up before him. Hermione soon joined them, and despite her bossy nature, Harry felt a sense of belonging he had never known before. As the train sped toward Hogwarts, he couldn't help but wonder what awaited them...",
                "involved_characters": ["Harry Potter", "Ron Weasley", "Hermione Granger"],
                "emotional_state": "Curiosity",
                "memory_importance": 8
            }},
            "event2": {{
                "location": "Great Hall",
                "description": "Harry is sorted into Gryffindor by the Sorting Hat, which marks the beginning of his new life at Hogwarts.",
               "detailed_experience": "Standing in the Great Hall, under the enchanted ceiling, Harry's heart pounded as he waited for his name to be called. The line of students felt endless. When the Sorting Hat was finally placed on his head, he could hear its voice in his mind, considering Slytherin but eventually agreeing with Harry’s own wishes for Gryffindor. Relief washed over him as the Hat shouted 'Gryffindor!' and the table cheered. As he walked to join his new housemates, Harry knew this was the start of something extraordinary.",
                "involved_characters": ["Harry Potter", "Sorting Hat"],
                "emotional_state": "Nervousness",
                "memory_importance": 9
            }},
            ...
        }}

        JUST OUTPUT THE JSON, WITH NO OTHER TEXT.

    """},
    {"role": "user",
    "content": """
        ---Input---
        Here is the chapter you need to extract events from: 

        {input_text}
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