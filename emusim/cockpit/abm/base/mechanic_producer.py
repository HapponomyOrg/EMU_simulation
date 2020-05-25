from emusim.cockpit.abm.base.producer import Producer


class MechanicProducer(Producer):

    # label: a label for the producer. Can serve as an identifier of sorts.
    # producer_lifetime: the amount of cycles the producer lasts. Maintenance can reset this. Can not be set to Product.NO_EXPIRY.
    # maintenance_interval: the interval the producer can function without needing maintenance. Going longer without maintenance results in damage.
    # health_profile: determines how much damage the producer can sustain and how damage impacts its capacities.
    def __init__(self, label, producer_lifetime, maintenance_interval, health_profile):
        super().__init__(label, producer_lifetime, health_profile)

    def do_maintenance(self):
        return # implement

    def repair(self):
        return # implement
