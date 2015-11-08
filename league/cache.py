from django.core.cache.backends.db import DatabaseCache
from django.db import connections, router, transaction

class LeagueCache(DatabaseCache):
    
    def delete_where(self, where=None):
        db = router.db_for_write(self.cache_model_class)
        table = connections[db].ops.quote_name(self._table)
        cursor = connections[db].cursor()

        try:
            cursor.execute("DELETE FROM %s WHERE %s" % (table, where))
            transaction.commit_unless_managed(using=db)
        except:
            pass

# For backwards compatibility
class CacheClass(DatabaseCache):
    pass
