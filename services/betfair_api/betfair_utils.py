class BetfairApiUtils:
    @staticmethod
    def divisor(entrance_list: list, partition: int) -> tuple[int, int]:
        list_lenght = len(entrance_list)

        N = int(list_lenght / partition)
        N2 = list_lenght - N * partition

        return N, N2
