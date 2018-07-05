import models

models.database.connect()
models.database.create_tables([models.TelegramUsers, ])
