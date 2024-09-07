class DefaultDBRouter:
    route_app_labels = {'auth', 'contenttypes', 'sessions', 'admin'}

    READONLY_DATABASE = 'default'
    WRITE_DATABASE = 'ams'

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self.WRITE_DATABASE

        return self.READONLY_DATABASE

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self.WRITE_DATABASE

        return self.READONLY_DATABASE

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == self.READONLY_DATABASE:
            return False

        if app_label in self.route_app_labels:
            return db == self.WRITE_DATABASE

        return None
