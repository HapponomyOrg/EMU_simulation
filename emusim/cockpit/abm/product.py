from uuid import uuid4

class Product:
    NO_EXPIRY = -1

    # type_id: the unique id for the collection of instances of a specific type of product.
    # id: the unique id of the product.
    # label: a label for the product. For display and type identification purposes.
    # type: the type of the Product. See ProductType.
    # product_expiration: # the amount of cycles the product lasts. Can be set to NO_EXPIRY
    def __init__(self, label, type, product_expiration):
        self.type_id = str(type) + "-" + str(label)
        self.id = uuid4()
        self.label = label
        self.type = type
        self.product_expiration = product_expiration

    def get_label(self):
        return self.label

    def get_type(self):
        return self.type

    def get_expiration(self):
        return self.product_expiration

    # Age the product. This is called each cycle and subtracts 1 from
    def age(self):
        if self.product_expiration != self.NO_EXPIRY and self.product_expiration > 0:
            self.product_expiration -= 1

    def is_expired(self):
        return self.product_expiration == 0



