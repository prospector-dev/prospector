from prospector.adaptor.base import AdaptorBase
from prospector.adaptor.common import CommonAdaptor
from prospector.adaptor.libraries import CeleryAdaptor, DjangoAdaptor
from prospector.adaptor.no_doc_warnings import NoDocWarningsAdaptor
from prospector.adaptor.strictness import NoOpAdaptor


LIBRARY_ADAPTORS = {
    DjangoAdaptor.name: DjangoAdaptor,
    CeleryAdaptor.name: CeleryAdaptor,
}

STRICTNESS_ADAPTORS = {
    'veryhigh': NoOpAdaptor,
    'high': NoOpAdaptor,
    'medium': NoOpAdaptor,
    'low': NoOpAdaptor,
    'verylow': NoOpAdaptor
}
