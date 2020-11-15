def move_zeros(array):
    zeros = [i for i in array if i == 0 and not isinstance(i, bool)]
    print(zeros)
    non_zeros = [i for i in array if i != 0 or isinstance(i, bool)]
    print(non_zeros)
    non_zeros.extend(zeros)
    return non_zeros


print(move_zeros(["a", 0, 0, "b", None, "c", "d", 0, 1,
                  False, 0, 1, 0, 3, [], 0, 1, 9, 0, 0, {}, 0, 0, 9]))
