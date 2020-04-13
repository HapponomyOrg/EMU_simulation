

class Product:
    NO_EXPIRY = -1

    def __init__(self, label, type, product_expiration):
        self.label = label # a label for the product. Can serve as an identifier of sorts
        self.type = type # the type of product, see ProductType
        self.product_expiration = product_expiration

    def get_label(self):
        return self.label

    def get_type(self):
        return self.type

    def get_expiration(self):
        return self.product_expiration

    def age(self):
        if self.product_expiration != self.NO_EXPIRY and self.product_expiration > 0:
            self.product_expiration -= 1

    def is_expired(self):
        return self.product_expiration == self.NO_EXPIRY or self.product_expiration > 0



