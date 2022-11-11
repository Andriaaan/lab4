from models import *

def create_entry(model_class, *, commit=True, **kwargs):
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    return entry


def get_entry_byid(model_class, uid, **kwargs):
    return session.query(model_class).filter_by(id=uid, **kwargs).one()


def update_entry(entry, *, commit=True, **kwargs):
    for key, value in kwargs.items():
        setattr(entry, key, value)
    if commit:
        session.commit()
    else:
        return entry


def delete_entry(model_class, uid, *, commit=True, **kwargs):
    session.query(model_class).filter_by(uid=uid, **kwargs).delete()
    if commit:
        session.commit()