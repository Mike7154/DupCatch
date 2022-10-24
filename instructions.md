# Instructions for running DupCatch

Information:

This tool has two functions, the first is to find similar cards within
the deck sorted by most similar pairs. The second is to automatically
merge fields, merge tags, or tag them as 'covered by' another deck (see
below). If you have any trouble, feel free to open an issue on GitHub or
email me m6611022\@gmail.com

Pre-requisites

-   Must have Python installed on the computer

-   Must have the required python libraries

    -   pip install -r requirements.txt

## Finding Duplicates

1.  Export an Anki package file into the folder
    DupCatch/anki_collection.

2.  Edit the settings file (at least edit the Duplicates section at the
    top of settings.yml) (see settings below)

3.  Run the duplicates with python dupcatch.py -r

    a.  Logs will be sent to DupCatch/bin/logs.txt

    b.  If you have any errors, open an issue on github and include
        settings.yml data and logs.txt data.

    c.  When complete, this will create a new Anki package file in the
        same folder in step 1 with '\_dupes_tagged' appended.

    d.  The resulting file will only include notes that were tagged as
        duplicates and not all of the notes that were checked.

    e.  Notes will be tagged with \~DupCatch_V2. Notes will be tagged as
        pairs. The tag will include something like 001:95. This means
        that it is the first most similar pair with a similarity score
        of 95 (scoring from 0 -- 100)

4.  Import the deck into Anki for review. You can now merge fields,
    tags, or mark them as non-duplicates or covered by deck (see Merge
    below)

    a.  I recommend using the Special Fields addon and protecting all
        fields (ie. Import tags setting)

    b.  It is a good idea to backup your collection before importing
        this deck into it.

## Merge

1.  After a duplicates run, you can tag one or both note pairs to
    designate which notes should be combined.

    a.  Adding a ::merge tag suffix

        i.  If two notes are tagged with the same DupCatch tag (ie.
            \[\~DupCatch_V2::D2022-10-22_00:26::001.100\]), adding a
            "::merge" to one of the tags will that note to receive [both
            fields and tags]{.ul} from the other note with the same tag.

    b.  Adding a ::mfields tag suffix

        i.  The same as the previous except the note with ::mfields
            added will receive fields (and not tags) from the other note
            with the same tag. Fields included in the fields_to_ignore
            setting will not be merged. (i.e.. A note with
            \~DupCatch_V2::D2022-10-22_00:26::001.100::mfields will
            fields from any note tagged with
            \~DupCatch_V2::D2022-10-22_00:26::001.100)

    c.  Adding a ::mtags tag suffix

        i.  Same as the previous two except the note will receive tags
            only. Tags included in tags_to_ignore will not be included
            in the merge

    d.  Adding a ::cb tag suffix

        i.  If two notes are tagged with the same DupCatch tag. Adding
            this tag to either of the notes will cause both of the notes
            to receive a tag (!Covered_By::Other deck).

        ii. For example, if there are two notes that both have the tag
            \[\~DupCatch_V2::D2022-10-22_00:26::001.100\], and note1 is
            in deck "Deck1" and note2 is in deck "Deck2::subdeck". If
            you add the tag
            \[\~DupCatch_V2::D2022-10-22_00:26::001.100::cb\] to either
            note1 or note2, Note 1 will receive the tag
            \[!Covered_By::deck2::subdeck\] and Note2 will receive the
            tag \[!Covered_By::Deck1\]

        iii. The value of this is users that have both decks can quickly
             identify which cards are already overed by the other deck
             that they already use.

    e.  Adding a ::nd tag suffix.

        i.  If two notes are tagged with the same DupCatch tag, adding
            this tag to either of the notes will cause the tool to
            remember them as non-duplicates and not include them in
            future Duplicates runs. This information is saved in
            bin/non_dupes.json

2.  Edit the settings.yml file under the Merge section (see settings
    below)

3.  Export the deck again with DupCatch tags included into the folder
    DupCatch/anki_collection

4.  Run the duplicates with *python dupcatch.py -m*

    a.  You can send me any errors through github and I will help you
        figure it out. Please include the settings.yml information and
        the logs file so I can try to reproduce the error.

    b.  The tool will export a new Anki package file into the folder
        from Step 3.

    c.  The new deck will only include notes that were changed or tagged
        and not all the other notes. Notes with only ::nd tags were not
        changed and will not be included in the exported file

5.  Open in Anki and review the changes. All items that were changed
    will be tagged with \~DupCatch tags to be reviewed easily.

    a.  I recommend backing up your anki collection in case anything
        weird happens so you can revert if needed. Or open in a new
        profile to review.

## Settings File

Settings are in YAML format, which was designed to be easy for human
input. [YAML File
Format](https://docs.fileformat.com/programming/yaml/). Note that while
quotes are usually not required for text, special characters need to be
in quotes or escaped. (ie. Quotes are required if the tag starts with \#
like in \#AK_Original_Decks)

### Duplicates -- run with python dupcatch.py -r

-   Fields_to_check: These are fields that should be compared for
    similarity (ie Text, Front and back, etc)

-   check_duplicates_tag: Look for duplicates in notes that have this
    tag

-   compare_to_tag: Compare notes to notes that have this tag. (can be
    the same as above if you want to find duplicates within a deck)

-   tags_to_skip: Don't compare notes if one of them have any of these
    tags. Note that the note must start with this tag. So to match
    '\#AK_Original_Decks' you must include all of the tag up to the end
    of the tag or up to a subtag (ie up to ::)

### Merge -- run with python dupcatch.py -m

-   **merge_tags**: If 'True' merge tags for note pairs that have either
    merge_suffix or merge_tags_suffix. This is uni-directional: The
    receiving note is the paired note that contains the suffix (i.e.. A
    note with \~DupCatch_V2::D2022-10-22_00:26::001.100::merge will
    receive tags from any note tagged with
    \~DupCatch_V2::D2022-10-22_00:26::001.100)

-   **merge**\_**fields**: If 'True', merge fields for note pairs that
    have either merge_suffix or merge_fields_suffix. Fields will go from
    the sender note to the receiver note. The receiving note is the one
    that contains the suffix at the end of the DupCatch tag (i.e.. A
    note with \~DupCatch_V2::D2022-10-22_00:26::001.100::merge will
    receive fields from any note tagged with
    \~DupCatch_V2::D2022-10-22_00:26::001.100)

-   **Tags_to_ignore:** tags to not merge when copying tags from one
    note to it's paired note

-   **Fields_to_ignore:** Fields to ignore when copying fields from the
    sender to receiver.

-   **Field_seperator:** When merging two fields, this will be added
    between the field content.

-   **Merge_suffix:** Notes with this added to the end of a tag will
    receive fields and tags from any note with the same tag (minus the
    merge_suffix) (i.e.. A note with
    \~DupCatch_V2::D2022-10-22_00:26::001.100::merge will receive tags
    and fields from any note tagged with
    \~DupCatch_V2::D2022-10-22_00:26::001.100)

-   **Merge_tags_suffix:** Notes with this added to the end of a tag
    will receive tags from any note with the same tag (minus the
    merge_tags_suffix). Works similar to merge_suffix without a field
    merge

-   **Merge_fields_suffix:** Notes with this added to the end of a tag
    will receive fields from any note with the same tag (minus the
    merge_fields_suffix). Works similar to merge_suffix without a tag
    merge

-   **map_missing_field:** When merging fields, the tool will attempt to
    find matching fields for any included fields (ie. 'Extra' -\>
    'Extra', 'Textbook' -\> 'Textbook'), but fields in the sender note
    that do not have a match will go to this field in the receiver note.
    (ie. 'Unique Field' -\> 'Additional Resources')

-   **covered_by_tag:** notes with the covered_by_suffix will be tagged
    with this tag with the deck of the paired note replacing (DECK).
    This is bidirectional. For example, if there are two notes that both
    have the tag \[\~DupCatch_V2::D2022-10-22_00:26::001.100\], and
    note1 is in deck "Deck1" and note2 is in deck "Deck2::subdeck". If
    you add the tag "\[\~DupCatch_V2::D2022-10-22_00:26::001.100::cb\]
    to either note1 or note2. Note 1 will receive the tag
    \[!Covered_By::deck2::subdeck\] and Note2 will receive the tag
    \[!Covered_By::Deck1\]

-   **covered_by_suffix:** text to use to denote covered_by (see above)

### Remember -- run with python dupcatch.py -m

-   **non_dupes_tag_suffix:** Suffix denotes that the note pair is not a
    duplicate and the note pair will note be scored in future runs. The
    information is stored in DupCatch/bin/non_dupes.json. This is
    bidirectional, so it doesn't matter which note in the pair has the
    tag. For example, if a note is tagged with
    \[\~DupCatch_V2::D2022-10-22_00:26::001.100::nd\] it will be
    remembered as not a duplicate of any card with the tag
    \[\~DupCatch_V2::D2022-10-22_00:26::001.100\]

### Scoring -- How scores are calculated in Duplicates runs

-   **close_multiplier:** words included in clozes will have their 'rare
    score' multiplied by this number

-   **emphasis_multiplier:** notes that are within a bold, underline, or
    italics HTML tag will have their scores multiplied by this number

-   **emphasis_pattern:** contains HTML tags that should be included in
    emphasis_multiplier. Default \[bui\] for \<b\> \<i\> and \<u\> tags.

-   **Score_cutoff:** Minimum score to include in the output

-   **Keep_top:** include the top n most similar pairs whether or not
    they meet eh score cutoff.

-   **Keep_top_absolute:** keep the top n note pairs that have the
    highest absolute score (before normalized to a 0-100 score) whether
    or not they meet the score cutoff.

-   **Keep_top_one_diection:** Keep the top n notes for each direction
    score whether or not they meet the score cutoff. IE, if note 1
    contains all of the words in note2, but note2 has a second fact or
    sentence that is not in note 1. The forward score will be high and
    the reverse score will be low, making the overall score \~50.
