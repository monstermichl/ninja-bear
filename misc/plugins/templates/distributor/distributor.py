from ninja_bear import DistributorBase, DistributeInfo


class Distributor(DistributorBase):
    """
    <name-upper> specific distributor. For more information about the distributor methods,
    refer to DistributorBase.
    """

    def distribute(self, info: DistributeInfo) -> DistributorBase:

        """
        Method to distribute a generated config which must be implemented here.

        :param info: Contains the required information to distribute the generated config.
        :type info:  DistributeInfo
        """
        raise Exception('distribute method not implemented')
