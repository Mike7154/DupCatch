import mlfiles
import re
from ankisync2 import AnkiDesktop
import numpy as np
from tqdm import tqdm
import pandas as pd
import mltext
import anki_functions
import datetime
from anki.collection import Collection


def word_rare_score(freq, leveling=10):
    return abs(np.log(1 / (freq * leveling)))


# for k in [1,2,3,4,5,6,7,8,9,25,100]:
#    for i in [.04, .01, .001, .0001, 2.705378834198153e-06]:
#        print(word_rare_score(i,k))

def initialize_database():
    mlfiles.clear_folder("bin/collection")
    temp = mlfiles.load_setting('Misc', 'template_col')
    mlfiles.copy_file(temp, 'bin/collection')
    col = Collection("bin/collection/collection.anki2")
    folder_name = "/" + mlfiles.load_setting("Misc", "folder")
    extension = mlfiles.load_setting("Misc", "extension")
    folder = mlfiles.get_current_dir(folder_name)
    file = mlfiles.find_file(folder, extension)
    mlfiles.update_log("Loading the anki file " + file)
    col.import_anki_package(file)
    col.close()
    return file


def build_word_df(notes_using,
                  fields):  # this returns a dataframe of all the words in selected notes with frequencies,
    # and weights (cloze, bolded, italics, etc)
    fields_to_check = mlfiles.load_setting("Duplicates", "fields_to_check")
    html_cleaner = mltext.compile_html_cleaner()
    cloze_cleaner = anki_functions.compile_cloze()
    cloze_cleaner1 = anki_functions.compile_cloze('[{]{2}c[0-9]+::(.*?[^ .,;][}]{2}[a-zA-Z-]+)')
    cloze_cleaner2 = anki_functions.compile_cloze('[{]{2}{c[0-9]+::(.*?)[}]{2}')
    cloze_cleaner3 = anki_functions.clean_clozes_patterns()
    tag_cleaner = mltext.compile_html_tag(mlfiles.load_setting('Scoring', 'emphasis_pattern'))
    cloze_compile = anki_functions.compile_cloze()
    emphasis_multiplier = mlfiles.load_setting("Scoring", "emphasis_multiplier")
    cloze_multiplier = mlfiles.load_setting("Scoring", "cloze_multiplier")
    synonym_dict = mltext.reverse_synonym_dict(mlfiles.load_all_settings()['Misc']['synonyms'], mltext.unicode_dict())
    pattern_1 = re.compile(r'[(.,!*#?)]')
    pattern_3 = re.compile('[^A-Za-z0-9]+')
    pattern_4 = re.compile('(?<=[A-Za-z])/(?=[A-Za-z])')
    mlfiles.print_log("Building Word Dataframe")
    unimportant_words = mlfiles.load_setting('Misc', 'unimportant_words')
    unimportant_words = mltext.lemm_sing(unimportant_words)
    list_of_dfs = []
    # For this, I take every word in the note and assign a rare score based on the frequency of that word.
    # The rarity scores are multiplied by 'importance weights'
    # Important words are words that are in a cloze, bolded, italicized or underlined
    for note in tqdm(notes_using):
        note_string = anki_functions.combine_fields(fields, note, fields_to_check)
        word_string = re.sub(pattern_4, " ", note_string)
        word_string = mltext.replace_patterns(word_string, synonym_dict)
        word_string = re.sub(pattern_1, " ", word_string)
        clozes = mltext.find_text(word_string, cloze_cleaner1)
        clozes = mltext.clean_patterns_words(clozes, cloze_cleaner3)
        word_string = mltext.clean_text(word_string, cloze_cleaner1)
        clozes.extend(mltext.find_text(word_string, cloze_cleaner))
        clozes = [mltext.clean_text(c, html_cleaner, "") for c in clozes]
        remaining_words = mltext.clean_text(word_string, cloze_cleaner2)
        emphasized_words = mltext.find_text(remaining_words, tag_cleaner)
        remaining_words = mltext.clean_text(remaining_words, tag_cleaner)
        remaining_words = mltext.clean_text(remaining_words, html_cleaner)
        remaining_words = mltext.clean_ws(remaining_words)
        remaining_words = remaining_words.split()
        clozed_words = mltext.split_list(clozes)
        emphasized_words = mltext.split_list(emphasized_words)
        remaining_words = mltext.clean_words(remaining_words, pattern_3)
        clozed_words = mltext.clean_words(clozed_words, pattern_3)
        emphasized_words = mltext.clean_words(emphasized_words, pattern_3)
        remaining_words = mltext.lemm_sing(remaining_words)
        clozed_words = mltext.lemm_sing(clozed_words)
        emphasized_words = mltext.lemm_sing(emphasized_words)
        df1 = pd.DataFrame({'nid': [note.id for i in range(len(emphasized_words))], 'word': emphasized_words,
                            'multiplier': [emphasis_multiplier for i in range(len(emphasized_words))],
                            'type': ["emphasis" for i in range(len(emphasized_words))]})
        df2 = pd.DataFrame({'nid': [note.id for i in range(len(clozed_words))], 'word': clozed_words,
                            'multiplier': [cloze_multiplier for i in range(len(clozed_words))],
                            'type': ["cloze" for i in range(len(clozed_words))]})
        df3 = pd.DataFrame({'nid': [note.id for i in range(len(remaining_words))], 'word': remaining_words,
                            'multiplier': [1 for i in range(len(remaining_words))],
                            'type': ['remaining' for i in range(len(remaining_words))]})
        list_of_dfs.extend([df1, df2, df3])
    mlfiles.print_log("Combining data frames")
    outdf = pd.concat(list_of_dfs, ignore_index=True)
    mlfiles.update_log("Removing the unimportant words: " + ", ".join(unimportant_words))
    outdf = outdf[~outdf['word'].isin(unimportant_words)]
    outdf['freq'] = outdf.groupby('word')['word'].transform('count') / len(outdf)
    min(outdf['freq'])
    max(outdf['freq'])
    outdf['rare_score'] = word_rare_score(outdf['freq'], mlfiles.load_setting("Scoring", "rare_leveling"))
    outdf['weighted_score'] = outdf['rare_score'] * outdf['multiplier']
    return outdf


def build_clean_dict(notes_using, fields):
    mlfiles.print_log("Building sentences dictionary")
    fields_to_check = mlfiles.load_setting("Duplicates", "fields_to_check")
    cloze_clean3 = anki_functions.clean_clozes_patterns()
    html_cleaner = mltext.compile_html_cleaner()
    spaces = re.compile(' +')
    dict = {}
    for note in tqdm(notes_using):
        note_string = anki_functions.combine_fields(fields, note, fields_to_check)
        clean_string = mltext.clean_patterns(note_string, cloze_clean3)
        clean_string = mltext.clean_text(clean_string, html_cleaner)
        clean_string = re.sub(spaces, " ", clean_string)
        clean_string = clean_string.strip()
        dict.update({note.id: clean_string})
    return dict


def score_matches(word_df, nids_1, nids_2):  # this scores the word pairs
    worddf_simple = pd.pivot_table(word_df, index=['nid', 'word'],
                                   aggfunc={'weighted_score': np.sum}).reset_index().rename_axis(None)
    special_df = word_df[(word_df.type != 'remaining')]
    # because it takes a lot of memory to compare every possible word for every note-note combination.
    # -I filter it to only notes that contain at least 1 'special word' in common
    # -special words are words that are within a cloze, bolded, italicized, or underlinzed
    mlfiles.print_log("Comparing special words to limit the number of note-note pairs")
    special_df1 = special_df[special_df['nid'].isin(nids_1)]
    special_df2 = special_df[special_df['nid'].isin(nids_2)]
    special_join = pd.merge(special_df1, special_df2, on='word', how='inner')
    special_join['combined_special'] = special_join['weighted_score_x'] + special_join['weighted_score_y']
    special = pd.pivot_table(special_join, index=['nid_x', 'nid_y'],
                             aggfunc={'combined_special': np.sum}).reset_index().rename_axis(None)
    special = special.sort_values("combined_special", axis=0, ascending=False)
    cutoff = word_rare_score(0.01, mlfiles.load_setting("Scoring", "rare_leveling")) * (
            mlfiles.load_setting('Scoring', 'cloze_multiplier') + mlfiles.load_setting('Scoring',
                                                                                       'emphasis_multiplier')) / 2
    special = special[
        special['combined_special'] > cutoff]  # if the only special word in common is a word like 'The', skip
    nids1 = list(special['nid_x'])
    nids2 = list(special['nid_y'])
    special = None
    del special
    word_df = None
    del word_df
    bin_number = round(len(nids1) / mlfiles.load_setting('Misc', 'bin_size') + 1)
    # I split the next step into bins to avoid maxing out ram
    nids1_split = np.array_split(nids1, bin_number)
    nids2_split = np.array_split(nids2, bin_number)
    nidnid = [nids1[i] + nids2[i] for i in range(len(nids1))]
    non_dupes_dict = mlfiles.load_dict(mlfiles.load_setting('Misc', 'non_dupes_dict'))
    completed_pairs = [int(k) for k in non_dupes_dict.keys()]
    df_list = []
    mlfiles.print_log('Prioritizing ' + str(len(nids1) / 1000) + "K of " + str(
        (len(nids_1) * len(nids_2)) / 1000) + "K possible note-note comparisons based on 'important word' matches")
    mlfiles.print_log("Now finding every word match between the prioritized note-note pairs")
    min_score = mlfiles.load_setting('Misc', 'absolute_min_score')
    for i in tqdm(range(len(
            nids1_split))):  # in this loop, I find all the matching word between each note pair and add the score
        # for each word
        nid1_bin = nids1_split[i]
        nid2_bin = nids2_split[i]
        worddf_simple1 = worddf_simple[worddf_simple['nid'].isin(nid1_bin)]
        worddf_simple2 = worddf_simple[worddf_simple['nid'].isin(nid2_bin)]
        binjoin = pd.merge(worddf_simple1, worddf_simple2, on='word', how='inner')
        binjoin['nidnid'] = binjoin['nid_x'] + binjoin["nid_y"]
        binjoin = binjoin[~binjoin['nidnid'].isin(completed_pairs)]
        binjoin = binjoin[binjoin['nidnid'].isin(nidnid)]
        binout = pd.pivot_table(binjoin, index=['nid_x', 'nid_y', 'nidnid'], aggfunc={'weighted_score_x': np.sum,
                                                                                      'weighted_score_y': np.sum}).reset_index().rename_axis(
            None)
        if len(binout.index) > 0:
            completed_pairs.extend(list(binout['nidnid']))
            binout['combined_weighted'] = binout['weighted_score_x'] + binout['weighted_score_y']
            binout = binout[binout['combined_weighted'] > min_score]
            df_list.append(binout)
    completed_pairs = None
    del completed_pairs
    mlfiles.update_log('Calculating scores')
    binout_comb = pd.concat(df_list, ignore_index=True)
    binout_comb = binout_comb[binout_comb['nid_x'] != binout_comb['nid_y']]
    binout_comb['combined_weighted'] = binout_comb['weighted_score_x'] + binout_comb['weighted_score_y']
    binout_comb = binout_comb.drop_duplicates(subset=['nidnid', 'combined_weighted'], keep='first')
    note_maxes = pd.pivot_table(worddf_simple, index=['nid'],
                                aggfunc={'weighted_score': np.sum}).reset_index().rename_axis(None)
    note_maxes_x = note_maxes.rename(columns={'nid': 'nid_x', "weighted_score": "note_max_x"})
    final_scores = pd.merge(binout_comb, note_maxes_x, on='nid_x', how='left')
    binout_comb = None
    del binout_comb
    note_maxes_x = None
    del note_maxes_x
    note_maxes_y = note_maxes.rename(columns={'nid': 'nid_y', "weighted_score": "note_max_y"})
    final_scores = final_scores = pd.merge(final_scores, note_maxes_y, on='nid_y', how='left')
    note_maxes_y = None
    del note_maxes_y
    note_maxes = None
    del note_maxes
    final_scores['max_score'] = final_scores['note_max_x'] + final_scores['note_max_y']
    # Finally, I calculate a score for each note pair that adds all the word-match scores and divides by the highest
    # possible score for that note-note pair
    final_scores['score'] = final_scores['combined_weighted'] / final_scores['max_score'] * 100
    final_scores['score_x'] = final_scores['weighted_score_x'] / final_scores['note_max_x']  # calculate forward score
    final_scores['score_y'] = final_scores['weighted_score_y'] / final_scores['note_max_y']  # calculate reverse score
    final_scores = final_scores.sort_values("score", axis=0, ascending=False)
    cutoff_final = final_scores[final_scores['score'] > mlfiles.load_setting('Scoring', "score_cutoff")]
    cutoff_final = cutoff_final.drop_duplicates(subset='nidnid', keep='first')
    mlfiles.update_log("found " + str(len(cutoff_final.index)) + " note pairs that meet the score cutoff")
    top_n = final_scores.head(n=mlfiles.load_setting('Scoring', "keep_top"))
    final_scores = final_scores.sort_values("combined_weighted", axis=0, ascending=False)
    top_m = final_scores.head(n=mlfiles.load_setting('Scoring', "keep_top_absolute"))
    final_scores = final_scores.sort_values("score_x", axis=0, ascending=False)
    top_x = final_scores.head(n=mlfiles.load_setting('Scoring', 'keep_top_one_direction'))
    final_scores = final_scores.sort_values("score_y", axis=0, ascending=False)
    top_y = final_scores.head(n=mlfiles.load_setting('Scoring', 'keep_top_one_direction'))
    output_scores = cutoff_final.append(top_n)
    output_scores = output_scores.append(top_m)
    output_scores = output_scores.append(top_x)
    output_scores = output_scores.append(top_y)
    output_scores = output_scores.drop_duplicates()
    final_scores = None
    del final_scores
    output_scores.drop_duplicates(subset='nidnid', keep='first', inplace=True)
    return output_scores


def tag_duplicates(anki, output_scores):
    mlfiles.update_log('Tagging ' + str(len(output_scores)) + ' note pairs')
    notes_1 = list(output_scores['nid_x'])
    notes_2 = list(output_scores['nid_y'])
    i = 0
    now = datetime.datetime.now()
    date_string = now.strftime('%Y-%m-%d_%H:%M')
    for i in range(len(notes_1)):
        tag = "~DupCatch_V2::D" + date_string + "::" + str(i).zfill(4)
        pair = [notes_1[i], notes_2[i]]
        for nid in pair:
            mlfiles.print_log("Tagging Note " + nid + " with the tag " + tag)
            note = anki.get_note(int(nid))
            note.add_tag(tag)
            anki.update_note(note)


def run_duplicate_finder():
    anki_file = initialize_database()
    collection_file = 'bin/collection/collection.anki2'

    try:
        mltext.download_wordnet()
    except Exception as e:
        mlfiles.log_exception(e)
    anki = AnkiDesktop(filename=collection_file)
    mlfiles.update_log('Anki file loaded at ' + anki.filename)
    notes = anki.db.Notes
    mlfiles.update_log("Loaded " + str(len(list(notes.select()))) + ' notes')
    fields = anki.db.Fields
    check_duplicates_tag = mlfiles.load_setting("Duplicates", "check_duplicates_tag")
    compare_to_tag = mlfiles.load_setting("Duplicates", "compare_to_tag")
    tags_to_skip = mlfiles.load_setting("Duplicates", "tags_to_skip")
    mlfiles.update_log(
        'Only notes with ' + check_duplicates_tag + ' tag will be compared to notes with the tag ' + compare_to_tag)
    mlfiles.update_log('Excluding notes that are tagged with ' + "; ".join(list(tags_to_skip)))
    notes_to_skip = anki_functions.tagged_notes(notes, tags_to_skip)
    notes_1 = notes.select().where(notes.tags.contains(check_duplicates_tag) & notes.id.not_in(notes_to_skip))
    notes_2 = notes.select().where(notes.tags.contains(compare_to_tag) & notes.id.not_in(notes_to_skip))
    notes_using = notes_1 | notes_2
    mlfiles.update_log(str(len(notes_1)) + ' notes will be compared to ' + str(len(notes_2)) + ' notes.')
    # clean_words = build_clean_dict(notes_using, fields)
    mlfiles.update_log("Building a word dataframe for the selected notes")
    word_df = build_word_df(notes_using, fields)
    nids_1 = [n.id for n in notes_1]
    nids_2 = [n.id for n in notes_2]
    output_scores = score_matches(word_df, nids_1, nids_2)
    output_scores.drop_duplicates(inplace=True)
    word_df = None
    del word_df
    anki.close()
    col = Collection(collection_file)
    tag_duplicates(col, output_scores)
    l1 = list(output_scores['nid_x'])
    l2 = list(output_scores['nid_y'])
    p = min(15, len(l1))
    # print('Here are the top ' + str(p) + ' results')
    ids_to_keep = l1
    ids_to_keep.extend(l2)
    # for k in range(p):
    #     n1 = l1[k]
    #     n2 = l2[k]
    #     mlfiles.print_log('note1:')
    #     mlfiles.print_log(clean_words.get(n1))
    #     mlfiles.print_log('note2:')
    #     mlfiles.print_log(clean_words.get(n2))
    #     mlfiles.print_log('---------------------------------------------')
    col.close()
    delete_unchanged_records(collection_file, ids_to_keep)
    new_file_path = re.sub("[.]", "_notes_merged.", anki_file)
    file_path = 'bin/collection/output.apkg'
    export_apkg_file(collection_file, file_path, new_file_path)
    mlfiles.update_log('DUPLICATES RUN COMPLETE - Exported results to ' + new_file_path)
    mlfiles.update_log('-------------------------------------------------------------')
    mlfiles.clear_folder("bin/collection")


def export_apkg_file(anki2_file, file_path, new_file_path):
    col = Collection(anki2_file)
    col.export_anki_package(out_path=file_path, limit=90000, with_scheduling=False, with_media=False,
                            legacy_support=True)
    mlfiles.copy_file(file_path, new_file_path)
    col.close()


def help(sys_arg):
    if len(sys_arg) == 1 or '-h' in sys_arg or '--help' in sys_arg:
        mlfiles.update_log(
            "No option selected: type -r for 'Run duplicates', -m for 'merge'. Modify the settings in settings.yml")


def run_merge():
    anki_file = initialize_database()
    collection_file = 'bin/collection/collection.anki2'
    merge_tags = mlfiles.load_setting('Merge', 'merge_tags')
    merge_fields = mlfiles.load_setting('Merge', 'merge_fields')
    merge_suffix = mlfiles.load_setting('Merge', 'merge_suffix')
    merge_fields_suffix = mlfiles.load_setting('Merge', 'merge_fields_suffix')
    merge_tags_suffix = mlfiles.load_setting('Merge', 'merge_tags_suffix')
    non_dupes_tag_suffix = mlfiles.load_setting('Remember', 'non_dupes_tag_suffix')
    if merge_tags:
        mlfiles.update_log(
            "Based on the settings, I will attempt to marge tags for any pairs that contain (tag) '" + merge_suffix + "' or '" + merge_tags_suffix + "'")
    if merge_fields:
        mlfiles.update_log(
            "based on the settings, I will attempt to merge fields for any pairs that contain (tag) '" + merge_suffix + "' or '" + merge_fields_suffix + "'")
    if merge_fields is False and merge_tags is False:
        mlfiles.update_log(
            "The settings prevent tag and field merging, I will still check for any tags that contain " + non_dupes_tag_suffix)
    folder_name = mlfiles.load_setting("Misc", "folder")
    anki = AnkiDesktop(filename=collection_file)
    mlfiles.update_log('Anki file loaded at ' + anki.filename)
    notes = anki.db.Notes
    mlfiles.update_log("Loaded " + str(len(list(notes.select()))) + ' notes')
    mlfiles.update_log("Building Tags DataFrame")
    tag_df = build_tag_df(notes)
    merge_notes = filter_df_pattern(tag_df, 'tag', merge_suffix)
    tag_notes = filter_df_pattern(tag_df, 'tag', merge_tags_suffix)
    field_notes = filter_df_pattern(tag_df, 'tag', merge_fields_suffix)
    save_non_dupes(tag_df, non_dupes_tag_suffix)
    anki.close()
    col = Collection(collection_file)
    now = datetime.datetime.now()
    date_string = now.strftime('%Y-%m-%d_%H:%M')
    ids_to_keep = []
    if merge_fields:
        merge_fields_df = pd.concat([merge_notes, field_notes], axis=0)
        merge_field_nids = list(merge_fields_df['nid'])
        merge_field_tags = list(merge_fields_df['tag'])
        field_separator = mlfiles.load_setting('Merge', 'field_seperator')
        map_missing_field = mlfiles.load_setting('Merge', 'map_missing_field')
        fields_to_ignore = mlfiles.load_setting('Merge', 'fields_to_ignore')
        mlfiles.update_log("Ignoring fields " + " ".join(fields_to_ignore))
        mlfiles.update_log("Merging the fields of " + str(len(merge_field_nids)) + " note pairs")
        for i in range(len(merge_field_nids)):
            tag_to_add = "~DupCatch_V2::M" + date_string + "::fields_merged::" + str(i).zfill(3)
            nid1 = merge_field_nids[i]
            tag = merge_field_tags[i]
            tag_to_find = re.sub(merge_suffix, '', tag)
            tag_to_find = re.sub(merge_fields_suffix, '', tag_to_find)
            note_pair_df = filter_df_pattern(tag_df, 'tag', tag_to_find)
            nids = list(note_pair_df['nid'])
            nids.remove(nid1)
            nid2 = nids[0]
            note1 = col.get_note(nid1)
            note2 = col.get_note(nid2)
            anki_functions.map_note_fields(note1, note2, map_missing_field, fields_to_ignore, field_separator)
            note1.add_tag(tag_to_add + '::keep')
            note2.add_tag(tag_to_add)
            col.update_note(note1)
            col.update_note(note2)
            ids_to_keep.extend([nid1, nid2])
    if merge_tags:
        merge_tags_df = pd.concat([merge_notes, tag_notes], axis=0)
        merge_tag_nids = list(merge_tags_df['nid'])
        merge_tag_tags = list(merge_tags_df['tag'])
        tags_to_ignore = mlfiles.load_setting('Merge', 'tags_to_ignore')
        i = 0
        mlfiles.update_log("Merging the tags of " + str(len(merge_tag_nids)) + " note pairs")
        mlfiles.update_log("Ignoring tags " + "; ".join(tags_to_ignore))
        for i in range(len(merge_tag_nids)):
            tag_to_add = "~DupCatch_V2::M" + date_string + "::tags_merged::" + str(i).zfill(3)
            nid1 = merge_tag_nids[i]
            tag = merge_tag_tags[i]
            tag_to_find = re.sub(merge_suffix, '', tag)
            tag_to_find = re.sub(merge_tags_suffix, '', tag_to_find)
            note_pair_df = filter_df_pattern(tag_df, 'tag', tag_to_find)
            nids = list(note_pair_df['nid'])
            nids.remove(nid1)
            nid2 = nids[0]
            note1 = col.get_note(nid1)
            note2 = col.get_note(nid2)
            anki_functions.combine_tags(note1, note2, tags_to_ignore)
            note1.add_tag(tag_to_add + '::keep')
            note2.add_tag(tag_to_add)
            col.update_note(note1)
            col.update_note(note2)
            ids_to_keep.extend([nid1, nid2])
    covered_by_suffix = mlfiles.load_setting("Merge", "covered_by_suffix")
    covered_by_tag = mlfiles.load_setting("Merge", "covered_by_tag")
    covered_by_df = filter_df_pattern(tag_df, 'tag', covered_by_suffix)
    covered_nids = list(covered_by_df['nid'])
    covered_tags = list(covered_by_df['tag'])
    i = 0
    mlfiles.update_log("Tagging " + str(len(covered_nids)) + ' note-pairs with a <' + covered_by_tag + '> tag')
    for i in range(len(covered_nids)):
        nid1 = covered_nids[i]
        tag = covered_tags[i]
        tag_to_find = re.sub(covered_by_suffix, '', tag)
        note_pair_df = filter_df_pattern(tag_df, 'tag', tag_to_find)
        nids = list(note_pair_df['nid'])
        nids.remove(nid1)
        nid2 = nids[0]
        note1 = col.get_note(nid1)
        note2 = col.get_note(nid2)
        anki_functions.tag_covered_by(note1, note2, col, covered_by_tag)
        col.update_note(note1)
        col.update_note(note2)
        ids_to_keep.extend([nid1, nid2])
    col.close()
    delete_unchanged_records(collection_file, ids_to_keep)
    new_file_path = re.sub("[.]", "_notes_merged.", anki_file)
    file_path = 'bin/collection/output.apkg'
    export_apkg_file(collection_file, file_path, new_file_path)
    mlfiles.update_log('MERGE RUN COMPLETE - Exported results to ' + new_file_path)
    mlfiles.update_log('-------------------------------------------------------------')
    mlfiles.clear_folder("bin/collection")


def save_non_dupes(tag_df, non_dupes_tag_suffix):
    non_dupes = filter_df_pattern(tag_df, 'tag', non_dupes_tag_suffix)
    nd_tags = non_dupes['tag']
    non_dupes_dict = mlfiles.load_dict(mlfiles.load_setting('Misc', 'non_dupes_dict'))
    non_dupes_list = [int(k) for k in non_dupes_dict.keys()]
    for tag in nd_tags:
        tag_to_find = re.sub(non_dupes_tag_suffix, '', tag)
        non_dupe_pair = filter_df_pattern(tag_df, 'tag', tag_to_find)
        non_dupe_nids = list(non_dupe_pair['nid'])
        nidnid = non_dupe_nids[0] + non_dupe_nids[1]
        if nidnid not in non_dupes_list:
            non_dupes_dict.update({nidnid: non_dupe_nids[0]})
    mlfiles.write_dict(mlfiles.load_setting('Misc', "non_dupes_dict"), non_dupes_dict)


def build_tag_df(notes):
    tags_dflist = []
    for note in tqdm(notes.select()):
        tags = note.tags
        df = pd.DataFrame({'nid': [note.id for i in range(len(tags))], 'tag': tags})
        tags_dflist.append(df)
    outdf = pd.concat(tags_dflist, ignore_index=True)
    return outdf


def filter_df_pattern(df, column: str, pattern: str):
    df['test'] = df[column].str.contains(pattern)
    newdf = df[df['test'] == True]
    newdf.pop('test')
    return newdf


def delete_unchanged_records(anki2_file, id_list_to_keep):
    anki = AnkiDesktop(filename=anki2_file)
    notes = anki.db.Notes
    query = notes.delete().where(notes.id.not_in(id_list_to_keep))
    query.execute()
    anki.close()
