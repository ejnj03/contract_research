"""v2 - four chained prompts (canonical).

part_1 Motions + Issues -> part_2 issue decomposition -> part_3 argument trees
-> part_4 contract-language disputes. Each step consumes the previous response.

Used by: versions/o1_structured_input.py, versions/step_4.py,
         versions/gpt_4_turbo_unbatched.py
"""

part_1 = """
Evaluate the results of the functions below for the given opinion_text, performing all the detailed steps in the 
functions exactly as instructed, and give the fully evaluated output in the format:  "[RESPONSE] motions = Motions(opinion_text), 
issues = Issues(Motions(opinion_text)) [END RESPONSE]", where both motions is a set of strings, and issues is a dict of string: set of strings.  
Do not skip any steps or components of the input/output, despite the length and complexity of the task. Do not include anything else in your 
response other than the fully evaluated output in the requested format.

These are the functions to evaluate: 

1. Motions(opinion_text): return the set of specific occasion (procedural action) and the motivating party (the 
party that filed the procedural action) that the court issues a decision on in opinion_text;  

    a. examples: {“Defendants' Motion to Dismiss”, ““Defendants' Motion to Stay”}, {“Plaintiff’s 
    Motion for Summary Judgment”}, {“Defendant’s Appeal”};  

    b. Alternatively, if the opinion_text is on a trial, not a pretrial motion or an appeal, it should be a set 
    of claims made by the plaintiff against the defendant (example: {Plaintiff's Negligence and Breach 
    of Contract Claim”}); 

    c. If the motions are motions for summary judgment made by the plaintiff and defendant, return 
    {“Motion for Summary Judgment”); 

2. Issues(Motions(opinion_text)):  
    a. for each motion m in the set Motions(opinion_text): identify the issues that the court identifies as 
    key to the making a judgment on the motion, extracted directly from the opinion_text as a set, 
    following the format in the example below: 

        i. For motion m = “Defendants' Motion to Dismiss”: 
            1. “Defendants' Motion to Dismiss”: {“whether the Court may exercise limited 

            personal jurisdiction over Defendants”, “whether it has subject matter 
            jurisdiction”, “whether it has subject matter jurisdiction under the diversity 
            statute”}; 

        ii. And using as much of the original text from opinion_text as possible; 
    b. The returned value should be a fully expanded dictionary dict with key motion m: value set(); 

        i. Example: for Motions(opinion_text) = {“Defendants' Motion to Dismiss”, “Defendants' 
        Motion to Stay”: 

            1. Issues(Motions(opinion_text)) = {“Defendants' Motion to Dismiss”: {“whether 
            the Court may exercise limited personal jurisdiction over Defendants”, “whether 
            it has subject matter jurisdiction”, “whether it has subject matter jurisdiction 
            under the diversity statute”}, “Defendants' Motion to Stay”: {“whether or not the 
            two proceedings are ‘parallel’”}}; 

    c. return dict 
"""

part_2 = """
Using the result of evaluating issues = Issues(Motions(opinion_text)) from your previous response, with issues_dict = issues, 
evaluate the results of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly 
as instructed, and give the fully evaluated and expanded output in the format:  
‘[RESPONSE] (python) updated_issues_dict, leaves = Decompose(issues_dict) [END RESPONSE]’ ; 
where updated_issues_dict should be a valid nested python dictionary of string: set of strings, and leaves should be a valid list of strings, 
fully expanded without skipping any recursive calls. Do not skip any steps or components of the input/output, despite the length and complexity of the task 
(do not skip any issues/sub_issues, or the fleshing out of any recursive calls to sub_issues/issues). Do not include anything else in your 
response other than the fully evaluated output in the requested format.
These are the functions to evaluate: 

3. Decompose(issues_dict): 

    a. issue_linked_dict = {\}; 
    b. leaves = []; 
    c. def Recurse(issues): 

        i. If issues is empty: return; 
        ii. Else for each issue i in issues s: 

            1. sub_issues = {\}; 
            a. identify whether the court specifies other issues, burden of proof(s), or 

            legal standards that the issue i is contingent upon; if there are any such 
            sub-issues that can be extracted directly from the opinion_text as a set, 
            give them as a set of sub-issues, and set sub_issues to the set such 
            sub-issues (sub_issues are typically of the form “... whether….” or “... 
            defendant must …” or “... plaintiff must…”); Use as much of the 
            original text from opinion_text as possible; 

            b. If sub_issues is not empty:  
                i. set issue_linked_dict[i] to sub_issues and 

                Recurse(sub_issues); 
            c. Else if sub_issues is empty: add issue i to leaves and return (without 

            adding key i to issue_dict); 
        d. For motion m: issues s in issues_dict.items(): 

            i. Recuse(issues = s); 
        e. Return issue_linked_dict, leaves; 
        f. Example:  

            Calling Recurse(issues) for issues = {“whether the Court may exercise limited personal 
            jurisdiction over Defendants”, “whether it has subject matter jurisdiction under the diversity 
            statute”}: 
            After the first call issue_linked_dict = {“whether the Court may exercise limited personal jurisdiction 
            over Defendants”: {“whether any of Michigan's relevant long-arm statutes authorize the exercise 
            of jurisdiction over Defendants”, “whether exercise of that jurisdiction comports with 
            constitutional due process.”}, “whether it has subject matter jurisdiction under the diversity 
            statute”:  {Court addresses Defendants' Rule 12(b)(6) challenges to the remaining claims to 
            determine whether diversity jurisdiction exists.}, leaves = []; 

            g. After the second recursive call(s) issue_linked_dict = [“whether the Court may exercise limited personal 
            jurisdiction over Defendants”: {“whether any of Michigan's relevant long-arm statutes authorize 
            the exercise of jurisdiction over Defendants”, “whether exercise of that jurisdiction comports with 
            constitutional due process.”}, “whether exercise of that jurisdiction comports with constitutional 
            due process.”: {“To show that the exercise of personal jurisdiction comports with due process, 
            Plaintiffs must “establish with reasonable particularity sufficient ‘minimum contacts' with 
            Michigan so that the exercise of jurisdiction over Defendants would not offend ‘traditional notions 
            of fair play and substantial justice.”/}/},  leaves = [“whether any of Michigan's relevant long-arm 
            statutes authorize the exercise of jurisdiction over Defendants”, “Court addresses Defendants' Rule 
            12(b)(6) challenges to the remaining claims to determine whether diversity jurisdiction exists.”]; 
"""

part_3 = """
Using the result of evaluating updated_issues_dict, leaves = Decompose(issues_dict) from your previous response, with leaves, 
evaluate the results of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly as 
instructed, and give the fully evaluated and expanded output in the format:  ‘[RESPONSE] (python) debates = Crossfire(leaves) [END RESPONSE]’ ; 
where debates should be a variable representing a valid nested python dictionary of strings, fully expanded for each leaf in leaves and each 
recursive call to Recurse_argue. Do not skip any steps or components of the input/output, despite the length and complexity of the task 
(do not skip any leaves, or the fleshing out of any leaves; do not skip any recursive calls, or any ‘positions’ within the call). Do not include anything else in your 
response other than the fully evaluated output in the requested format.
These are the functions to evaluate: 

4. Crossfire(leaves):  
    a. debates = {/}; 
    b. for each leaf l in leaves: 

        i. plaintiff_positions; 
        ii. defendant_positions ; 

        iii. Set plaintiff_positions to  the set of all claim(s) or arguments made by the plaintiff that 
        directly engage leaf l, or take a position on leaf l; there may be none; Use as much of the 
        original text from opinion_text as possible; 

        iv. Set defendant_positions to the set of all claim(s) or arguments made by the plaintiff that 
        directly engage leaf l, or take a position on leaf l; there may be none; Use as much of the 
        original text from opinion_text as possible; 

        v. plaintiff_chains = []; 
        vi. defendant_chains = []; 

        vii. def Recurse_argue(positions, party, chain): 
            1. If positions is empty:; 

                a. return; 
            2. For position p in positions: 

                a. refutations = {/}, support = {}; 
                b. Set refutations to be the set of all argument(s) or refutation(s) made by 

                the party’s opponent directly against position p; Use as much of the 
                original text from opinion_text as possible; 

                c. Set support to be the set of all supporting argument(s) or evidence(s) 
                presented by the party directly supporting position p; Use as much of the 
                original text from opinion_text as possible; 

                d. If refutations is not empty: 
                    i. Add  tuple (p, “refutations”, refutations) to chain; 

                e. If support is not empty: 
                    i. Add  tuple (p, “support”, support) to chain; 

                f. Set opposing_party to defendant if party is plaintiff; set opposing party 
                to plaintiff if party is defendant; 

                g. Recurse_argue(support, party, chain); 
                h. Recurse_argue(refutations, opposing_party, chain); 

        viii. Recurse_argue(plaintiff_positions, plaintiff, plaintiff_chains); 
        ix. Recurse_argue(defendant_positions, defendant, defendant_chains); 
        x. Set debates[leaf][“plaintiff”] = plaintiff_chains if plaintiff_chains is not empty; else don’t 

        add the key to debates[leaf]; 
        xi. Set debates[leaf][“defendant”] = defendant_chains if defendant_chains is not empty; else 

        don’t add the key to debates[leaf]; 
        xii. Return debates; 
"""

part_4 = """
Using the result of evaluating  debates = Crossfire(leaves) from your previous response as debates, evaluate the results
 of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly as instructed, 
 and give the fully evaluated interpretation_disputes dictionary in the format:  $interpretation_disputes = Type_dispute(debates)$  
 in the indicated return variable type (dict, list, etc.) in the function. Do not skip any steps or components of the input/output, 
 despite the length and complexity of the task, and show your reasoning/justification for obtaining the resulting interpretation_disputes dictionary. There may be multiple 'disputed_word's, or none. 
These are the functions to evaluate: 
 
$interpretation_disputes = Type_dispute(debates)$ 
 
Type_dispute(debates):  

    1. Define a Locus as a segment of word(s) that are either: {a single word (example: discuss)} OR {single 
    grammatical phrase (noun phrase, verb phrase, adjective phrase, etc.) (example: “has been eaten”)} ; OR  
    {a single dependent clause (example: “When the dog barked loudly”}; 

    2. Define contract as: a legally binding, agreement between two parties, enforceable by law; if 
    the word or phrase is a word or phrase that is directly quoted from a contract, as defined; 

    3. Disputes = {} 
    4. For each leaf, positions in debates.items(): Using the definitions of ‘Locus’ and ‘contract’ provided: 

        a. Referencing leaf and all components of positions: 
            i. Identify the set of all disagreement(s), or issue(s), between the plaintiff and defendant that 

            satisfy the requirement of being about: 
                1. “the interpretation/definition of a Locus in a given contract between the 

                defendant and the plaintiff”; OR 
                2. “whether a Locus in a contract between the defendant and the plaintiff is 

                ambiguous and subject to interpretation”; OR 
                3.  “what standards should be applied to interpreting a Locus in a contract between 

                the defendant and the plaintiff”; OR 
                4. “whether two parts of a contract contradict each other with respect to the 

                definition/interpretation of a Locus in the contract”

            where Locus must satisfy the definition given in 1., and contract must satisfy the definition given in 2.

            ii. And assign this set to the variable all_disputes;  

            iii. For dispute in all_disputes: 
                1. set argument_type to the requirement that dispute satisfies (ex. If it satisfies “the 
                interpretation/definition of a Locus in a given contract between the defendant 
                and the plaintiff”, then  argument_type = “the interpretation/definition of a 
                Locus in a given contract between the defendant and the plaintiff”); 

                2. referencing all components of positions:  
                3. set plaintiff_argument to the argument regarding argument_type that the plaintiff 

                makes about the Locus that dispute is about; 
                    a. If argument_type == “the interpretation/definition of a phrase or word 

                    in a given contract between the defendant and the plaintiff”: then the 
                    plaintiff_argument must be an explicit definition or interpretation of the  
                    phrase or word in dispute) 

                4. set defendant_argument to the argument regarding argument_type that the 
                defendant makes about the word or phrase dispute is about; 

                    a. If argument_type == “the interpretation/definition of a phrase or word 
                    in a given contract between the defendant and the plaintiff”: then the 
                    defendant_argument must be an explicit definition or interpretation of 
                    the  phrase or word in dispute 

                5. set disputed_word to the Locus that defendant_argument and 
                plaintiff_argument assert (their respective opinion on) argument_type; this 

                should be the specific Locus that is disputed, not the sentence or larger 
                clause that the Locus belongs to.; 

                6. disputed_word must be (a Locus that is present, word for word, in a 
                contract between the plaintiff and defendant) AND (must satisfy the definition given in 1. of a Locus); else: continue;

                7. set  court_opinion to the side that the court opinion takes dispute (“plaintiff” or 
                “defendant”);  

                8. If the court does not directly discuss, or mention its stance on argument_type 
                regarding Locus: continue (without adding the key disputed_word to 
                Disputes); 

                9. Set contract_excerpt to the contract clause or sentence within the contract that 
                Locus belongs to; 

                10. Set: 
                    a. Disputes[disputed_word][“Argument Type”] = argument_type; 
                    b. Disputes[disputed_word][“Plaintiff”] = plaintiff_argument; 
                    c. Disputes[disputed_word][“Defendant”] = defendant_argument; 
                    d. Disputes[disputed_word][“Court Opinion”] = court_opinion; 
                    e. Disputes[disputed_word][“Excerpt”] = contract_excerpt; 

        5. return Disputes; 
"""
