from prospector.adaptor.libraries import CeleryAdaptor, DjangoAdaptor


LIBRARY_ADAPTORS = {
    DjangoAdaptor.name: DjangoAdaptor,
    CeleryAdaptor.name: CeleryAdaptor,
}
