def natural_numbers_reverse(n,a=10):
    if a<n:
        return
    print(a)
    natural_numbers_reverse(n,a-1)
natural_numbers_reverse(1)

def another_method(i):
    if i<1:
        return
    print(i)
    another_method(i-1)
another_method(10)

def another_method_one(j):
    if j<0:
        return
    another_method_one(j-1)
    print(j)
another_method_one(5)


