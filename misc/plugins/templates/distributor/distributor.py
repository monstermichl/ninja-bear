from ninja_bear import DistributorBase, DistributeInfo


class Distributor(DistributorBase):
    """
    <name-upper> specific distributor. For more information about the distributor methods,
    refer to DistributorBase.
    """

    def distribute(self, info: DistributeInfo) -> DistributorBase:
        """
        Distributes the generated config. Here goes all the logic to distribute the generated
        config according to the plugin's functionality (e.g. commit to Git, copy to a different
        directory, ...).

        :param info: Contains the required information to distribute the generated config.
        :type info:  DistributeInfo
        """
        # TODO: Implement
        raise Exception('distribute method not implemented')
