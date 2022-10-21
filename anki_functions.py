import re
import mltext


def combine_tags(note1, note2, tags_to_ignore=[]):
    tags = note2.tags
    new_tags = []
    for t in tags:
        include = True
        for tti in tags_to_ignore:
            if tti.lower() in t.lower():
                include = False
        if include:
            new_tags.append(t)
    for nt in new_tags:
        note1.add_tag(nt)


def combine_field(receiver_note, giver_note, receiver_field, giver_field, field_seperator="<br>", remove_similar=True):
    pattern = '<img(.*?)>'
    giver_field_text = giver_note[giver_field]
    receiver_field_text = receiver_note[receiver_field]
    if remove_similar:
        giver_field_text = mltext.combine_remove_common(receiver_field_text, giver_field_text, pattern)
    if len(receiver_field_text) == 0:
        new_field = giver_field_text
    else:
        new_field = receiver_field_text + field_seperator + giver_field_text
    if len(giver_field_text) == 0 or giver_field_text in receiver_field_text:
        new_field = receiver_field_text
    receiver_note[receiver_field] = new_field


def map_note_fields(note1, note2, unmapped_default, ignore_fields=[], field_separator="<br>"):
    note_1_fields = []
    for (name, value) in note1.items():
        if name not in ignore_fields:
            note_1_fields.append(name)
    note_2_fields = []
    for (name, value) in note2.items():
        if name not in ignore_fields:
            note_2_fields.append(name)
    note_2_maps = []
    for field in note_2_fields:
        if field in note_1_fields:
            note_2_maps.append(field)
        else:
            note_2_maps.append(unmapped_default)
    for i in range(len(note_2_fields)):
        n2f = note_2_fields[i]
        n2m = note_2_maps[i]
        combine_field(note1, note2, n2m, n2f, field_separator)


def exclude_tags(notes_model, tags_to_exclude):
    notes = notes_model
    for t in tags_to_exclude:
        query = notes.delete().where(notes.tags.contains(t))
        query.execute()


def tagged_notes(notes_model, tag_list):
    notes = notes_model.select(notes_model.id).where(notes_model.tags.contains(tag_list[0]))
    for t in tag_list:
        query = notes_model.select(notes_model.id).where(notes_model.tags.contains(t))
        notes = notes | query
    return notes


def compile_cloze(pattern='[{]{2}c[0-9]+::(.*?)[}:]{2}'):
    return re.compile(pattern)


def combine_fields(fields_model, note, fields, sep=" "):
    fields = get_fields(fields_model, note, fields)
    return sep.join(fields)


def get_fields(fields_model, note, fields):
    return [get_field(fields_model, note, f) for f in fields]


def get_field(fields_model, note, field_name):
    return note.flds[get_field_index(fields_model, note, field_name)]


def get_field_index(fields_model, note, field_name):
    return get_field_names(fields_model, note).index(field_name)


def get_field_names(fields_model, note):
    fields = fields_model.select().where(fields_model.ntid == note.model.id).order_by(fields_model.ord)
    return [f.name for f in fields]


def clean_clozes_patterns():
    patterns = ['[{]{2}c[0-9]+::', ':{2}(.*?)[}]{2}', '[{}]']
    p_out = []
    for p in patterns:
        p_out.append(re.compile(p))
    return p_out


def get_note_deck(col, note):
    cid = note.card_ids()[0]
    card = col.get_card(cid)
    did = card.current_deck_id()
    return col.decks.get(did)


def build_deck_tag(deck_name, prefix=''):
    tag = prefix + re.sub(' ', '_', deck_name)
    return tag


def tag_covered_by(note1, note2, col, tag='(DECK)'):
    deck1 = get_note_deck(col, note1)['name']
    deck2 = get_note_deck(col, note2)['name']
    d1tag = build_deck_tag(deck1)
    d2tag = build_deck_tag(deck2)
    d1tag = re.sub("[(]DECK[)]", d1tag, tag)
    d2tag = re.sub("[(]DECK[)]", d2tag, tag)
    note1.add_tag(d2tag)
    note2.add_tag(d1tag)
