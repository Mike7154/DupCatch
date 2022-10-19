import mlfiles
import re
from ankisync2 import AnkiDesktop
import numpy as np
from tqdm import tqdm
import pandas as pd
import mltext
import mlfiles
import anki_functions





def word_rare_score(freq, leveling = 10):
    return abs(np.log(1/(freq*leveling)))

#for k in [1,2,3,4,5,6,7,8,9,25,100]:
#    for i in [.04, .01, .001, .0001, 2.705378834198153e-06]:
#        print(word_rare_score(i,k))


def build_word_df(notes_using, fields): #this returns a dataframe of all the words in selected notes with frequencies, and weights (cloze, bolded, italics, etc)
    fields_to_check = mlfiles.load_setting("Duplicates","fields_to_check")
    HTML_CLEANR = mltext.compile_html_cleaner()
    HTML_TAG_CLEANR = mltext.compile_html_cleaner(False)
    CLOZE_CLEANR = anki_functions.compile_cloze()
    CLOZE_CLEANR1 = anki_functions.compile_cloze('\{\{c[0-9]+::(.*?[^ .,;]\}{2}[a-zA-Z-]+)')
    CLOZE_CLEANR2 = anki_functions.compile_cloze('\{\{c[0-9]+::(.*?)[/}]{2}')
    CLOZE_CLEANR3 = anki_functions.clean_clozes_patterns()
    TAG_CLEANR = mltext.compile_html_tag(mlfiles.load_setting('Scoring','emphasis_pattern'))
    cloze_compile = anki_functions.compile_cloze()
    emphasis_multiplier = mlfiles.load_setting("Scoring","emphasis_multiplier")
    cloze_multiplier = mlfiles.load_setting("Scoring","cloze_multiplier")
    synonym_dict = mltext.reverse_synonym_dict(mlfiles.load_all_settings()['Misc']['synonyms'], mltext.unicode_dict())
    pattern_1 = re.compile(r'[(.,!*#\?)]')
    pattern_3 = re.compile('[^A-Za-z0-9]+')
    pattern_4 = re.compile('(?<=[A-Za-z])/(?=[A-Za-z])')
    mlfiles.print_log("Building Word Dataframe")
    list_of_dfs = []
    #For this, i take every word in the note and assign a rare score based on the frequency of that word.
    #The rarity scores are multiplied by 'importance weights'
    #Important words are words that are in a cloze, bolded, italicized or underlined
    for note in tqdm(notes_using):
        note_string = anki_functions.combine_fields(fields, note, fields_to_check)
        word_string = re.sub(pattern_4, " ",note_string)
        word_string = mltext.replace_patterns(word_string, synonym_dict)
        word_string = re.sub(pattern_1," ", word_string)
        clozes = mltext.find_text(word_string, CLOZE_CLEANR1)
        clozes = mltext.clean_patterns_words(clozes, CLOZE_CLEANR3)
        word_string = mltext.clean_text(word_string, CLOZE_CLEANR1)
        clozes.extend(mltext.find_text(word_string, CLOZE_CLEANR))
        clozes = [mltext.clean_text(c, HTML_CLEANR, "") for c in clozes]
        remaining_words = mltext.clean_text(word_string, CLOZE_CLEANR2)
        emphasized_words = mltext.find_text(remaining_words, TAG_CLEANR)
        remaining_words = mltext.clean_text(remaining_words, TAG_CLEANR)
        remaining_words = mltext.clean_text(remaining_words, HTML_CLEANR)
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
        df1 = pd.DataFrame({'nid':[note.id for i in range(len(emphasized_words))], 'word':emphasized_words, 'multiplier':[emphasis_multiplier for i in range(len(emphasized_words))], 'type':["emphasis" for i in range(len(emphasized_words))]})
        df2 = pd.DataFrame({'nid':[note.id for i in range(len(clozed_words))], 'word':clozed_words, 'multiplier':[cloze_multiplier for i in range(len(clozed_words))], 'type':["cloze" for i in range(len(clozed_words))]})
        df3 = pd.DataFrame({'nid':[note.id for i in range(len(remaining_words))], 'word':remaining_words, 'multiplier':[1 for i in range(len(remaining_words))], 'type':['remaining' for i in range(len(remaining_words))]})
        list_of_dfs.extend([df1,df2,df3])
    mlfiles.print_log("Combining data frames")
    outdf = pd.concat(list_of_dfs, ignore_index = True)
    outdf['freq'] = outdf.groupby('word')['word'].transform('count') / len(outdf)
    min(outdf['freq'])
    max(outdf['freq'])
    outdf['rare_score'] = word_rare_score(outdf['freq'],mlfiles.load_setting("Scoring","rare_leveling"))
    outdf['weighted_score'] = outdf['rare_score'] * outdf['multiplier']
    return outdf

def build_clean_dict(notes_using, fields):
    mlfiles.print_log("Building sentences dictionary")
    fields_to_check = mlfiles.load_setting("Duplicates","fields_to_check")
    CLOZE_CLEANR3 = anki_functions.clean_clozes_patterns()
    HTML_CLEANR = mltext.compile_html_cleaner()
    spaces = re.compile( '[ ]+')
    dict = {}
    for note in tqdm(notes_using):
        note_string = anki_functions.combine_fields(fields, note, fields_to_check)
        clean_string = mltext.clean_patterns(note_string, CLOZE_CLEANR3)
        clean_string = mltext.clean_text(clean_string, HTML_CLEANR)
        clean_string = re.sub(spaces," ",clean_string)
        clean_string = clean_string.strip()
        dict.update({note.id: clean_string})
    return dict

def score_matches(word_df, nids_1, nids_2): #this scores the word pairs
    worddf_simple = pd.pivot_table(word_df, index = ['nid','word'], aggfunc = {'weighted_score':np.sum}).reset_index().rename_axis(None)
    special_df = word_df[(word_df.type != 'remaining')]
    #because it takes a lot of memory to compare every possible word for every note-note combination.
    # -I filter it to only notes that contain at least 1 'special word' in common
    # -special words are words that are within a cloze, bolded, italicized, or underlinzed
    mlfiles.print_log("Comparing special words to limit the number of note-note pairs")
    special_df1 = special_df[special_df['nid'].isin(nids_1)]
    special_df2 = special_df[special_df['nid'].isin(nids_2)]
    special_join = pd.merge(special_df1, special_df2, on = 'word', how = 'inner')
    special_join['combined_special'] = special_join['weighted_score_x'] + special_join['weighted_score_y']
    special = pd.pivot_table(special_join, index = ['nid_x','nid_y'], aggfunc = {'combined_special':np.sum}).reset_index().rename_axis(None)
    special = special.sort_values("combined_special", axis = 0, ascending = False)
    cutoff =  word_rare_score(0.01,mlfiles.load_setting("Scoring","rare_leveling")) * (mlfiles.load_setting('Scoring','cloze_multiplier')+mlfiles.load_setting('Scoring','emphasis_multiplier'))/2
    special = special[special['combined_special'] > cutoff] #if the only special word in common is a word like 'The', skip
    nids1 = list(special['nid_x'])
    nids2 = list(special['nid_y'])
    special = None; del special
    word_df = None; del word_df
    bin_size = round(len(nids1) / mlfiles.load_setting('Misc','bin_size') + 1)
    #I split the next step into bins to avoid maxing out ram
    nids1_split = np.array_split(nids1,bin_size)
    nids2_split = np.array_split(nids2,bin_size)
    nidnid = [nids1[i] + nids2[i] for i in range(len(nids1))]
    completed_pairs = []
    df_list = []
    mlfiles.print_log('Prioritizing ' + str(len(nids1) / 1000) + "K of " + str((len(nids_1) * len(nids_2))/ 1000) + "K possible note-note comparisons based on 'important word' matches")
    mlfiles.print_log("Now finding every word match between the prioritized note-note pairs")
    for i in tqdm(range(len(nids1_split))): #in this loop, I find all the matching word between each note pair and add the score for each word
        nid1_bin = nids1_split[i]
        nid2_bin = nids2_split[i]
        worddf_simple1 = worddf_simple[worddf_simple['nid'].isin(nid1_bin)]
        worddf_simple2 = worddf_simple[worddf_simple['nid'].isin(nid2_bin)]
        binjoin = pd.merge(worddf_simple1, worddf_simple2, on = 'word', how = 'inner')
        binjoin['nidnid'] = binjoin['nid_x'] + binjoin["nid_y"]
        binjoin = binjoin[~binjoin['nidnid'].isin(completed_pairs)]
        binjoin = binjoin[binjoin['nidnid'].isin(nidnid)]
        binjoin['combined_weighted'] = binjoin['weighted_score_x'] + binjoin['weighted_score_y']
        binout = pd.pivot_table(binjoin, index = ['nid_x','nid_y','nidnid'], aggfunc = {'combined_weighted':np.sum}).reset_index().rename_axis(None)
        completed_pairs.append(list(binout['nidnid']))
        df_list.append(binout)
    df_list[i]
    completed_pairs = None; del completed_pairs
    mlfiles.update_log('Calculating scores')
    binout_comb = pd.concat(df_list, ignore_index = True)
    binout_comb = binout_comb[binout_comb['nid_x'] != binout_comb['nid_y']]
    binout_comb = binout_comb.drop_duplicates(subset = ['nidnid','combined_weighted'], keep = 'first')
    note_maxes = pd.pivot_table(worddf_simple, index = ['nid'], aggfunc = {'weighted_score':np.sum}).reset_index().rename_axis(None)
    note_maxes_x = note_maxes.rename(columns = {'nid':'nid_x', "weighted_score":"note_max_x"})
    final_scores = pd.merge(binout_comb, note_maxes_x, on = 'nid_x', how = 'left')
    binout_comb = None; del binout_comb
    note_maxes_x = None; del note_maxes_x
    note_maxes_y = note_maxes.rename(columns = {'nid':'nid_y', "weighted_score":"note_max_y"})
    final_scores = final_scores = pd.merge(final_scores, note_maxes_y, on = 'nid_y', how = 'left')
    note_maxes_y = None; del note_maxes_y
    note_maxes = None; del note_maxes
    final_scores['max_score'] = final_scores['note_max_x'] +  final_scores['note_max_y']
    #Finally, I calculate a score for each note pair that adds all the word-match scores and divides by the highest possible score for that note-note pair
    final_scores['score'] = final_scores['combined_weighted'] / final_scores['max_score'] * 100
    final_scores = final_scores.sort_values("score", axis = 0, ascending = False)
    cutoff_final = final_scores[final_scores['score'] > mlfiles.load_setting('Scoring', "score_cutoff")]
    cutoff_final = cutoff_final.drop_duplicates(subset = 'nidnid', keep = 'first')
    mlfiles.update_log("found " + str(len(cutoff_final.index)) + " note pairs that meet the score cutoff")
    top_n = final_scores.head(n = mlfiles.load_setting('Scoring',"keep_top"))
    final_scores = final_scores.sort_values("combined_weighted", axis = 0, ascending = False)
    top_m = final_scores.head(n = mlfiles.load_setting('Scoring',"keep_top_absolute"))
    output_scores = cutoff_final.append(top_n)
    output_scores = output_scores.append(top_m)
    output_scores = output_scores.drop_duplicates()
    final_scores = None; del final_scores
    output_scores.drop_duplicates(subset = 'nidnid', keep = 'first', inplace = True)
    return output_scores
