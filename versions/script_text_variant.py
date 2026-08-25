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
Using the result of evaluating issues from your previous response, with issues_dict = issues, 
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
    1. Identify and define Contract to be the legal definition given in the opinion_text; If it is not explicitly provided, a document should be considered a contract
    if the court in the opinion_text deems the document as legally binding.

    2. Define a Locus as (a segment of word(s) that are either: {a single word (example: discuss)} OR {single 
    grammatical phrase (noun phrase, verb phrase, adjective phrase, etc.) (example: “has been eaten”)} ; OR  
    {a single dependent clause (example: “When the dog barked loudly”};) AND (is not a full sentence, or several sentences) AND (is not the title of an entire clause in a Contract)  

        i. If issues is empty: return; 
        iii. Else for each issue i in issues: 
            1. if (issue is regarding
                A. “the interpretation/definition of a Locus in a given Contract between the 

                defendant and the plaintiff”; OR 
                B. “whether a Locus in a Contract between the defendant and the plaintiff is 

                ambiguous and subject to interpretation”; OR 
                C.  “what (legal) standards or clauses should be applied to interpreting a Locus in a Contract between 

                the defendant and the plaintiff”; OR 
                D. “the interpretation/definition of a Locus in a Contract based on a specific part of/clause in Contract.”

                ,where Locus must satisfy the definition given in 1., and Contract must satisfy the definition given in 2,
            ) {
            then add issue i to leaves;
            }
            2. sub_issues = {\}; 

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
#part 3 change to "and make sure to show all of your steps in obtaining...""
part_3 = """
Using the result of evaluating updated_issues_dict, leaves from your previous response, with leaves, 
evaluate the results of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly as 
instructed, and give the fully evaluated and expanded output in the format:  ‘[RESPONSE] (python) debates = Crossfire(leaves) [END RESPONSE]’ ; 
where debates should be a variable representing a valid nested python dictionary of strings, fully expanded for each leaf in leaves and each 
recursive call to Recurse_argue. Do not skip any steps or components of the input/output, despite the length and complexity of the task 
(do not skip any leaves, or the fleshing out of any leaves; do not skip any recursive calls, or any ‘positions’ within the call). Do not include anything else in your 
response other than the fully evaluated output in the requested format.
These are the functions to evaluate: 

4. Crossfire(leaves):  
    
    a. debates = {/}; 
    
    b. 
    1. Identify and define Contract to be the legal definition given in the opinion_text; If it is not explicitly provided, a document should be considered a contract
    if the court in the opinion_text deems the document as legally binding.

    2. Define a Locus as (a segment of word(s) that are either: {a single word (example: discuss)} OR {single 
    grammatical phrase (noun phrase, verb phrase, adjective phrase, etc.) (example: “has been eaten”)} ; OR  
    {a single dependent clause (example: “When the dog barked loudly”};) AND (is not a full sentence, or several sentences) AND (is not the title of an entire clause in a Contract)  

    for each leaf l in leaves: 

        1. if leaf is regarding ( 
            A = “the interpretation/definition of a Locus in a given Contract between the 

            defendant and the plaintiff”; OR 
            B = “whether a Locus in a Contract between the defendant and the plaintiff is 

            ambiguous and subject to interpretation”; OR 
            C = “what (legal) standards or clauses should be applied to interpreting a Locus in a Contract between 

            the defendant and the plaintiff”; OR 
            D = “the interpretation/definition of a Locus in a Contract based on a specific part of/clause in Contract.”

            where Locus must satisfy the definition given in 1., and Contract must satisfy the definition given in 2.
        ) {
            then: 
            set arg_type to the string literal corresponding to either of A, B, C, or D, depending on which option leaf corresponds to; 
            plaintiff_argument = None;
            defendant_argument = None;
            referencing leaf and opinion_text:
                for [pos, pos_arg] in [["plaintiff", platiff_argument], ["defendant", defendant_argument]]:
                find and set pos_arg to the position pos takes on leaf, and is: 
                        a. If argument_type == A.: an explicit definition or interpretation of the Locus in the Contract;
                        b. if argument_type == B.: an assertion/argument that either (the language of Locus in the Contract is ambiguous and subject to interpretation) or that (the language of Locus in the contract is not ambiguous and does not leave room for interpretation);
                        c. if argument_type == C.: an assertion/argument that a specific legal standard or legal clause should be applied in interpreting Locus; 
                        d. if argument_type == D.: an assertion/argument that Locus should be intepreted/defined based on a specific part of/clause in the contract.;
                where Locus must satisfy the definition given in 1., and Contract must satisfy the definition given in 2.
            set debates["plaintiff_chains"] = (plaintiff_argument, "refutations", {defendant_argument})
            continue;
        }

        i. plaintiff_positions; 
        ii. defendant_positions; 

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
Using the result of evaluating  debates from your previous response as debates, evaluate the results
 of the functions below for the given opinion_text, performing all the detailed steps in the functions exactly as instructed, 
 and give the fully evaluated interpretation_disputes dictionary in the format:  $interpretation_disputes = Type_dispute(debates)$  
 in the indicated return variable type (dict, list, etc.) in the function. Do not skip any steps or components of the input/output, 
 despite the length and complexity of the task and make sure to show all of your steps in obtaining interpretation_disputes. There may be multiple 'disputed_word's, or none. 
These are the functions to evaluate: 
 
Type_dispute(debates):  

    1. Identify and define Contract to be the legal definition given in the opinion_text; If it is not explicitly provided, a document should be considered a contract
    if the court in the opinion_text deems the document as legally binding.

    2. Define a Locus as (a segment of word(s) that are either: {a single word (example: discuss)} OR {single 
    grammatical phrase (noun phrase, verb phrase, adjective phrase, etc.) (example: “has been eaten”)} ; OR  
    {a single dependent clause (example: “When the dog barked loudly”};) AND (is not a full sentence, or several sentences) AND (is not the title of an entire clause in a Contract)  

    3. Disputes = {} 

    4. For each leaf, positions in debates.items(): Using the definitions of ‘Locus’ and ‘Contract’ provided: 
        b. for position: args in positions.items():
            for each tuple in args:
            
            i. Using leaf as context, identify whether the first or third element of the tuple:
                A= "is an assertion made/opinion an explicit definition or interpretation of a Locus in a Contract"; OR 
                B= "an assertion/argument that either (the language of Locus in a Contract is ambiguous and subject to interpretation) or that (the language of a Locus in a Contract is not ambiguous and does not leave room for interpretation)"; OR 
                C= "an assertion/argument that a specific legal standard or legal clause should be applied in interpreting a Locus in a Contract"; OR 
                D= “an assertion/argument that a Locus in a Contract should be intepreted/defined based on a specific part of/clause in the Contract."

            where Locus must satisfy the definition given in 1., and Contract must satisfy the definition given in 2.
            If the tuple does satisfy A, B, C, or D:
                argument_type = ""
                1. set argument_type to the string literal corresponding to either of A, B, C, or D, depending requirement that element of the tuple satisfies; 

                opponent_position = None;
                position_argument = None
                2.  if (position == "plaintiff") {
                        set opponent_position = "defendant"
                    
                    } else {
                        set opponent_position = "plaintiff";
                    }
                    set position_argument = tuple[0]
                    if (both the tuple[0] and tuple[2] are an assertion made regarding argument_type) {
                        if (tuple[1] == "refutations") {
                                set opponent_position = tuple[2];
                                continue to step 5.;
                        } else {
                                position_argument += tuple[2];
                        }
                    } 

                opponent_argument = ""

                3. referencing the contention of leaf, and all of the tuple args in both positions (debates[leaf]), that tuple belongs to, and opinion_text,
                find and set opponent_argument to the argument/refutation/engagment opponent_position makes regarding argument_type against position's position_argument, and satisfies: 
                    a. If argument_type == A.: then opponent_argument should be an explicit definition or interpretation of the  
                    Locus in dispute
                    b. if argument_type == B.: then opponent_argument 
                    must argue that either (the language of Locus in the contract is ambiguous and subject to interpretation) or that (the language of Locus in the contract is not ambiguous and does not leave room for interpretation);
                    c. if argument_type == C.: then opponent_argument must argue that a specific legal standard or legal clause should be applied in interpreting Locus, which is different from the legal standard argued for by position; 
                    d. if argument_type == D.: then opponent_argument must argue that Locus should be intepreted/defined based on a specific part of/clause in the contract. 
                5. set disputed_word to the Locus that opponent_argument and 
                position_argument assert (their respective opinion on) argument_type; this 
                should be the specific Locus that is disputed, not the sentence or larger 
                clause that the Locus belongs to.; 

                6. disputed_word must be (a Locus that is present, word for word, in a 
                contract between the plaintiff and defendant) AND (must satisfy the definition given in 1. of a Locus) AND (the document that locus belongs to must satifsy the definition given in 2. of a Contract); 
                else: continue;

                7. set  court_opinion to the side that the court opinion takes dispute (“plaintiff” or 
                “defendant”);  

                8. If the court does not directly discuss or mention argument_type 
                regarding Locus: continue (without adding the key disputed_word to 
                Disputes); 

                9. Set contract_excerpt to the contract clause or sentence within the contract that 
                Locus belongs to; 

                10. Set: 
                    a. Disputes[disputed_word][“Argument Type”] = argument_type; 
                    b. Disputes[disputed_word][position] = position_argument; 
                    c. Disputes[disputed_word][opponent_position] = opponent_argument; 
                    d. Disputes[disputed_word][“Court Opinion”] = court_opinion; 
                    e. Disputes[disputed_word][“Excerpt”] = contract_excerpt; 

        5. return Disputes; 
"""
