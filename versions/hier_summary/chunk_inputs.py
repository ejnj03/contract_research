import pandas as pd
import re

def chunk_text(input_text):
    # Dictionary to hold the sections
    sections = {}
    
    # Define the section titles to split on
    section_titles = ['BACKGROUND', 'INTRODUCTION', 'FACTS', 'SUMMARY JUDGMENT STANDARD', 'LEGAL STANDARD', 'MATERIAL FACTS', 'ANALYSIS', 'DISCUSSION', 'CONCLUSION']
    
    # First, split the text by the main sections
    split_text = re.split(r'(?=BACKGROUND|Background|Introduction|INTRODUCTION|FACTS|Facts|SUMMARY JUDGMENT STANDARD|Summary Judgment Standard|LEGAL STANDARD|Legal Standard|MATERIAL FACTS|Material Facts|ANALYSIS|Analysis|DISCUSSION|Discussion|CONCLUSION|Conclusion)', input_text)

    for i in range(len(split_text)):
        # For each section, find the title and the associated text
        for title in section_titles:
            if split_text[i].lower().startswith(title.lower()):
                # Store the section with the title as the key
                sections[title] = split_text[i]
                break

    # Further split the DISCUSSION section into subsections (A, B, C, ...)
    if 'DISCUSSION' in sections:

        # Modify regex to handle patterns like "A.The Parties and Their Relationships"
        discussion_split = re.split(r'\n', sections['DISCUSSION'], flags=re.MULTILINE)
        subsections = {}
        
        # Store the subsections as A, B, C, etc., with the text that follows the section name
        char = 'A'
        for idx, part in enumerate(discussion_split):
            
            match = re.match(rf'^({char})\.(.+)', part)
            if match:
                # Find the text that belongs to this section (everything after the section header)

                section_value = ''
                next_char = chr(ord(match.group(1)) + 1)
                
                # Collect everything that follows this subsection until the next subsection or the end
                for following_part in discussion_split[idx + 1:]:
                    
                    if re.match(rf'^({next_char})\.(.+)', following_part):
                        break
                    section_value += following_part + '\n'
                
                char = next_char
                subsections[part] = section_value.strip()

        # Handle numeric subsections (e.g., "1.", "2.", etc.) if no lettered subsections are found
        if len(subsections) == 0:
            num = '1'
            for idx, part in enumerate(discussion_split):
                match = re.match(rf'^({num})\.(.+)', part)
                if match:

                    section_value = ''
                    next_num = str(int(match.group(1)) + 1)
                    for following_part in discussion_split[idx + 1:]:
                        if re.match(rf'^{next_num}\.(.+)', following_part):
                            break
                        section_value += following_part + '\n'
                    num = next_num
                    subsections[part] = section_value.strip()

        # If fewer than 2 subsections are found, use the entire DISCUSSION text
        if len(subsections) <= 2:
            subsections = {'DISCUSSION': sections['DISCUSSION']}
        
        #print(subsections.keys())
        sections['DISCUSSION'] = subsections

    # Similarly handle the ANALYSIS section
    if 'ANALYSIS' in sections:
        analysis_split = re.split(r'\n', sections['ANALYSIS'], flags=re.MULTILINE)
        subsections = {}

        # Store the subsections as A, B, C, etc., with the text that follows the section name
        char = 'A'
        for idx, part in enumerate(analysis_split):
            
            match = re.match(rf'^({char})\.(.+)', part)
            if match:
                
                section_value = ''
                next_char = chr(ord(match.group(1)) + 1)
                
                # Collect everything that follows this subsection until the next subsection or the end
                for following_part in analysis_split[idx + 1:]:
                    
                    if re.match(rf'^({next_char})\.(.+)', following_part):
                        break
                    section_value += following_part + '\n'
                char = next_char
                subsections[part] = section_value.strip()

        if len(subsections) == 0:
            num = '1'
            for idx, part in enumerate(analysis_split):
                match = re.match(rf'^({num})\.(.+)', part)
                if match:
                    section_key = match.group(1) + '.'  # e.g., "1."
                    section_value = ''
                    
                    for following_part in analysis_split[idx + 1:]:
                        if re.match(r'^([0-9])\.(.+)', following_part):
                            break
                        section_value += following_part + '\n'
                    
                    subsections[part] = section_value.strip()
                    num = next_num
        if len(subsections) <= 2:
            subsections = {'ANALYSIS': sections['ANALYSIS']}
        
        #print(subsections.keys())

        sections['ANALYSIS'] = subsections
    
    return sections

def chunk_csv():
    labels_df = pd.read_csv('labels.csv') 
    citations = labels_df['citation']
    text_list = labels_df['text'].to_list()
    citation_list = citations.to_list()
    label_list = labels_df['corrected_labels'].to_list()
    
    # Process each sample by chunking the text and storing relevant info
    samples = [{"citation": citation, "text": chunk_text(str(text)), "label": label} for citation, text, label in zip(citation_list, text_list, label_list)]
    return samples

if __name__ == "__main__":
    samples = chunk_csv()
    for sample in samples:
        if sample["citation"] == "377 F.Supp.3d 633":
            print(sample["text"].keys())
            print(sample["text"]["DISCUSSION"].keys())
            print(sample["text"])