"""v1 - single-prompt extraction.

One long instruction that defines Contract, Locus and argument categories A-E,
and asks for the full JSON array of arguments in a single call.

Used by: versions/gpt_unbatched.py
"""

context1 = """1. Identify and define Contract to be the legal definition given in the opinion_text; If it is not explicitly provided, a document should be considered a contract
   if the court in the opinion_text deems the document as legally binding.

   2. Define a Locus as (a segment of word(s) that are either: {a single word (example: discuss)} OR {single
   grammatical phrase (noun phrase, verb phrase, adjective phrase, etc.) (example: “has been eaten”)} ; OR 
   {a single dependent clause (example: “When the dog barked loudly”};) AND (is not a full sentence, or several sentences) AND (is not the title of an entire clause in a Contract) 

3. Identify all arguments made that fit into one of the following categories in the opinion_text:        
       
    A= "an assertion/argument that seeks to promote a specific interpretation of contractual language, rather than trying to establish the rules that should govern the interpretation"; OR
    B= "an assertion/argument about whether or not there exists ambiguity in the existing contractual language"; OR
    C= "an assertion/argument that seeks to establish the rule that should govern the interpretation of contractual language, rather than an assertion/argument that promotes a specific interpretation of the contractual language"; OR
    D= “an assertion/argument that a Locus in a Contract should be interpreted/defined a certain way in order to avoid inconsistencies with other parts of the contract, other contracts between the parties, statutes or the like."
    E= "an assertion/argument regarding the interpretation of contractual language or a Locus in a Contract, but does not fit into any of the categories specified above (A, B, C or D)."

Return all of these arguments in JSON format with the following structure for each <argument>:
{
    "citation": <citation>,
    "disputed_word": <disputed_word>,
    "argument_position": <argument_position>,
    "argument_type": <argument_type>,
    "argument": <argument>,
    "argument_excerpts": <argument_excerpts>,
    "contract_excerpt": <contract_excerpt>
}

Return an array of these JSON objects,

Where:
citation is the given citation for the opinion_text (example of citation: 331 F.Supp.3d 263);
disputed_word (a Locus that is present, word for word, in a  contract between the plaintiff and defendant) AND (must satisfy the definition given in 1. of a Locus) AND (the document that locus belongs to must satisfy the definition given in 2. of a Contract); 
disputed_word should be the specific Locus that is disputed, not the sentence or larger clause that the Locus belongs to.; 
(example of disputed_word: "retirement");
argument_position is either of plaintiff, defendant, or court (example of argument_position: "plaintiff");
argument_type is the type of argument; if the type of argument is either category A, B, C, or D, then argument_type should be "A", "B", "C", or "D"; 
However, if it is of type E, argument_type should be a description akin to the definitions specified above for category A, B, C, and D, specifying exactly what kind of argument regarding the interpretation of contractual language or a Locus in a Contract it is; 
argument is the argument made by argument_position regarding disputed_word of category argument_type;
argument_excerpts should be all of the excerpts from the opinion_text in which the argument is made, combined into a single string; 
contract_excerpt should be the contract clause or sentence within the contract that Locus belongs to; (example of contract_excerpt: “Plaintiffs argue that under the 1997 Plan, participants are eligible for deferred compensation if they retire from any employment at or after age sixty-five, based on the Plan's definition of 'retirement' as 'withdrawal from full time active employment at or after age 65.”);


The same locus may be used in multiple tuples. 
The same argument_position (plaintiff, defendant, court) may make multiple arguments within one opinion_text, that may or may not be of different argument_type.
In this case, return each argument individually, without omitting any arguments made by each position.
If there are no such arguments, return an empty array.
opinion_text: 
"""

context2 = """1. Identify and define Contract to be the legal definition given in the opinion_text; If it is not explicitly provided, a document should be considered a contract
   if the court in the opinion_text deems the document as legally binding.

   2. Define a Locus as (a segment of word(s) that are either: {a single word (example: discuss)} OR {single
   grammatical phrase (noun phrase, verb phrase, adjective phrase, etc.) (example: “has been eaten”)} ; OR 
   {a single dependent clause (example: “When the dog barked loudly”};) AND (is not a full sentence, or several sentences) AND (is not the title of an entire clause in a Contract) 

3. Identify all arguments made that fit into one of the following categories in the opinion_text:        
       
    A= "an assertion/argument that seeks to promote a specific interpretation of contractual language, rather than trying to establish the rules that should govern the interpretation"; OR
    B= "an assertion/argument about whether or not there exists ambiguity in the existing contractual language"; OR
    C= "an assertion/argument that seeks to establish the rule that should govern the interpretation of contractual language, rather than an assertion/argument that promotes a specific interpretation of the contractual language"; OR
    D= “an assertion/argument that a Locus in a Contract should be interpreted/defined a certain way in order to avoid inconsistencies with other parts of the contract, other contracts between the parties, statutes or the like."

Return all of these arguments in JSON format with the following structure for each <argument>:
{
    "citation": <citation>,
    "disputed_word": <disputed_word>,
    "argument_position": <argument_position>,
    "argument_type": <argument_type>,
    "argument": <argument>,
    "argument_excerpts": <argument_excerpts>,
    "contract_excerpt": <contract_excerpt>
}

Return an array of these JSON objects,

Where:
citation is the given citation for the opinion_text (example of citation: 331 F.Supp.3d 263);
disputed_word (a Locus that is present, word for word, in a  contract between the plaintiff and defendant) AND (must satisfy the definition given in 1. of a Locus) AND (the document that locus belongs to must satisfy the definition given in 2. of a Contract); 
disputed_word should be the specific Locus that is disputed, not the sentence or larger clause that the Locus belongs to.; 
(example of disputed_word: "retirement");
argument_position is either of plaintiff, defendant, or court (example of argument_position: "plaintiff");
argument_type is the type of argument (should be "A", "B", "C", or "D");
argument is the argument made by argument_position regarding disputed_word of category argument_type;
argument_excerpts should be all of the excerpts from the opinion_text in which the argument is made, combined into a single string; 
contract_excerpt should be the contract clause or sentence within the contract that Locus belongs to; (example of contract_excerpt: “Plaintiffs argue that under the 1997 Plan, participants are eligible for deferred compensation if they retire from any employment at or after age sixty-five, based on the Plan's definition of 'retirement' as 'withdrawal from full time active employment at or after age 65.”);


The same locus may be used in multiple tuples. 
The same argument_position (plaintiff, defendant, court) may make multiple arguments within one opinion_text, that may or may not be of different argument_type.
In this case, return each argument individually, without omitting any arguments made by each position.
If there are no such arguments, return an empty array.
opinion_text: 
"""
