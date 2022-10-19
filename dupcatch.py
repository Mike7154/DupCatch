import mlfiles
import dupcatch_subs
import anki_functions
from tqdm import tqdm
from fuzzywuzzy import fuzz
from ankisync2 import AnkiDesktop
import mltext
mltext.download_wordnet()

from importlib import reload
reload(dupcatch_subs)
reload(anki_functions)
reload(mltext)
reload(mlfiles)
# reload(mlfiles)
# reload(plex_functions)
# reload(mlfiles)
#reload(mlscraping)
#reload(general_functions)

folder_name = mlfiles.load_setting("Misc","folder")
extension = mlfiles.load_setting("Misc","extension")
folder = mlfiles.get_current_dir(folder_name)
file = mlfiles.find_file(folder, extension)
anki =  AnkiDesktop(filename = file)
mlfiles.update_log('Anki file loaded at ' + anki.filename)
notes = anki.db.Notes
mlfiles.update_log("Loaded " + str(len(list(notes.select()))) + ' notes')
fields = anki.db.Fields
check_duplicates_tag = mlfiles.load_setting("Duplicates","check_duplicates_tag")
compare_to_tag = mlfiles.load_setting("Duplicates","compare_to_tag")
tags_to_skip = mlfiles.load_setting("Duplicates", "tags_to_skip")
mlfiles.update_log('Only notes with ' + check_duplicates_tag + ' tag will be compared to notes with the tag ' + compare_to_tag)
mlfiles.update_log('Excluding tags that contain ' + "; ".join(list(tags_to_skip)))
notes_to_skip = anki_functions.tagged_notes(notes, tags_to_skip)
notes_1 = notes.select().where(notes.tags.contains(check_duplicates_tag) & notes.id.not_in(notes_to_skip))
notes_2 = notes.select().where(notes.tags.contains(compare_to_tag) & notes.id.not_in(notes_to_skip))
notes_using = notes_1 | notes_2
mlfiles.update_log(str(len(notes_1)) + ' notes will be compared to ' + str(len(notes_2)) + ' notes.')
clean_words = dupcatch_subs.build_clean_dict(notes_using, fields)
mlfiles.update_log("Attempting to build a word dataframe for all of the selected notes")
word_df = dupcatch_subs.build_word_df(notes_using, fields)
nids_1 = [n.id for n in notes_1]
nids_2 = [n.id for n in notes_2]
output_scores = dupcatch_subs.score_matches(word_df, nids_1, nids_2)
output_scores.drop_duplicates(inplace = True)
word_df = None; del word_df

mlfiles.update_log('Tagging ' + str(len(output_scores)) + ' note pairs')
notes_1 = list(output_scores['nid_x'])
notes_2 = list(output_scores['nid_y'])
i = 0
import datetime

now = datetime.datetime.now()
date_string = now.strftime('%Y-%m-%d_%H:%M')
for i in range(len(notes_1)):
    tag = "~DupCatch_V2::" + date_string + "::" + str(i).zfill(4)
    pair = [notes_1[i], notes_2[i]]
    sub_notes = notes.select().where(notes.id << pair)
    for n in sub_notes:
        mlfiles.print_log("tagging note " + str(n.id) + ' with ' + tag)
        new_tags = n.tags
        new_tags.append(tag)
        query = notes.update(tags=new_tags).where(notes.id == n.id)
        query.execute()
l1 = list(output_scores['nid_x'])
l2 = list(output_scores['nid_y'])
p = min(15, len(l1))
print('Here are the top ' + str(p) + ' results')
for k in range(p):
    n1 = l1[k]
    n2 = l2[k]
    mlfiles.print_log('note1:')
    mlfiles.print_log(clean_words.get(n1))
    mlfiles.print_log('note2:')
    mlfiles.print_log(clean_words.get(n2))
    mlfiles.print_log('---------------------------------------------')
mlfiles.update_log('Completed duplicates check: file is located at ' + anki.filename)
anki.close()
