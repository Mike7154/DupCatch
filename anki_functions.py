import re


def get_field_names(fields, note):
    fields = fields.select().where(fields.ntid == note.model.id).order_by(fields.ord)
    return [f.name for f in fields]


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

def get_field(fields_model, note, field_name):
    index = get_field_names(fields_model,note).index(field_name)
    return note.flds[index]

def get_fields(fields_model, note, fields):
    return [get_field(fields_model, note, f) for f in fields]

def combine_fields(fields_model, note, fields, sep = " "):
    fields = get_fields(fields_model, note, fields)
    return sep.join(fields)

def compile_cloze(pattern = '\{\{c[0-9]+::(.*?)[\}:]{2}'):
    return re.compile(pattern)

def clean_clozes_patterns():
    patterns = ['\{\{c[0-9]+::',':{2}(.*?)\}{2}','[\{\}]']
    p_out = []
    for p in patterns:
        p_out.append(re.compile(p))
    return p_out
