"""Six fixed questions asked in sequence against a single opinion.

`context` is the law-student framing used for the Vertex AI chat session;
utils/assistants.py sends the same questions with no preamble.

Used by: utils/gemini_vertex.py, utils/assistants.py
"""

context = "You are a careful law student who is skilled at identifying logical structures within legal documents and uses step by step reasoning. The pasted text is the full text of the opinion of a court case about contract disputes. Please answer following questions about this case based on the opinion, and format answers as the number and question followed by the answer. Answers do not have to be in complete sentences."

question_1 = "1. A case that is a contract language interpretation dispute is one where the plaintiff and defendant assert different interpretations of a phrase or term in a contract or argue about whether a phrase or term in a contract is ambiguous and subject to interpretation. Based on this definition, is this case about language interpretation dispute? Answer '1' if it is a contract language interpretation dispute and '0' otherwise."
question_2 = "2. What's the specific word or phrase in the contract that the plaintiff and defendant dispute over? It may be the case that the term or phrase (we call this phrase A) is defined explicitly in the contract, so the dispute is over the interpretation of another term or phrase (we reference this as phrase B) within the part of the contract that defines phrase A. In this case, include only phrase B." 
question_3 = "3. What is the contract excerpt that the disputed phrase or term occurs in? If the answer to the previous question includes two or more terms or phrases, include contract excerpts relevant to both terms or phrases."
question_4 = "4. What's the plaintiff's interpretation of the disputed contract language that was the answer to question 2?"
question_5 = "5. What's the defendant's interpretation of the disputed contract language that was the answer to question 2?"
question_6 = "6. Who did the court side with, and why? Answer 'P' if plaintiff and 'D' if defendant."

question_list = [question_1, question_2, question_3, question_4, question_5, question_6]
