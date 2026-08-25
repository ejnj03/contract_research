import json
import pandas as pd
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

#complete list of texts 
def format_csv():
    labels_df = pd.read_csv('labels.csv') 
    citations = labels_df['citation']
    text_list = labels_df['text'].to_list()
    citation_list = citations.to_list()
    label_list = labels_df['corrected_labels'].to_list()
    
    samples = [{"citation": citation, "text": str(text), "label": label} 
               for citation, text, label in zip(citation_list, text_list, label_list)]
    
    for sample in samples:
        if len(sample["text"]) <= 100:  # Corrected check for NaN
            file_path = f'data/{sample["citation"]}.txt'
            if os.path.exists(file_path):  # Ensure file exists before opening
                with open(file_path, 'r') as f:
                    text = f.read()
                    sample["text"] = text
    
    # Debugging output for entries that still have NaN text
    for _, input_sample in enumerate(samples):
        if len(sample["text"]) <= 100:  # Check for NaN text
            print(f"Missing text for citation: {input_sample['citation']}")
    
    return samples

part_1 = "Evaluate the results of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly as instructed, and give the fully evaluated output in the format:  $motions = Motions(opinion_text)$ $issues = Issues(Motions(opinion_text))$, in the instructed variable type (dict, list, etc.) in the indicated return variable type (dict, list, etc.).  Do not skip any steps or components of the input/output, despite the length and complexity of the task. These are the functions to evaluate:   Motions(opinion_text): return the set of specific occasion (procedural action) and the motivating party (the party that filed the procedural action) that the court issues a decision on in opinion_text;  examples: {“Defendants' Motion to Dismiss”, ““Defendants' Motion to Stay”}, {“Plaintiff’s Motion for Summary Judgment”}, {“Defendant’s Appeal”};  Alternatively, if the opinion_text is on a trial, not a pretrial motion or an appeal, is should be a set of claims made by the plaintiff against the defendant (example: {Plaintiff's Negligence and Breach of Contract Claim”}); If the motions are motions for summary judgment made by the plaintiff and defendant, return {“Motion for Summary Judgment”); Issues(Motions(opinion_text)):  for each motion m in the set Motions(opinion_text): identify the issues that the court identifies as key to the making a judgment on the motion, extracted directly from the opinion_text as a set, following the format in the example below: For motion m = “Defendants' Motion to Dismiss”: “Defendants' Motion to Dismiss”: {“whether the Court may exercise limited personal jurisdiction over Defendants”, “whether it has subject matter jurisdiction”, “whether it has subject matter jurisdiction under the diversity statute”}; And using as much of the original text from opinion_text as possible; The returned value should be a fully expanded dictionary dict with key motion m: value set(); Example: for Motions(opinion_text) = {“Defendants' Motion to Dismiss”, “Defendants' Motion to Stay”: Issues(Motions(opinion_text)) = {“Defendants' Motion to Dismiss”: {“whether the Court may exercise limited personal jurisdiction over Defendants”, “whether it has subject matter jurisdiction”, “whether it has subject matter jurisdiction under the diversity statute”}, “Defendants' Motion to Stay”: {“whether or not the two proceedings are ‘parallel’”}}; return dict"
part_2 = "Using the result of evaluating Issues(Motions(opinion_text)) from your previous response as issues_dict, evaluate the results of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly as instructed, and give the fully evaluated and expanded output in the format:  $issue_linked_dict, leaves = Decompose(issues_dict)$;  in the indicated return variable type (dict, list, etc.) and expand all leaves fully. Do not skip any steps or components of the input/output, despite the length and complexity of the task (do not skip any of the recursive calls). These are the functions to evaluate:   Decompose(issues_dict): issue_linked_dict = {}; leaves = []; def Recurse(issues): If issues is empty: return; Else for each issue i in issues s: sub_issues = {}; identify whether the court specifies other issues, burden of proof(s), or legal standards that the issue i is contingent upon; if there are any such sub-issues that can be extracted directly from the opinion_text as a set, give them as a set of sub-issues, and set sub_issues to the set such sub-issues (sub_issues are typically of the form “... whether….” or “... defendant must …” or “... plaintiff must…”); Use as much of the original text from opinion_text as possible; If sub_issues is not empty:  set issue_linked_dict[i] to sub_issues and Recurse(sub_issues); Else if sub_issues is empty: add issue i to leaves and return (without adding key i to issue_dict); For motion m: issues s in issues_dict.items(): Recuse(issues = s); Return issue_linked_dict, leaves; Example:  Calling Recurse(issues) for issues = {“whether the Court may exercise limited personal jurisdiction over Defendants”, “whether it has subject matter jurisdiction under the diversity statute”}: After the first call issues_dict = {“whether the Court may exercise limited personal jurisdiction over Defendants”: {““whether any of Michigan's relevant long-arm statutes authorize the exercise of jurisdiction over Defendants”, “whether exercise of that jurisdiction comports with constitutional due process.”}, “whether it has subject matter jurisdiction under the diversity statute”:  {Court addresses Defendants' Rule 12(b)(6) challenges to the remaining claims to determine whether diversity jurisdiction exists.}, leaves = []; After the second recursive call(s) issues_dict = [“whether the Court may exercise limited personal jurisdiction over Defendants”: {“whether any of Michigan's relevant long-arm statutes authorize the exercise of jurisdiction over Defendants”, “whether exercise of that jurisdiction comports with constitutional due process.”}, “whether exercise of that jurisdiction comports with constitutional due process.”: {“To show that the exercise of personal jurisdiction comports with due process, Plaintiffs must “establish with reasonable particularity sufficient ‘minimum contacts' with Michigan so that the exercise of jurisdiction over Defendants would not offend ‘traditional notions of fair play and substantial justice.”}},  leaves = [“whether any of Michigan's relevant long-arm statutes authorize the exercise of jurisdiction over Defendants”, “Court addresses Defendants' Rule 12(b)(6) challenges to the remaining claims to determine whether diversity jurisdiction exists.”];"
part_3 = "Using the result of evaluating Decompose(issues_dict) from your previous response, with issue_linked_dict, leaves = Decompose(issues_dict), evaluate the results of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly as instructed, and give the fully evaluated and expanded output in the format:  $debates = Crossfire(leaves)$;  in the indicated return variable type (dict, list, etc.) and expand the entire dictionary debates in your returned response. Do not skip any steps or components of the input/output, despite the length and complexity of the task (do not skip any leaves, or the fleshing out of any leaves). These are the functions to evaluate:   Crossfire(leaves):  debates = {}; for each leaf l in leaves: plaintiff_positions; defendant_positions ; Set plaintiff_positions to  the set of all claim(s) or arguments made by the plaintiff that directly engage leaf l, or take a position on leaf l; there may be none; Use as much of the original text from opinion_text as possible; Set defendant_positions to the set of all claim(s) or arguments made by the plaintiff that directly engage leaf l, or take a position on leaf l; there may be none; Use as much of the original text from opinion_text as possible; plaintiff_chains = []; defendant_chains = []; def Recurse_argue(positions, party, chain): If positions is empty:; return; For position p in positions: refutations = {}, support = {}; Set refutations to be the set of all argument(s) or refutation(s) made by the party’s opponent directly against position p; Use as much of the original text from opinion_text as possible; Set support to be the set of all supporting argument(s) or evidence(s) presented by the party directly supporting position p; Use as much of the original text from opinion_text as possible; If refutations is not empty: Add  tuple (positions, “refutations”, refutations) to chain; If support is not empty: Add  tuple (positions, “support”, support) to chain; Set opposing_party to defendant if party is plaintiff; set opposing party to plaintiff if party is defendant; Recurse_argue(support, party, chain); Recurse_argue(refutations, opposing_party, chain); Recurse_argue(plaintiff_positions, plaintiff, plaintiff_chains); Recurse_argue(defendant_positions, defendant, defendant_chains); Set debates[leaf][“plaintiff”] = plaintiff_chains if plaintiff_chains is not empty; else don’t add the key to debates[leaf]; Set debates[leaf][“defendant”] = defendant_chains if defendant_chains is not empty; else don’t add the key to debates[leaf]; Return debates;"
part_4 = "Using the result of evaluating Crossfire(leaves) from your previous response as debates, evaluate the results of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly as instructed, and give the fully evaluated interpretation_disputes dictionary in the format:  $interpretation_disputes = Type_dispute(debates)$  in the indicated return variable type (dict, list, etc.) in the function. Do not skip any steps or components of the input/output, despite the length and complexity of the task. These are the functions to evaluate:   $interpretation_disputes = Type_dispute(debates)$  Type_dispute(debates):  Define phrase as: a small group of words standing together as a conceptual unit, typically forming a component clause of a sentence (example: “to improve standards”); a sentence is not a phrase; Define contract as: a legally binding agreement between two parties, enforceable by law; if the word or phrase is a word or phrase that is directly quoted from a contract, as defined; Disputes = {} For each leaf, positions in debates.items(): Referencing leaf and all components of positions: Identify the set of all disagreement(s), or issue(s), between the plaintiff and defendant that satisfy the requirement of being about: “the interpretation/definition of a phrase or word in a given contract between the defendant and the plaintiff”; OR “whether a phrase or word in a contract between the defendant and the plaintiff is ambiguous and subject to interpretation”; OR  “what standards should be applied to interpreting a phrase or term in a contract between the defendant and the plaintiff”; And assign this set to the variable all_disputes;  For dispute in all_disputes: set argument_type to the  requirement that dispute satisfies (ex. If it satisfies “the interpretation/definition of a phrase or word in a given contract between the defendant and the plaintiff”, then  argument_type = “the interpretation/definition of a phrase or word in a given contract between the defendant and the plaintiff”); referencing all components of positions:  set plaintiff_argument to the argument regarding argument_type that the plaintiff makes about the word or phrase that dispute is about; set defendant_argument to the argument regarding argument_type that the defendant makes about  the word or phrase dispute is about; set disputed_word to the word or phrase that defendant_argument and plaintiff_argument assert (their respective opinion on) argument_type; this should be the specific word or phrase that is disputed, not the sentence or larger clause that the word or phrase belongs to.; disputed_word must be a word or phrase that is present, word for word, in a contract between the plaintiff and defendant; set  court_opinion to the side that the court opinion takes dispute (“plaintiff” or “defendant”);  If the court does not directly discuss, or mention its stance on argument_type regarding word or phrase: continue (without adding the key disputed_word to Disputes); Set contract_excerpt to the contract clause or sentence within the contract that locus belongs to; Set: Disputes[disputed_word][“Argument Type”] = argument_type; Disputes[disputed_word][“Plaintiff”] = plaintiff_argument; Disputes[disputed_word][“Defendant”] = defendant_argument; Disputes[disputed_word][“Court Opinion”] = court_opinion; Disputes[disputed_word][“Excerpt”] = contract_excerpt; return Disputes;"

def to_gpt_input(model, file_name, steps_file_name, ref_archive):
    samples = format_csv()
    with open(file_name, 'w') as f, open(steps_file_name, 'w') as f_s, open(ref_archive, 'r') as archive_r:
        archive_dict = file.readline().strip()
        for number, input_sample in enumerate(samples):
            content = "\n opinion_text = " + input_sample["text"]
            citation = input_sample["citation"]
            if input_sample["citation"] in archive_dict:
            with open(file_path, 'w') as archive_w:
                messages = [
                    {"role": "user", "content": part_1.strip() + content.strip()},
                    #{"role": "user", "content": question_7.strip()},
                    {"role": "assistant", "content": input_sample["citation"]["part_1"]}
                    {"role": "user", "content": part_2.strip()}
                    {"role": "assistant", "content": input_sample["citation"]["part_2"]}
                    {"role": "user", "content": part_3.strip()}
                    {"role": "assistant", "content": input_sample["citation"]["part_3"]}
                    {"role": "user", "content": part_4.strip()}
                ]
                #archive of files up to current step
                

                
                    
                    # Construct the message dictionary
                    messages = [
                        {"role": "user", "content": part_1.strip() + content.strip()},
                        
                        #{"role": "user", "content": question_7.strip()},
                    ]
                    
                    # Construct the full JSON object
                    print("extracting response 1...")
                    response = client.chat.completions.create(model= model, messages= messages)
                    print("writing response for " + citation + " step 1")
                    message = citation + " [START_1] " + response.choices[0].message.content + " [END_1] "
                    #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                    print(message)
                    # Write the JSON object as a string to the file
                    f_s.write(json.dumps(message))
                    messages.append({"role": "assistant", "content": response.choices[0].message.content})
                    messages.append({"role": "user", "content": part_2.strip()})

                    print("extracting response 2...")
                    response = client.chat.completions.create(model= model, messages= messages)
                    print("writing response for " + citation + " step 2")
                    message = " [START_2] " + response.choices[0].message.content + " [END_2] "
                    #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                    print(message)
                    # Write the JSON object as a string to the file
                    f_s.write(json.dumps(message))
                    messages.append({"role": "assistant", "content": response.choices[0].message.content})
                    messages.append({"role": "user", "content": part_3.strip()})

                    print("extracting response 3...")
                    response = client.chat.completions.create(model= model, messages= messages)
                    print("writing response for " + citation + " step 3")
                    message = " [START_3] " + response.choices[0].message.content + " [END_3] "
                    #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                    print(message)
                    # Write the JSON object as a string to the file
                    f_s.write(json.dumps(message))
                    messages.append({"role": "assistant", "content": response.choices[0].message.content})
                    messages.append({"role": "user", "content": part_4.strip()})

                print("extracting final response...")
                response = client.chat.completions.create(model= model, messages= messages)
                print("writing response for " + citation + " step 4")
                message = response.choices[0].message.content
                #other_messages = citation + response.choices[2].message.content + response.choices[1].message.content
                print(message)
                # Write the JSON object as a string to the file
                f.write(json.dumps(message))

                #f_s.write(json.dumps())
                f_s.write('\n')
                f.write('\n')

if __name__ == '__main__':
    to_gpt_input(model="o1-preview", file_name='o1_structured_output_ref.jsonl', steps_file_name = 'o1_structured_output_ref.jsonl', ref_archive = 'o1_step_3.jsonl')
