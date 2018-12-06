from django.core.cache import cache
from django.db.models import get_models, get_app
from django.db.models.signals import post_save
from django.dispatch import receiver

from singleton_models.models import SingletonModel


class CachedCopyHelper():
    """
    A shortcut for easily accessing SingletonModels, used primarily in
    `context_processors`.
    """
    def __init__(self):
        self._models = []
        self._model_map = {}

    def register(self, Model, name=None):
        """
        Register a model with this CachedCopyHelper. This CachedCopyHelper will
        then provide easy access to the model via `cached_copy[model_name]`.
        """
        if name is None:
            name = Model._meta.module_name

        self._models.append(Model)
        self._model_map[name] = Model

        if issubclass(Model, SingletonModel):
            post_save.connect(self.clear_on_save, sender=Model)

    def get(self, name):
        Model = self._get_model(name)
        if issubclass(Model, SingletonModel):
            return self._get_singleton(Model)
        else:
            return self._get_list(Model)

    def _get_list(self, Model):
        return Model.objects.all()

    def _get_singleton(self, Model):
        cache_key = self._get_key(Model)
        copy = cache.get(cache_key)

        if copy is None:
            try:
                copy = Model.objects.get(pk=1)
            except Model.DoesNotExist:
                msg = "Singleton '%s' has not been created" % Model
                raise Model.DoesNotExist(msg)

            # Cache for a day. It will not change all that often, and we listen
            # for model save events to invalidate the cache
            cache.set(cache_key, copy, 24 * 60 * 60 * 60)

        return copy

    def _get_model(self, name):
        return self._model_map[name]

    def _get_key(self, Model):
        return 'Singleton:%d:%s' % (id(self), Model._meta.module_name)

    def __getitem__(self, name):
        return self.get(name)

    def clear_on_save(self, sender, *args, **kwargs):
        """
        Clear the cache for a particular model when it is saved
        """
        self.clear(sender)

    def clear(self, Model):
        """
        Clear the cache for a model
        """
        if isinstance(Model, basestring):
            name = Model
            Model = self._get_model(name)

        cache_key = self._get_key(Model)
        cache.delete(cache_key)

    def clear_all(self):
        """
        Clear the whole cache for this CachedCopy
        """
        for Model in self._models:
            self.clear(Model)


cached_copy = CachedCopyHelper()
