import config.database


def model_to_dict(model: config.database.Model):
    return {k: v for k, v in model.__dict__.items() if not k.startswith("_")}
