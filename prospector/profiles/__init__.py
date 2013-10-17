from prospector.profiles.celery import CeleryProfile
from prospector.profiles.common import CommonProfile
from prospector.profiles.django import DjangoProfile
from prospector.profiles.no_doc_warnings import NoDocWarningsProfile


PROFILES = {
    'no_doc_warnings': NoDocWarningsProfile,
    'common': CommonProfile,
    # frameworks:
    'celery': CeleryProfile,
    'django': DjangoProfile,
}
