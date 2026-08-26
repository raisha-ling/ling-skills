---
name: write-grammar-culture-notes
description: "Analyzes a language-learning unit from an uploaded spreadsheet and creates one beginner-friendly Grammar Note and one relevant Culture Note. Use when a spreadsheet, CSV, XLSX, or unit table contains vocabulary, example sentences, dialogues, translations, transliterations, or lesson content that should be turned into concise textbook-style grammar and culture explanations."
---

# Writing Grammar & Culture Notes

## About

- **Privilege level:** draft-only — reads a spreadsheet you supply and produces draft notes for a human to review and edit before they reach learners. It writes nothing back to the sheet and publishes nothing.
- **Tools needed:** a spreadsheet reader (`.xlsx`, `.xls`, `.csv`). Document export and ZIP packaging only if you want the packaged output described under "Output"; otherwise the notes can be delivered as plain text in the conversation.
- **Where it runs:** any unit of language-course content that carries vocabulary, example sentences or dialogue.

Use this skill when the user provides a language-learning spreadsheet or unit content and wants a Grammar Note (GN) and Culture Note (CN) for each unit.

## Core objective

For each requested unit:

1. Read the entire unit before deciding on a topic.
2. Identify **one grammar topic** that is genuinely demonstrated by the unit content.
3. Write a clear, beginner-friendly Grammar Note using examples from that unit.
4. Identify **one cultural topic** naturally connected to the unit's vocabulary, sentences, dialogue, setting, communicative goal, or everyday context.
5. Write a concise Culture Note that explains the custom, convention, habit, etiquette, or real-life context accurately and neutrally.

The notes should feel like material from a modern beginner language textbook: simple enough for an A1 learner, but precise enough to be educational.

## Step 1: Understand the spreadsheet

Inspect the relevant sheet and determine how the unit is organized. Columns may include items such as:

- Unit / Lesson
- Sound ID
- Word or phrase
- Translation
- Transliteration / pronunciation
- Example sentence
- Dialogue
- Speaker
- Revised translation
- Grammar frame
- Notes

Column names may differ. Infer their roles from the data rather than requiring exact headers.

Before writing anything, collect all content belonging to the requested unit, including vocabulary, example sentences, and dialogues.

If Sound IDs or another ID system encode unit/lesson relationships, use them to connect vocabulary with its example sentence and dialogue where useful.

Prefer revised/final content over an earlier draft when both are present.

## Step 2: Choose the Grammar Note topic

Choose **one** grammar topic only.

The best topic is the rule or pattern that:

- appears clearly in the unit;
- is useful for a beginner;
- can be demonstrated with multiple examples from the unit when possible;
- matches the unit's learning stage;
- does not require teaching several unrelated advanced concepts first.

Good topics include, depending on the target language:

- basic word order;
- noun + adjective order;
- adjective agreement;
- pronouns;
- possessives;
- present-tense verb forms;
- negation;
- question formation;
- demonstratives;
- classifiers;
- articles;
- plural formation;
- basic case usage;
- common particles;
- politeness markers;
- basic prepositions/postpositions;
- a recurring sentence construction.

### Topic-selection priority

Use this order when several topics are possible:

1. A new or especially prominent structure in the unit.
2. A structure repeated across several words/sentences/dialogue lines.
3. A foundational rule that helps learners understand several examples at once.
4. A useful reinforcement topic if the unit does not introduce a clearly new structure.

Do **not** choose a grammar topic merely because it exists somewhere in the unit if it is peripheral.

Do **not** manufacture a grammar progression that is not supported by the sheet.

Do **not** teach an advanced exception unless it is necessary to understand the examples.

If the unit contains too little evidence for a confident grammar topic, state that briefly and choose the strongest observable pattern rather than inventing one.

## Step 3: Write the Grammar Note

Write for an English-speaking beginner unless the user specifies another learner language.

### Required structure

Use this structure unless the user provides a different template:

# [Grammar topic]

A short introductory paragraph explaining the rule in plain English.

## How it works

Explain the pattern in a simple textbook style. Use short paragraphs and, where useful, a compact table.

## Examples

Use examples from the unit. For each example, include:

- target-language form;
- pronunciation/transliteration if the sheet provides one and it is useful;
- natural English translation;
- literal translation only when it genuinely helps explain the grammar.

## Beginner Notes

End with 2–4 short takeaways that summarize what the learner should remember.

### Grammar writing rules

- Base the explanation on the unit's actual examples.
- Reuse the same vocabulary and forms learners have already encountered.
- Preserve the spelling/script used in the approved or revised content.
- Do not silently rewrite target-language examples just to fit the explanation.
- If an example appears incorrect or conflicts with the proposed rule, flag it instead of building the rule around it.
- Explain terminology when needed; avoid unnecessary linguistic jargon.
- Prefer “In [language]…” and concrete descriptions over abstract theory.
- Contrast with English only when the comparison makes the rule easier to understand.
- Do not imply that a tendency is an absolute rule if exceptions are common.
- Keep the scope narrow. One note = one central grammar idea.
- Do not add exercises unless requested.

## Step 4: Choose the Culture Note topic

Choose **one** cultural topic that has a real connection to the unit.

Look first for topics suggested by:

- greetings and forms of address;
- family relationships;
- food and drink;
- restaurants and cafés;
- shopping and markets;
- money and tipping;
- transport;
- homes and visiting etiquette;
- work or study culture;
- holidays or celebrations;
- socializing;
- age and hierarchy;
- politeness;
- gestures and body language;
- clothing;
- daily schedules;
- local institutions or services;
- culturally specific vocabulary appearing in the unit.

### Culture-topic selection rules

The topic should help a learner understand how the language may be used in real life.

Prefer practical cultural context over trivia.

Avoid broad stereotypes such as “people in X are very friendly” or “X culture is collectivist.” Describe observable conventions and acknowledge variation where appropriate.

Do not force a country-wide custom if the language is spoken across several countries or regions. Specify the relevant country, region, community, or context when necessary.

Do not present a religious, regional, generational, or family-specific practice as universal.

If the unit has no strong cultural hook, choose a modest everyday topic closely related to its communicative theme instead of inventing a dramatic cultural fact.

## Step 5: Write the Culture Note

### Required structure

# [Culture topic]

Write 2–4 concise paragraphs explaining the custom, convention, or real-life context.

When useful, add:

## Good to know

Include 2–4 short practical points for a learner.

### Culture writing rules

- Keep the tone informative, practical, and neutral.
- Explain what a visitor or learner is likely to encounter.
- Connect the topic back to vocabulary or situations in the unit where natural.
- Distinguish between common practice and strict rule.
- Mention regional or generational variation when it materially affects accuracy.
- Avoid tourist-guide clichés and unsupported claims.
- Never invent statistics, legal rules, historical facts, or etiquette conventions.
- If accuracy depends on a current or location-specific fact and reliable verification is not available, mark it as needing verification rather than guessing.
- Do not turn the Culture Note into another language/grammar lesson.

## Output quality check

Before finalizing each unit, verify:

### Grammar Note

- Is the topic clearly evidenced in the unit?
- Is it appropriate for the learner level?
- Does the note explain one central rule rather than several unrelated rules?
- Are the examples taken from the unit wherever possible?
- Are examples and translations internally consistent?
- Is the explanation simple but technically accurate?
- Does the Beginner Notes section accurately summarize the rule?

### Culture Note

- Is the topic relevant to the unit?
- Is it useful to someone learning the language?
- Is it culturally specific without stereotyping?
- Are claims phrased with appropriate nuance?
- Have uncertain claims been avoided or flagged?

## Output format for multiple units

When the user requests several units, process them one at a time and clearly separate them:

# Unit 3

## Grammar Note
[complete note]

## Culture Note
[complete note]

# Unit 4

## Grammar Note
[complete note]

## Culture Note
[complete note]

Do not use the same Grammar Note or Culture Note topic repeatedly across adjacent units unless repetition is pedagogically justified by the content.

## When the user provides an existing style/template

If the user supplies previous Grammar Notes, Culture Notes, formatting guidelines, or a reference document, treat those as the primary style reference.

Match their:

- approximate length;
- headings;
- use of tables;
- terminology;
- transliteration treatment;
- translation style;
- capitalization and punctuation;
- tone and learner level.

Content accuracy and unit relevance still take priority over mechanically copying a reference.

## Final behavior

Do not ask the user to choose the grammar or culture topic unless they explicitly want to choose it themselves. Topic selection is part of this skill.

When the evidence strongly favors a topic, select it and proceed.

If two topics are equally strong, choose the one that gives the learner more explanatory value using the unit's own examples.

Output should look like this:
.Zip file with two folders: Culture Notes; Grammar Notes; each unit separately in .docs file
## Definition of done

Pass conditions, all checkable without arguing:

1. Exactly one Grammar Note and one Culture Note per requested unit. Never two of either, never the two merged into one.
2. Every target-language example in the Grammar Note appears verbatim in that unit's rows, in the script and spelling the sheet uses. Zero invented examples.
3. The Grammar Note carries the required headings: a topic heading, "How it works", "Examples", and "Beginner Notes" with 2–4 takeaways.
4. The Culture Note is 2–4 paragraphs, names the country, region or community when the language is spoken across several, and contains no invented statistic, legal rule or historical fact.
5. Across adjacent units, no Grammar Note or Culture Note topic repeats unless the unit content justifies the repetition.

**Golden example.**

Input: Unit 3 of a Nepali sheet containing घर ("house"), यो मेरो घर हो। ("This is my house.") and कार ("car").

Accepted output: a Grammar Note titled "Saying 'my' with मेरो" — a short plain-English intro, a "How it works" section showing possessive + noun + हो, an "Examples" section built only from unit 3's own rows with transliteration and natural English translation, and 3 Beginner Notes. Alongside it, a Culture Note on what a visitor meets in a Nepali home — shoes left at the door, tea offered on arrival — in 3 paragraphs plus a "Good to know" list, tied back to घर, with regional and generational variation acknowledged rather than stated as universal.

**Adversarial case.**

A unit that is a bare vocabulary list: 12 nouns, no example sentences, no dialogue, no repeated structure. There is no grammar evidence to build a rule on.

The skill must not manufacture a grammar progression or teach a rule the unit never demonstrates, and must not import examples from outside the unit to prop one up. It states briefly that the unit carries too little evidence for a confident grammar topic, writes the note around the strongest pattern actually observable in the rows, and flags the thinness for the editor instead of padding it out.
