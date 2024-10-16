import os
import json

def chunk_text_by_chapter(file_path, bookname):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Split the text by 'CHAPTER' keyword
    chapters = text.split('CHAPTER ')[1:]
    
    # Prepare the JSONL structure
    data = []
    for i, chapter in enumerate(chapters, start=1):
        # Clean the chapter title and content
        chapter_title_and_content = chapter.split('\n', 1)
        chapter_title = chapter_title_and_content[0].strip()
        chapter_content = chapter_title_and_content[1].strip()

        # Create a dictionary entry
        chapter_dict = {f"{bookname}-chapter{i}": chapter_content}
        
        # Append to data list
        data.append(chapter_dict)
    
    # Save to jsonl
    output_file = f"jsonl/{bookname}_chapters.jsonl"
    with open(output_file, 'w', encoding='utf-8') as jsonl_file:
        for entry in data:
            jsonl_file.write(json.dumps(entry) + '\n')

    print(f"Chapters saved to {output_file}")

def process_books_in_folder(folder_path):
    # Loop through all .txt files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            # Get full file path
            file_path = os.path.join(folder_path, filename)
            
            # Use the filename (without extension) as the book name
            bookname = os.path.splitext(filename)[0]
            
            print(f"Processing {filename}...")
            chunk_text_by_chapter(file_path, bookname)

# Example usage:
process_books_in_folder('/root/Xiangpeng/HarryPotter-memory/book')
